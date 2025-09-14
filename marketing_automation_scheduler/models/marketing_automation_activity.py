from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta

class MarketingAutomationActivity(models.Model):
    _inherit = 'marketing.activity'

    # ---- Planification avancée (tes champs) ----
    is_scheduled = fields.Boolean(
        string='Planification avancée',
        default=False,
        help="Activer la planification avancée avec fréquence et quantité",
    )

    scheduled_quantity = fields.Integer(
        string="Nombre d'activités",
        default=1,
        help="Nombre total d'activités à créer",
    )

    schedule_frequency = fields.Selection(
        [
            ('daily', 'Quotidien'),
            ('weekly', 'Hebdomadaire'),
            ('monthly', 'Mensuel'),
            ('custom', 'Personnalisé'),
        ],
        string='Fréquence',
        default='weekly',
    )

    # Jours de la semaine
    monday = fields.Boolean('Lundi', default=False)
    tuesday = fields.Boolean('Mardi', default=False)
    wednesday = fields.Boolean('Mercredi', default=False)
    thursday = fields.Boolean('Jeudi', default=False)
    friday = fields.Boolean('Vendredi', default=False)
    saturday = fields.Boolean('Samedi', default=False)
    sunday = fields.Boolean('Dimanche', default=False)

    # Créneaux horaires
    time_slot_start = fields.Float(
        string='Heure de début',
        default=9.0,
        help="Heure de début au format décimal (ex: 9.5 = 9h30)",
    )
    time_slot_end = fields.Float(
        string='Heure de fin',
        default=17.0,
        help="Heure de fin au format décimal (ex: 17.0 = 17h00)",
    )

    # Intervalle entre activités
    interval_value = fields.Integer(
        string='Intervalle',
        default=1,
        help="Valeur de l'intervalle",
    )
    interval_unit = fields.Selection(
        [
            ('hours', 'Heures'),
            ('days', 'Jours'),
            ('weeks', 'Semaines'),
        ],
        string="Unité d'intervalle",
        default='days',
    )

    # Date de départ
    schedule_start_date = fields.Datetime(
        string='Date de début de planification',
        default=fields.Datetime.now,
    )

    # O2M vers le scheduler (utilisé par la vue)
    generated_scheduler_ids = fields.One2many(
        comodel_name='marketing.automation.scheduler',
        inverse_name='source_activity_id',
        string='Activités planifiées générées',
    )

    # ---------- Contraintes ----------
    @api.constrains('time_slot_start', 'time_slot_end')
    def _check_time_slots(self):
        for record in self:
            if record.is_scheduled:
                if record.time_slot_start >= record.time_slot_end:
                    raise ValidationError(_("L'heure de fin doit être supérieure à l'heure de début."))
                if record.time_slot_start < 0 or record.time_slot_end > 24:
                    raise ValidationError(_("Les heures doivent être comprises entre 0 et 24."))

    @api.constrains('scheduled_quantity')
    def _check_scheduled_quantity(self):
        for record in self:
            if record.is_scheduled and record.scheduled_quantity < 1:
                raise ValidationError(_("Le nombre d'activités doit être au moins de 1."))

    # ---------- Utilitaires ----------
    def _get_selected_weekdays(self):
        """Retourne la liste des jours sélectionnés (0=lundi, 6=dimanche)"""
        weekdays = []
        if self.monday: weekdays.append(0)
        if self.tuesday: weekdays.append(1)
        if self.wednesday: weekdays.append(2)
        if self.thursday: weekdays.append(3)
        if self.friday: weekdays.append(4)
        if self.saturday: weekdays.append(5)
        if self.sunday: weekdays.append(6)
        return weekdays

    def _calculate_next_execution_date(self, current_date, count):
        """Calcule la prochaine date d'exécution basée sur la fréquence"""
        if self.schedule_frequency == 'daily':
            return current_date + timedelta(days=self.interval_value * count)
        elif self.schedule_frequency == 'weekly':
            weekdays = self._get_selected_weekdays()
            if not weekdays:
                return current_date
            next_date = current_date
            for _ in range(count):
                found = False
                for _ in range(7):
                    next_date += timedelta(days=1)
                    if next_date.weekday() in weekdays:
                        found = True
                        break
                if not found:
                    next_date = current_date + timedelta(days=count)
                    break
            return next_date
        elif self.schedule_frequency == 'monthly':
            # approximation simple (30 jours * interval)
            return current_date + timedelta(days=30 * self.interval_value * count)
        else:  # custom
            return current_date + timedelta(days=self.interval_value * count)

    def _calculate_scheduled_time(self, date):
        """Calcule l'heure de planification dans le créneau horaire défini"""
        start_hour = int(self.time_slot_start)
        start_minute = int((self.time_slot_start - start_hour) * 60)
        return date.replace(hour=start_hour, minute=start_minute, second=0, microsecond=0)

    # ---------- Génération ----------
    def _generate_scheduled_activities(self):
        """Génère les activités planifiées selon les paramètres définis"""
        if not self.is_scheduled:
            return

        # nettoie les anciennes
        self.generated_scheduler_ids.unlink()

        scheduler_obj = self.env['marketing.automation.scheduler']
        current_date = self.schedule_start_date

        for i in range(self.scheduled_quantity):
            if i > 0:
                current_date = self._calculate_next_execution_date(self.schedule_start_date, i)
            scheduled_time = self._calculate_scheduled_time(current_date)

            # récupère l'action serveur depuis l'activité (v18 = server_action_id)
            server_action_id = False
            if hasattr(self, 'server_action_id') and self.server_action_id:
                server_action_id = self.server_action_id.id
            elif hasattr(self, 'server_action') and self.server_action:
                server_action_id = self.server_action.id

            scheduler_obj.create({
                'source_activity_id': self.id,
                'campaign_id': self.campaign_id.id,
                'activity_type': self.activity_type,  # ex: 'server_action'
                'server_action': server_action_id,    # champ du scheduler = 'server_action'
                'scheduled_date': scheduled_time,
                'name': f"{self.name} - #{i + 1}",
                'state': 'scheduled',
            })

    def action_generate_scheduled_activities(self):
        """Action bouton pour générer les activités planifiées"""
        self.ensure_one()
        if self.schedule_frequency == 'weekly' and not self._get_selected_weekdays():
            raise ValidationError(_("Vous devez sélectionner au moins un jour de la semaine pour la fréquence hebdomadaire."))
        self._generate_scheduled_activities()
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Activités générées'),
                'message': _('%d activités ont été planifiées avec succès.') % len(self.generated_scheduler_ids),
                'type': 'success',
            }
        }
