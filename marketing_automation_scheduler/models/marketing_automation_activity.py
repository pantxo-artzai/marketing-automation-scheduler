from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import timedelta

class MarketingAutomationActivity(models.Model):
    _inherit = 'marketing.activity'

    # … tes champs existants …

    generated_scheduler_ids = fields.One2many(
        'marketing.automation.scheduler',
        'source_activity_id',
        string='Activités planifiées générées',
    )

    def _generate_scheduled_activities(self):
        if not self.is_scheduled:
            return
        self.generated_scheduler_ids.unlink()
        scheduler_obj = self.env['marketing.automation.scheduler']
        current_date = self.schedule_start_date

        for i in range(self.scheduled_quantity):
            if i > 0:
                current_date = self._calculate_next_execution_date(self.schedule_start_date, i)
            scheduled_time = self._calculate_scheduled_time(current_date)

            # Récupère l'ID de l'action serveur, quel que soit le nom sur activity
            server_action_id = False
            if hasattr(self, 'server_action_id') and self.server_action_id:
                server_action_id = self.server_action_id.id
            elif hasattr(self, 'server_action') and self.server_action:
                server_action_id = self.server_action.id

            scheduler_obj.create({
                'source_activity_id': self.id,
                'campaign_id': self.campaign_id.id,
                'activity_type': self.activity_type,      # 'server_action' attendu par ton scheduler
                'server_action': server_action_id,        # champ du scheduler = 'server_action'
                'scheduled_date': scheduled_time,
                'name': f"{self.name} - #{i + 1}",
                'state': 'scheduled',
            })
