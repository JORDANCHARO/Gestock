# GestStock - Gestion de Stock pour Boulangerie

Une application web simple et efficace pour gérer les stocks d'une boulangerie, développée avec Flask et SQLite.

## Fonctionnalités

- Authentification des utilisateurs (admin et employés)
- Gestion des matières premières et produits finis
- Suivi des entrées et sorties de stock
- Alertes de stock bas
- Tableau de bord avec statistiques
- Interface utilisateur intuitive

## Prérequis

- Python 3.8 ou supérieur
- pip (gestionnaire de paquets Python)

## Installation

1. Clonez ce dépôt ou téléchargez les fichiers

2. Créez un environnement virtuel (recommandé) :
```bash
python -m venv venv
```

3. Activez l'environnement virtuel :
- Windows :
```bash
venv\Scripts\activate
```
- Mac/Linux :
```bash
source venv/bin/activate
```

4. Installez les dépendances :
```bash
pip install -r requirements.txt
```

5. Initialisez la base de données :
```bash
python init_db.py
```

## Lancement de l'application

1. Démarrez le serveur :
```bash
python app.py
```

2. Accédez à l'application dans votre navigateur :
```
http://localhost:5000
```

## Identifiants par défaut

- Email : admin@boulangerie.com
- Mot de passe : admin123

## Structure du projet

```
gestock/
├── app.py              # Point d'entrée de l'application
├── models.py           # Modèles de données
├── init_db.py          # Script d'initialisation de la base de données
├── requirements.txt    # Dépendances Python
├── database/          # Dossier contenant la base de données SQLite
└── templates/         # Templates HTML
    ├── base.html
    ├── login.html
    └── dashboard.html
```

## Sécurité

- Changez le mot de passe administrateur par défaut après la première connexion
- La clé secrète de l'application doit être modifiée en production
- Utilisez HTTPS en production

## Licence

Ce projet est sous licence MIT. 