from app import app, db
from models import User
from werkzeug.security import generate_password_hash

def init_db():
    with app.app_context():
        # Création des tables
        db.create_all()
        
        # Création d'un utilisateur administrateur par défaut
        admin = User.query.filter_by(email='admin@example.com').first()
        if not admin:
            admin = User(
                email='admin@example.com',
                password=generate_password_hash('admin123'),
                name='Administrateur',
                role='admin'
            )
            db.session.add(admin)
            db.session.commit()
            print("Utilisateur administrateur créé avec succès!")
        else:
            print("L'utilisateur administrateur existe déjà.")

if __name__ == '__main__':
    init_db() 