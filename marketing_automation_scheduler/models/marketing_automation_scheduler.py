from odoo import models, fields, api, _
from datetime import datetime

class MarketingAutomationScheduler(models.Model):
    _name = 'marketing.automation.scheduler'
    _description = "Planificateur d'activités marketing"
    _order = 'scheduled_date desc'
    _rec_name = 'name'
    
    name = fields.Char(
        string='Nom',
        required=True
    )
    
    source_activity_id = fields.Many2one(
        'marketing.automation.activity',
        string='Activité source',
        required=True,
        ondelete='cascade'
    )
    
    campaign_id = fields.Many2one(
        'marketing.automation.campaign',
        string='Campagne',
        required=True
    )
    
    activity_type = fields.Selection([
        ('email', 'Email'),
        ('server_action', 'Server Action'),
    ], string="Type d'activité", required=True)
    
    server_action = fields.Many2one(
        'ir.actions.server',
        string='Action serveur'
    )
    
    scheduled_date = fields.Datetime(
        string='Date de planification',
        required=True
    )
    
    state = fields.Selection([
        ('scheduled', 'Planifié'),
        ('executed', 'Exécuté'),
        ('failed', 'Échoué'),
        ('cancelled', 'Annulé')
    ], string='État', default='scheduled')
    
    execution_date = fields.Datetime(
        string="Date d'exécution"
    )
    
    error_message = fields.Text(
        string="Message d'erreur"
    )
    
    # Compteur de participants traités
    participants_count = fields.Integer(
        string='Participants traités',
        default=0
    )
    
    def action_execute_now(self):
        """Exécuter immédiatement l'activité planifiée"""
        self.ensure_one()
        try:
            count = self._execute_activity()
            self.write({
                'state': 'executed',
                'execution_date': fields.Datetime.now(),
                'participants_count': count
            })
            
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Activité exécutée'),
                    'message': _('Activité exécutée avec succès pour %d participants.') % count,
                    'type': 'success',
                }
            }
        except Exception as e:
            self.write({
                'state': 'failed',
                'error_message': str(e),
                'execution_date': fields.Datetime.now()
            })
            
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Erreur'),
                    'message': _("Erreur lors de l'exécution: %s") % str(e),
                    'type': 'danger',
                }
            }
    
    def _execute_activity(self):
        """Exécute l'activité selon son type"""
        participants_processed = 0
        
        if self.activity_type == 'server_action' and self.server_action:
            # Obtenir les participants de la campagne
            participants = self.campaign_id.participant_ids.filtered(
                lambda p: p.state == 'running'
            )
            
            for participant in participants:
                try:
                    # Exécuter l'action serveur dans le contexte du contact
                    self.server_action.with_context(
                        active_id=participant.res_id,
                        active_model=participant.res_model,
                        active_ids=[participant.res_id],
                        scheduler_id=self.id,
                        campaign_id=self.campaign_id.id
                    ).run()
                    
                    participants_processed += 1
                    
                except Exception as e:
                    # Log de l'erreur mais continuer avec les autres participants
                    continue
        
        return participants_processed
    
    @api.model
    def _cron_execute_scheduled_activities(self):
        """Cron job pour exécuter les activités planifiées"""
        scheduled_activities = self.search([
            ('state', '=', 'scheduled'),
            ('scheduled_date', '<=', fields.Datetime.now())
        ])
        
        for activity in scheduled_activities:
            try:
                count = activity._execute_activity()
                activity.write({
                    'state': 'executed',
                    'execution_date': fields.Datetime.now(),
                    'participants_count': count
                })
            except Exception as e:
                activity.write({
                    'state': 'failed',
                    'error_message': str(e),
                    'execution_date': fields.Datetime.now()
                })
    
    def action_reset_to_scheduled(self):
        """Remettre l'activité en état planifié"""
        self.write({
            'state': 'scheduled',
            'execution_date': False,
            'error_message': False,
            'participants_count': 0
        })