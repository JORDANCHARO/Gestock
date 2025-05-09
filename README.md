# Gestock - Application de Gestion de Boulangerie

Gestock est une application web de gestion complète pour boulangeries, développée avec Flask et SQLAlchemy.

## Fonctionnalités

- Gestion des stocks et des produits
- Gestion des recettes et de la production
- Gestion des ventes et des clients
- Gestion des fournisseurs
- Gestion des utilisateurs et des rôles
- Rapports et statistiques
- Interface adaptée aux écrans tactiles

## Prérequis

- Python 3.8 ou supérieur
- pip (gestionnaire de paquets Python)
- Git

## Installation

1. Cloner le dépôt :
```bash
git clone https://github.com/votre-username/gestock.git
cd gestock
```

2. Créer un environnement virtuel :
```bash
python -m venv venv
source venv/bin/activate  # Sur Windows : venv\Scripts\activate
```

3. Installer les dépendances :
```bash
pip install -r requirements.txt
```

4. Initialiser la base de données :
```bash
python init_db.py
```

## Configuration

1. Créer un fichier `.env` à la racine du projet :
```
FLASK_APP=app.py
FLASK_ENV=development
SECRET_KEY=votre_clé_secrète
```

2. Pour la production, configurer les variables d'environnement :
- `DATABASE_URL` : URL de la base de données PostgreSQL
- `FLASK_ENV=production`
- `SECRET_KEY` : Clé secrète pour la sécurité

## Démarrage

1. Mode développement :
```bash
python app.py
```

2. Mode production :
```bash
gunicorn app:app
```

## Accès

- URL : http://localhost:5000
- Identifiants par défaut :
  - Utilisateur : admin
  - Mot de passe : admin123

## Déploiement

L'application peut être déployée sur :
- Render.com
- Heroku
- PythonAnywhere
- Votre propre serveur

## Contribution

Les contributions sont les bienvenues ! N'hésitez pas à :
1. Fork le projet
2. Créer une branche pour votre fonctionnalité
3. Commiter vos changements
4. Pousser vers la branche
5. Ouvrir une Pull Request

## Licence

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails. 