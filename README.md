# Marketing Automation Scheduler

Module Odoo v18 qui étend le Marketing Automation pour permettre une planification avancée d'activités avec fréquence, créneaux horaires et quantités spécifiques.

## Fonctionnalités

- **Planification Avancée** : Définissez quantité, fréquence et créneaux horaires
- **Jours Personnalisés** : Sélection des jours de la semaine spécifiques  
- **Créneaux Horaires** : Configuration des heures de début/fin (ex: 9h-17h)
- **Exécution Automatique** : Cron job intégré toutes les 15 minutes
- **Interface Dédiée** : Vues Kanban, Liste et Formulaire
- **Actions Serveur** : Templates inclus pour appels, réunions, emails

## Installation

1. Télécharger le module dans le dossier addons d'Odoo
2. Redémarrer Odoo
3. Activer le mode développeur
4. Aller dans Apps > Mettre à jour la liste des apps
5. Rechercher "Marketing Automation Scheduler"
6. Installer le module

## Configuration

### Étape 1: Campagne Marketing Automation
1. Aller dans Marketing > Marketing Automation > Campagnes  
2. Créer ou modifier une campagne existante
3. Ajouter une activité de type "Server Action"

### Étape 2: Configuration de l'Activité
1. Dans l'activité, activer "Planification avancée"
2. Configurer les paramètres :
   - **Nombre d'activités** : ex. 10
   - **Fréquence** : Hebdomadaire
   - **Jours** : Mardi + Mercredi  
   - **Heures** : 9h00 - 17h00
   - **Date de début** : Date souhaitée

### Étape 3: Génération
1. Cliquer sur "Générer les Activités Planifiées"
2. Vérifier dans l'onglet "Activités Planifiées Générées"

## Utilisation

### Suivi des Activités Planifiées
- Menu : **Marketing > Activités Planifiées**
- Vue Kanban par état (Planifié/Exécuté/Échoué)
- Filtres : Aujourd'hui, Cette semaine, En retard

### Actions Disponibles
- **Exécuter Maintenant** : Lancement manuel immédiat
- **Replanifier** : Remettre en état "Planifié" 
- **Suivi Détaillé** : Nombre de participants traités

### Actions Serveur Incluses

#### 1. Créer Activité d'Appel
```python
# Crée une tâche d'appel dans la fiche contact avec échéance 2h
```

#### 2. Créer Activité de Réunion  
```python
# Crée une tâche de réunion avec échéance 1 jour
```

#### 3. Envoyer Email de Suivi
```python
# Envoi automatique d'email personnalisé si adresse présente
```

## Exemples d'Usage

### Cas 1: Appels Commerciaux Récurrents
- **Objectif** : 20 appels de prospection par semaine
- **Configuration** : 
  - Quantité: 20
  - Fréquence: Hebdomadaire  
  - Jours: Mardi, Mercredi, Jeudi
  - Heures: 9h00-12h00 et 14h00-17h00

### Cas 2: Emails de Nurturing
- **Objectif** : 5 emails sur 2 semaines  
- **Configuration** :
  - Quantité: 5
  - Fréquence: Personnalisé
  - Intervalle: 3 jours

### Cas 3: Relances Clients
- **Objectif** : Rappels échelonnés après devis
- **Configuration** :
  - Quantité: 3
  - Fréquence: Personnalisé  
  - Intervalles: J+3, J+7, J+14

## Architecture Technique

### Modèles
- `marketing.automation.activity` (étendu)
- `marketing.automation.scheduler` (nouveau)

### Vues  
- Formulaire activité avec section planification
- Vues Kanban/Liste/Formulaire pour scheduler
- Filtres et groupements avancés

### Cron Job
```xml
<!-- Exécution automatique toutes les 15 minutes -->
<field name="interval_number">15</field>
<field name="interval_type">minutes</field>
```

### Sécurité
- Droits basés sur groupes Marketing Automation existants
- Accès lecture/écriture pour utilisateurs et managers

## Personnalisation

### Créer une Action Serveur Personnalisée
1. Aller dans Paramètres > Actions > Actions Serveur
2. Créer nouvelle action sur modèle `res.partner`
3. Code Python pour traitement personnalisé
4. Utiliser dans campagne marketing automation

### Exemple Action Personnalisée
```python
# Intégration téléphonie - créer appel sortant
phone_system = env['phone.system'].sudo()
if record.phone:
    call_id = phone_system.create_outbound_call({
        'number': record.phone,
        'contact_id': record.id,
        'campaign': env.context.get('campaign_id')
    })
    record.message_post(body=f"Appel automatique programmé: {call_id}")
```

## Maintenance

### Nettoyage Données
Les anciennes activités exécutées peuvent être archivées/supprimées périodiquement pour optimiser les performances.

### Surveillance  
- Surveiller les activités en échec via vue filtrée
- Vérifier logs cron job si problèmes d'exécution
- Monitoring des performances sur gros volumes

## Support

- **Documentation** : Module basé sur marketing_automation d'Odoo
- **Communauté** : Forums Odoo pour questions générales  
- **Support Pro** : Via intégrateur Odoo certifié

## Licence

LGPL-3 - Compatible avec Odoo Community et Enterprise

---

**Version** : 18.0.1.0.0  
**Auteur** : Votre Entreprise  
**Compatibilité** : Odoo 18.0+