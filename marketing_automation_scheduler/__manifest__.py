{
    'name': 'Marketing Automation Scheduler',
    'version': '18.0.1.0.0',
    'category': 'Marketing',
    'summary': 'Enhanced Marketing Automation with Advanced Activity Scheduling',
    'description': """
        Marketing Automation Scheduler
        ==============================
        
        Ce module étend la fonctionnalité Marketing Automation d'Odoo pour permettre:
        
        * Planification d'activités avec fréquence et quantité spécifiques
        * Définition de créneaux horaires et jours de la semaine
        * Création automatique d'activités planifiées
        * Exécution automatique via cron job
        * Interface de gestion des activités planifiées
        
        Fonctionnalités principales:
        ---------------------------
        - Configuration de la fréquence (quotidien, hebdomadaire, mensuel)
        - Sélection des jours de la semaine
        - Définition des créneaux horaires (ex: 9h00-17h00)
        - Génération automatique d'activités selon les paramètres
        - Suivi de l'état des activités (planifié, exécuté, échoué)
        - Actions serveur personnalisables pour créer des tâches
        
        Exemple d'utilisation:
        ---------------------
        1. Créer une campagne marketing automation
        2. Ajouter une activité de type "Server Action" 
        3. Activer la "Planification avancée"
        4. Définir: 10 appels, tous les mardi/mercredi, 9h-17h
        5. Générer les activités planifiées
        6. Le système exécute automatiquement selon la planification
    """,
    'author': 'Votre Entreprise',
    'website': 'https://votre-entreprise.com',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'marketing_automation',
        'contacts',
        'calendar',
        'mail',
    ],
'data': [
    'security/marketing_automation_scheduler_security.xml',
    'security/ir.model.access.csv',
    'data/server_actions_data.xml',
    'data/ir_cron_data.xml',
    'views/marketing_automation_activity_views.xml',
    'views/marketing_automation_scheduler_views.xml',
],
'depends': ['base', 'marketing_automation', 'contacts', 'calendar', 'mail'],
    'demo': [],
    'installable': True,
    'auto_install': False,
    'application': False,
    'images': ['static/description/icon.png'],
}