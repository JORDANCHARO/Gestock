from flask import Flask, render_template, redirect, url_for, flash, request, jsonify, send_file
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import os
from models import (
    db, User, Product, StockMovement, Supplier, Recipe, 
    RecipeIngredient, Sale, ProductBatch, ProductionRecord, Category, Customer, SaleItem, Expense, ProductionSchedule
)
from sqlalchemy import func, desc
from decimal import Decimal
from functools import wraps
from weasyprint import HTML
import tempfile

app = Flask(__name__)
app.config['SECRET_KEY'] = 'votre_clé_secrète_ici'

# Ajout du filtre format_currency
@app.template_filter('format_currency')
def format_currency(value):
    return "{:,.2f}".format(float(value))

# Création du chemin absolu pour la base de données
basedir = os.path.abspath(os.path.dirname(__file__))

# Configuration de la base de données
if os.environ.get('DATABASE_URL'):
    # Configuration pour la production (PostgreSQL)
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL').replace('postgres://', 'postgresql://')
else:
    # Configuration pour le développement (SQLite)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'database', 'stock.db')

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialisation de la base de données avec l'application
db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

def insert_sample_data():
    try:
        # Création des catégories
        categories = [
            Category(name='Pain', description='Pains et baguettes'),
            Category(name='Viennoiseries', description='Croissants, pains au chocolat, etc.'),
            Category(name='Pâtisseries', description='Gâteaux et desserts'),
            Category(name='Sandwichs', description='Sandwichs et paninis')
        ]
        for category in categories:
            db.session.add(category)
        db.session.commit()

        # Création des fournisseurs
        suppliers = [
            Supplier(name='Meunerie du Nord', contact='Jean Dupont', phone='0123456789', email='contact@meunerie.fr'),
            Supplier(name='Fruits & Légumes Express', contact='Marie Martin', phone='0234567890', email='contact@fruits.fr'),
            Supplier(name='Lait Frais SA', contact='Pierre Durand', phone='0345678901', email='contact@lait.fr')
        ]
        for supplier in suppliers:
            db.session.add(supplier)
        db.session.commit()

        # Création des produits
        products = [
            Product(name='Farine T55', description='Farine de blé type 55', category_id=1, supplier_id=1, 
                   quantity=100, unit='kg', min_quantity=20, price=0.85),
            Product(name='Beurre', description='Beurre doux', category_id=2, supplier_id=3, 
                   quantity=50, unit='kg', min_quantity=10, price=8.50),
            Product(name='Sucre', description='Sucre blanc', category_id=1, supplier_id=1, 
                   quantity=80, unit='kg', min_quantity=15, price=1.20),
            Product(name='Œufs', description='Œufs frais calibre M', category_id=2, supplier_id=2, 
                   quantity=200, unit='pièce', min_quantity=50, price=0.35),
            Product(name='Chocolat', description='Chocolat noir pâtissier', category_id=2, supplier_id=1, 
                   quantity=30, unit='kg', min_quantity=5, price=12.50)
        ]
        for product in products:
            db.session.add(product)
        db.session.commit()

        # Création des recettes
        recipes = [
            Recipe(name='Baguette Tradition', description='Baguette française traditionnelle', 
                  preparation_time=30, cooking_time=25, yield_quantity=1, yield_unit='pièce'),
            Recipe(name='Croissant', description='Croissant au beurre', 
                  preparation_time=45, cooking_time=20, yield_quantity=12, yield_unit='pièce'),
            Recipe(name='Pain au Chocolat', description='Pain au chocolat', 
                  preparation_time=40, cooking_time=20, yield_quantity=12, yield_unit='pièce')
        ]
        for recipe in recipes:
            db.session.add(recipe)
        db.session.commit()

        # Création des clients
        customers = [
            Customer(name='Restaurant Le Petit Bistrot', contact='Sophie Martin', 
                    phone='0456789012', email='contact@bistrot.fr'),
            Customer(name='Hôtel Les Palmiers', contact='Thomas Dubois', 
                    phone='0567890123', email='contact@hotel.fr'),
            Customer(name='Épicerie Fine', contact='Julie Leroy', 
                    phone='0678901234', email='contact@epicerie.fr')
        ]
        for customer in customers:
            db.session.add(customer)
        db.session.commit()

        # Création des utilisateurs
        users = [
            User(username='boulanger1', password=generate_password_hash('boulanger123'), role='baker'),
            User(username='caissier1', password=generate_password_hash('caissier123'), role='cashier'),
            User(username='caissier2', password=generate_password_hash('caissier123'), role='cashier')
        ]
        for user in users:
            db.session.add(user)
        db.session.commit()

        # Création des ventes
        sales = [
            Sale(date=datetime.utcnow(), total_amount=45.50, payment_method='card', 
                 customer_id=1, user_id=2),
            Sale(date=datetime.utcnow(), total_amount=32.75, payment_method='cash', 
                 customer_id=2, user_id=2),
            Sale(date=datetime.utcnow(), total_amount=28.90, payment_method='card', 
                 customer_id=3, user_id=3)
        ]
        for sale in sales:
            db.session.add(sale)
        db.session.commit()

        # Création des dépenses
        expenses = [
            Expense(date=datetime.utcnow(), amount=150.00, category='Fournitures', 
                   description='Achat de farine', user_id=1),
            Expense(date=datetime.utcnow(), amount=85.50, category='Équipement', 
                   description='Réparation du four', user_id=1),
            Expense(date=datetime.utcnow(), amount=45.00, category='Divers', 
                   description='Nettoyage', user_id=1)
        ]
        for expense in expenses:
            db.session.add(expense)
        db.session.commit()

        # Création des plannings de production
        schedules = [
            ProductionSchedule(
                recipe_id=1, planned_quantity=20, 
                planned_start_time=datetime.utcnow() + timedelta(hours=2),
                planned_end_time=datetime.utcnow() + timedelta(hours=4),
                status='scheduled', priority=1, created_by=2
            ),
            ProductionSchedule(
                recipe_id=2, planned_quantity=50, 
                planned_start_time=datetime.utcnow() + timedelta(hours=5),
                planned_end_time=datetime.utcnow() + timedelta(hours=7),
                status='scheduled', priority=2, created_by=2
            )
        ]
        for schedule in schedules:
            db.session.add(schedule)
        db.session.commit()

    except Exception as e:
        print(f"Erreur lors de l'insertion des données : {str(e)}")
        db.session.rollback()
        raise e

# Création de l'utilisateur administrateur au démarrage
with app.app_context():
    db.create_all()
    admin = User.query.filter_by(username='admin').first()
    if not admin:
        admin = User(
            username='admin',
            password=generate_password_hash('admin123'),
            role='manager'
        )
        db.session.add(admin)
        db.session.commit()
        
        # Insérer les données fictives après la création de l'admin
        insert_sample_data()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password, password):
            login_user(user)
            user.last_login = datetime.utcnow()
            db.session.commit()
            return redirect(url_for('dashboard'))
        flash('Nom d\'utilisateur ou mot de passe incorrect')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    # Récupérer les statistiques pour le tableau de bord
    products = Product.query.all()
    low_stock_products = [p for p in products if p.quantity <= p.min_quantity]
    sales = Sale.query.order_by(Sale.date.desc()).limit(5).all()
    expenses = Expense.query.order_by(Expense.date.desc()).limit(5).all()
    schedules = ProductionSchedule.query.filter_by(status='scheduled').all()
    
    return render_template('dashboard.html', 
                         products=products,
                         low_stock_products=low_stock_products,
                         sales=sales,
                         expenses=expenses,
                         schedules=schedules)

# Routes pour la gestion des produits
@app.route('/products')
@login_required
def products():
    products = Product.query.all()
    return render_template('products.html', products=products)

def manager_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.has_role('manager'):
            flash('Accès non autorisé. Vous devez être gestionnaire.', 'danger')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def baker_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not (current_user.has_role('manager') or current_user.has_role('baker')):
            flash('Accès non autorisé. Vous devez être boulanger ou gestionnaire.', 'danger')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def cashier_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not (current_user.has_role('manager') or current_user.has_role('cashier')):
            flash('Accès non autorisé. Vous devez être caissier ou gestionnaire.', 'danger')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/products/add', methods=['GET', 'POST'])
@login_required
@manager_required
def add_product():
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        price = float(request.form.get('price'))
        stock = int(request.form.get('stock'))
        unit = request.form.get('unit')
        category_id = request.form.get('category_id')
        
        if not name or not unit:
            flash('Le nom et l\'unité du produit sont requis', 'danger')
            return redirect(url_for('add_product'))
        
        product = Product(
            name=name,
            description=description,
            price=price,
            stock=stock,
            unit=unit,
            category_id=category_id if category_id else None
        )
        
        db.session.add(product)
        db.session.commit()
        
        flash('Produit ajouté avec succès', 'success')
        return redirect(url_for('products'))
    
    categories = Category.query.all()
    return render_template('add_product.html', categories=categories)

@app.route('/products/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@manager_required
def edit_product(id):
    product = Product.query.get_or_404(id)
    if request.method == 'POST':
        product.name = request.form.get('name')
        product.description = request.form.get('description')
        product.category_id = request.form.get('category_id')
        product.supplier_id = request.form.get('supplier_id')
        product.unit = request.form.get('unit')
        product.quantity = float(request.form.get('quantity', 0))
        product.min_quantity = float(request.form.get('min_quantity', 0))
        product.price = float(request.form.get('price', 0))
        
        db.session.commit()
        flash('Produit modifié avec succès!')
        return redirect(url_for('products'))
    
    categories = Category.query.all()
    suppliers = Supplier.query.all()
    return render_template('edit_product.html', product=product, categories=categories, suppliers=suppliers)

@app.route('/products/delete/<int:id>')
@login_required
def delete_product(id):
    product = Product.query.get_or_404(id)
    db.session.delete(product)
    db.session.commit()
    flash('Produit supprimé avec succès!')
    return redirect(url_for('products'))

# Routes pour les mouvements de stock
@app.route('/movements')
@login_required
def movements():
    movements = StockMovement.query.order_by(StockMovement.date.desc()).all()
    return render_template('movements.html', movements=movements)

@app.route('/movements/add', methods=['GET', 'POST'])
@login_required
def add_movement():
    if request.method == 'POST':
        product_id = request.form.get('product_id')
        type = request.form.get('type')
        quantity = float(request.form.get('quantity'))
        description = request.form.get('description')

        movement = StockMovement(
            product_id=product_id,
            type=type,
            quantity=quantity,
            description=description,
            user_id=current_user.id
        )

        # Mise à jour du stock
        product = Product.query.get(product_id)
        if type == 'in':
            product.quantity += quantity
        else:
            product.quantity -= quantity

        db.session.add(movement)
        db.session.commit()
        flash('Mouvement de stock enregistré avec succès!')
        return redirect(url_for('movements'))

    products = Product.query.all()
    return render_template('add_movement.html', products=products)

# Routes pour la gestion des fournisseurs
@app.route('/suppliers')
@login_required
@manager_required
def suppliers():
    suppliers = Supplier.query.all()
    return render_template('suppliers.html', suppliers=suppliers)

@app.route('/suppliers/add', methods=['GET', 'POST'])
@login_required
@manager_required
def add_supplier():
    if request.method == 'POST':
        supplier = Supplier(
            name=request.form.get('name'),
            contact=request.form.get('contact'),
            phone=request.form.get('phone'),
            email=request.form.get('email'),
            address=request.form.get('address')
        )
        db.session.add(supplier)
        db.session.commit()
        flash('Fournisseur ajouté avec succès!')
        return redirect(url_for('suppliers'))
    return render_template('add_supplier.html')

@app.route('/suppliers/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_supplier(id):
    supplier = Supplier.query.get_or_404(id)
    if request.method == 'POST':
        supplier.name = request.form.get('name')
        supplier.contact = request.form.get('contact')
        supplier.phone = request.form.get('phone')
        supplier.email = request.form.get('email')
        supplier.address = request.form.get('address')
        db.session.commit()
        flash('Fournisseur modifié avec succès!')
        return redirect(url_for('suppliers'))
    return render_template('edit_supplier.html', supplier=supplier)

# Routes pour la gestion des recettes
@app.route('/recipes')
@login_required
@baker_required
def recipes():
    recipes = Recipe.query.all()
    return render_template('recipes.html', recipes=recipes)

@app.route('/recipes/add', methods=['GET', 'POST'])
@login_required
@baker_required
def add_recipe():
    if request.method == 'POST':
        recipe = Recipe(
            name=request.form.get('name'),
            description=request.form.get('description'),
            preparation_time=int(request.form.get('preparation_time')),
            cooking_time=int(request.form.get('cooking_time')),
            temperature=int(request.form.get('temperature')),
            yield_quantity=float(request.form.get('yield_quantity')),
            yield_unit=request.form.get('yield_unit'),
            selling_price=float(request.form.get('selling_price'))
        )
        db.session.add(recipe)
        db.session.commit()
        
        # Ajout des ingrédients
        ingredients = request.form.getlist('ingredients[]')
        quantities = request.form.getlist('quantities[]')
        units = request.form.getlist('units[]')
        
        total_cost = 0
        for i in range(len(ingredients)):
            product = Product.query.get(int(ingredients[i]))
            quantity = float(quantities[i])
            unit = units[i]
            
            # Calcul du coût de l'ingrédient
            ingredient_cost = (quantity * product.purchase_price) / product.quantity
            total_cost += ingredient_cost
            
            ingredient = RecipeIngredient(
                recipe_id=recipe.id,
                product_id=product.id,
                quantity=quantity,
                unit=unit,
                cost=ingredient_cost
            )
            db.session.add(ingredient)
        
        recipe.cost_price = total_cost
        db.session.commit()
        flash('Recette ajoutée avec succès!')
        return redirect(url_for('recipes'))
    
    products = Product.query.filter_by(type='raw').all()
    return render_template('add_recipe.html', products=products)

# Routes pour la gestion des ventes
@app.route('/sales')
@login_required
@cashier_required
def sales():
    sales = Sale.query.order_by(Sale.date.desc()).all()
    return render_template('sales.html', sales=sales)

@app.route('/sales/add', methods=['GET', 'POST'])
@login_required
@cashier_required
def add_sale():
    if request.method == 'POST':
        payment_method = request.form.get('payment_method')
        customer_id = request.form.get('customer_id')
        
        # Création de la vente
        sale = Sale(
            payment_method=payment_method,
            user_id=current_user.id,
            customer_id=customer_id if customer_id else None
        )
        db.session.add(sale)
        
        # Ajout des produits à la vente
        total_price = 0
        products = request.form.getlist('product_id[]')
        quantities = request.form.getlist('quantity[]')
        
        for product_id, quantity in zip(products, quantities):
            if product_id and quantity:
                product = Product.query.get(product_id)
                quantity = float(quantity)
                
                # Création de l'item de vente
                sale_item = SaleItem(
                    sale=sale,
                    product_id=product_id,
                    quantity=quantity,
                    unit_price=product.price
                )
                db.session.add(sale_item)
                
                # Mise à jour du stock
                product.stock -= quantity
                
                # Calcul du prix total
                total_price += product.price * quantity
        
        sale.total_price = total_price
        db.session.commit()
        flash('Vente enregistrée avec succès!')
        return redirect(url_for('sales'))
    
    products = Product.query.all()
    customers = Customer.query.all()
    return render_template('add_sale.html', products=products, customers=customers)

# Routes pour la gestion des lots
@app.route('/batches')
@login_required
def batches():
    batches = ProductBatch.query.order_by(ProductBatch.expiry_date.asc()).all()
    return render_template('batches.html', batches=batches)

@app.route('/batches/add', methods=['GET', 'POST'])
@login_required
def add_batch():
    if request.method == 'POST':
        product_id = request.form.get('product_id')
        quantity = float(request.form.get('quantity'))
        production_date = datetime.strptime(request.form.get('production_date'), '%Y-%m-%d')
        expiry_date = datetime.strptime(request.form.get('expiry_date'), '%Y-%m-%d')
        
        # Génération du numéro de lot
        batch_number = f"LOT-{datetime.now().strftime('%Y%m%d')}-{product_id}"
        
        batch = ProductBatch(
            product_id=product_id,
            batch_number=batch_number,
            quantity=quantity,
            production_date=production_date,
            expiry_date=expiry_date
        )
        db.session.add(batch)
        
        # Mise à jour du stock
        product = Product.query.get(product_id)
        product.quantity += quantity
        
        db.session.commit()
        flash('Lot ajouté avec succès!')
        return redirect(url_for('batches'))
    
    products = Product.query.filter_by(type='raw').all()
    return render_template('add_batch.html', products=products)

# Routes pour la gestion de la production
@app.route('/production')
@login_required
def production():
    today = datetime.now().date()
    production_records = ProductionRecord.query.filter(
        db.func.date(ProductionRecord.start_time) == today
    ).order_by(ProductionRecord.start_time.desc()).all()
    return render_template('production.html', production_records=production_records)

@app.route('/production/add', methods=['GET', 'POST'])
@login_required
def add_production():
    if request.method == 'POST':
        recipe_id = request.form.get('recipe_id')
        quantity = float(request.form.get('quantity'))
        notes = request.form.get('notes')
        
        production = ProductionRecord(
            recipe_id=recipe_id,
            quantity=quantity,
            start_time=datetime.now(),
            notes=notes,
            user_id=current_user.id
        )
        db.session.add(production)
        db.session.commit()
        flash('Production démarrée avec succès!')
        return redirect(url_for('production'))
    
    recipes = Recipe.query.all()
    return render_template('add_production.html', recipes=recipes)

@app.route('/production/complete/<int:id>', methods=['POST'])
@login_required
def complete_production(id):
    production = ProductionRecord.query.get_or_404(id)
    production.end_time = datetime.now()
    production.status = 'completed'
    
    # Création du lot de production
    batch = ProductBatch(
        product_id=production.recipe.id,
        batch_number=f"PROD-{datetime.now().strftime('%Y%m%d')}-{id}",
        quantity=production.quantity,
        production_date=production.start_time,
        expiry_date=production.start_time + timedelta(days=2)  # Exemple: 2 jours de conservation
    )
    db.session.add(batch)
    
    # Mise à jour du stock
    product = Product.query.get(production.recipe.id)
    product.quantity += production.quantity
    
    db.session.commit()
    flash('Production terminée avec succès!')
    return redirect(url_for('production'))

# Routes pour la gestion des dépenses
@app.route('/expenses')
@login_required
@manager_required
def expenses():
    expenses = Expense.query.order_by(Expense.date.desc()).all()
    return render_template('expenses.html', expenses=expenses)

@app.route('/expenses/add', methods=['GET', 'POST'])
@login_required
@manager_required
def add_expense():
    if request.method == 'POST':
        expense = Expense(
            description=request.form.get('description'),
            amount=float(request.form.get('amount')),
            category=request.form.get('category'),
            date=datetime.strptime(request.form.get('date'), '%Y-%m-%d'),
            user_id=current_user.id
        )
        db.session.add(expense)
        db.session.commit()
        flash('Dépense enregistrée avec succès!')
        return redirect(url_for('expenses'))
    return render_template('add_expense.html')

# Routes pour la gestion des utilisateurs
@app.route('/users')
@login_required
@manager_required
def users():
    users = User.query.all()
    return render_template('users.html', users=users)

@app.route('/users/add', methods=['GET', 'POST'])
@login_required
@manager_required
def add_user():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        role = request.form.get('role')
        
        if User.query.filter_by(username=username).first():
            flash('Ce nom d\'utilisateur existe déjà', 'danger')
            return redirect(url_for('add_user'))
        
        user = User(
            username=username,
            password=generate_password_hash(password),
            role=role
        )
        db.session.add(user)
        db.session.commit()
        flash('Utilisateur créé avec succès!', 'success')
        return redirect(url_for('users'))
    
    return render_template('add_user.html')

@app.route('/users/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@manager_required
def edit_user(id):
    user = User.query.get_or_404(id)
    if request.method == 'POST':
        username = request.form.get('username')
        role = request.form.get('role')
        password = request.form.get('password')
        
        # Vérifier si le nom d'utilisateur existe déjà pour un autre utilisateur
        existing_user = User.query.filter(User.username == username, User.id != id).first()
        if existing_user:
            flash('Ce nom d\'utilisateur existe déjà', 'danger')
            return redirect(url_for('edit_user', id=id))
        
        user.username = username
        user.role = role
        if password:  # Mettre à jour le mot de passe seulement si un nouveau est fourni
            user.password = generate_password_hash(password)
        
        db.session.commit()
        flash('Utilisateur mis à jour avec succès!', 'success')
        return redirect(url_for('users'))
    
    return render_template('edit_user.html', user=user)

@app.route('/users/<int:id>/delete', methods=['POST'])
@login_required
@manager_required
def delete_user(id):
    user = User.query.get_or_404(id)
    if user.id == current_user.id:
        flash('Vous ne pouvez pas supprimer votre propre compte', 'danger')
        return redirect(url_for('users'))
    
    db.session.delete(user)
    db.session.commit()
    flash('Utilisateur supprimé avec succès!', 'success')
    return redirect(url_for('users'))

# Routes pour la gestion des catégories
@app.route('/categories')
@login_required
@manager_required
def categories():
    categories = Category.query.all()
    return render_template('categories.html', categories=categories)

@app.route('/categories/add', methods=['GET', 'POST'])
@login_required
@manager_required
def add_category():
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        
        if not name:
            flash('Le nom de la catégorie est requis', 'danger')
            return redirect(url_for('add_category'))
        
        category = Category(name=name, description=description)
        db.session.add(category)
        db.session.commit()
        
        flash('Catégorie ajoutée avec succès', 'success')
        return redirect(url_for('categories'))
    
    return render_template('add_category.html')

@app.route('/categories/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_category(id):
    category = Category.query.get_or_404(id)
    
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        
        if not name:
            flash('Le nom de la catégorie est requis', 'danger')
            return redirect(url_for('edit_category', id=id))
        
        category.name = name
        category.description = description
        db.session.commit()
        
        flash('Catégorie modifiée avec succès', 'success')
        return redirect(url_for('categories'))
    
    return render_template('edit_category.html', category=category)

@app.route('/categories/delete/<int:id>')
@login_required
def delete_category(id):
    category = Category.query.get_or_404(id)
    
    # Vérifier si la catégorie a des produits
    if category.products:
        flash('Impossible de supprimer une catégorie qui contient des produits', 'danger')
        return redirect(url_for('categories'))
    
    db.session.delete(category)
    db.session.commit()
    
    flash('Catégorie supprimée avec succès', 'success')
    return redirect(url_for('categories'))

# Routes pour la gestion des clients
@app.route('/customers')
@login_required
@cashier_required
def customers():
    customers = Customer.query.all()
    return render_template('customers.html', customers=customers)

@app.route('/customers/add', methods=['GET', 'POST'])
@login_required
@manager_required
def add_customer():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        address = request.form.get('address')
        
        if not name:
            flash('Le nom du client est requis', 'danger')
            return redirect(url_for('add_customer'))
        
        if email and Customer.query.filter_by(email=email).first():
            flash('Cette adresse email est déjà utilisée', 'danger')
            return redirect(url_for('add_customer'))
        
        customer = Customer(
            name=name,
            email=email,
            phone=phone,
            address=address
        )
        
        db.session.add(customer)
        db.session.commit()
        
        flash('Client ajouté avec succès', 'success')
        return redirect(url_for('customers'))
    
    return render_template('add_customer.html')

@app.route('/customers/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_customer(id):
    customer = Customer.query.get_or_404(id)
    
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        address = request.form.get('address')
        
        if not name:
            flash('Le nom du client est requis', 'danger')
            return redirect(url_for('edit_customer', id=id))
        
        if email and email != customer.email:
            existing_customer = Customer.query.filter_by(email=email).first()
            if existing_customer and existing_customer.id != customer.id:
                flash('Cette adresse email est déjà utilisée', 'danger')
                return redirect(url_for('edit_customer', id=id))
        
        customer.name = name
        customer.email = email
        customer.phone = phone
        customer.address = address
        
        db.session.commit()
        
        flash('Client modifié avec succès', 'success')
        return redirect(url_for('customers'))
    
    return render_template('edit_customer.html', customer=customer)

@app.route('/customers/delete/<int:id>')
@login_required
def delete_customer(id):
    customer = Customer.query.get_or_404(id)
    
    # Vérifier si le client a des ventes
    if customer.sales:
        flash('Impossible de supprimer un client qui a des ventes', 'danger')
        return redirect(url_for('customers'))
    
    db.session.delete(customer)
    db.session.commit()
    
    flash('Client supprimé avec succès', 'success')
    return redirect(url_for('customers'))

# Routes pour la planification de la production
@app.route('/production/schedule')
@login_required
@baker_required
def production_schedule():
    schedules = ProductionSchedule.query.filter(
        ProductionSchedule.planned_start_time >= datetime.now()
    ).order_by(ProductionSchedule.planned_start_time).all()
    return render_template('production_schedule.html', schedules=schedules)

@app.route('/production/schedule/add', methods=['GET', 'POST'])
@login_required
@baker_required
def add_production_schedule():
    if request.method == 'POST':
        recipe_id = request.form.get('recipe_id')
        planned_quantity = float(request.form.get('planned_quantity'))
        planned_start_time = datetime.strptime(request.form.get('planned_start_time'), '%Y-%m-%dT%H:%M')
        planned_end_time = datetime.strptime(request.form.get('planned_end_time'), '%Y-%m-%dT%H:%M')
        priority = int(request.form.get('priority'))
        notes = request.form.get('notes')

        # Vérifier les ingrédients disponibles
        recipe = Recipe.query.get(recipe_id)
        missing_ingredients = []
        for ingredient in recipe.ingredients:
            product = Product.query.get(ingredient.product_id)
            required_quantity = (ingredient.quantity * planned_quantity) / recipe.yield_quantity
            if product.stock < required_quantity:
                missing_ingredients.append({
                    'name': product.name,
                    'required': required_quantity,
                    'available': product.stock
                })

        if missing_ingredients:
            flash('Ingrédients insuffisants pour cette production:', 'warning')
            for ingredient in missing_ingredients:
                flash(f"- {ingredient['name']}: {ingredient['required']} requis, {ingredient['available']} disponible", 'warning')
            return redirect(url_for('add_production_schedule'))

        schedule = ProductionSchedule(
            recipe_id=recipe_id,
            planned_quantity=planned_quantity,
            planned_start_time=planned_start_time,
            planned_end_time=planned_end_time,
            priority=priority,
            notes=notes,
            created_by=current_user.id
        )
        db.session.add(schedule)
        db.session.commit()
        flash('Production planifiée avec succès!')
        return redirect(url_for('production_schedule'))

    recipes = Recipe.query.all()
    return render_template('add_production_schedule.html', recipes=recipes)

@app.route('/production/schedule/<int:id>/start', methods=['POST'])
@login_required
def start_scheduled_production(id):
    schedule = ProductionSchedule.query.get_or_404(id)
    if schedule.status != 'scheduled':
        flash('Cette production a déjà été démarrée ou annulée', 'warning')
        return redirect(url_for('production_schedule'))

    production = ProductionRecord(
        recipe_id=schedule.recipe_id,
        quantity=schedule.planned_quantity,
        start_time=datetime.now(),
        notes=schedule.notes,
        user_id=current_user.id
    )
    db.session.add(production)
    schedule.status = 'in_progress'
    schedule.production_record = production
    db.session.commit()
    flash('Production démarrée avec succès!')
    return redirect(url_for('production_schedule'))

@app.route('/production/schedule/<int:id>/cancel', methods=['POST'])
@login_required
def cancel_scheduled_production(id):
    schedule = ProductionSchedule.query.get_or_404(id)
    if schedule.status != 'scheduled':
        flash('Cette production ne peut plus être annulée', 'warning')
        return redirect(url_for('production_schedule'))

    schedule.status = 'cancelled'
    db.session.commit()
    flash('Production annulée avec succès!')
    return redirect(url_for('production_schedule'))

# Route pour les rapports et statistiques
@app.route('/reports')
@login_required
@manager_required
def reports():
    # Période par défaut : 30 derniers jours
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    
    # Récupérer les ventes de la période
    current_sales = Sale.query.filter(
        Sale.date >= start_date,
        Sale.date <= end_date
    ).all()
    
    # Calculer les statistiques
    total_sales = sum(sale.total_amount for sale in current_sales)
    total_expenses = sum(expense.amount for expense in Expense.query.filter(
        Expense.date >= start_date,
        Expense.date <= end_date
    ).all())
    
    # Ventes par catégorie
    sales_by_category = db.session.query(
        Category.name,
        func.sum(SaleItem.quantity * SaleItem.unit_price).label('total')
    ).join(Product, Category.id == Product.category_id)\
     .join(SaleItem, Product.id == SaleItem.product_id)\
     .join(Sale, SaleItem.sale_id == Sale.id)\
     .filter(Sale.date >= start_date, Sale.date <= end_date)\
     .group_by(Category.name)\
     .all()
    
    # Produits les plus vendus
    top_products = db.session.query(
        Product.name,
        func.sum(SaleItem.quantity).label('total_quantity'),
        func.sum(SaleItem.quantity * SaleItem.unit_price).label('total_amount')
    ).join(SaleItem, Product.id == SaleItem.product_id)\
     .join(Sale, SaleItem.sale_id == Sale.id)\
     .filter(Sale.date >= start_date, Sale.date <= end_date)\
     .group_by(Product.name)\
     .order_by(func.sum(SaleItem.quantity * SaleItem.unit_price).desc())\
     .limit(5)\
     .all()
    
    # Produits en alerte de stock
    low_stock_products = Product.query.filter(
        Product.quantity <= Product.min_quantity
    ).all()
    
    # Produits en rupture de stock
    out_of_stock_products = Product.query.filter(
        Product.quantity == 0
    ).all()
    
    return render_template('reports.html',
                         start_date=start_date,
                         end_date=end_date,
                         total_sales=total_sales,
                         total_expenses=total_expenses,
                         sales_by_category=sales_by_category,
                         top_products=top_products,
                         low_stock_products=low_stock_products,
                         out_of_stock_products=out_of_stock_products)

@app.route('/reports/sales')
@login_required
@manager_required
def sales_report():
    # Logique des rapports de ventes
    return render_template('reports/sales.html')

@app.route('/reports/production')
@login_required
@manager_required
def production_report():
    # Logique des rapports de production
    return render_template('reports/production.html')

@app.route('/reports/profit')
@login_required
@manager_required
def profit_report():
    # Logique des rapports de bénéfices
    return render_template('reports/profit.html')

@app.route('/reports/export/pdf')
@login_required
@manager_required
def export_reports_pdf():
    # Période par défaut : 30 derniers jours
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    
    # Récupérer les ventes de la période
    current_sales = Sale.query.filter(
        Sale.date >= start_date,
        Sale.date <= end_date
    ).all()
    
    # Calculer les statistiques
    total_sales = sum(sale.total_amount for sale in current_sales)
    total_expenses = sum(expense.amount for expense in Expense.query.filter(
        Expense.date >= start_date,
        Expense.date <= end_date
    ).all())
    
    # Ventes par catégorie
    sales_by_category = db.session.query(
        Category.name,
        func.sum(SaleItem.quantity * SaleItem.unit_price).label('total')
    ).join(Product, Category.id == Product.category_id)\
     .join(SaleItem, Product.id == SaleItem.product_id)\
     .join(Sale, SaleItem.sale_id == Sale.id)\
     .filter(Sale.date >= start_date, Sale.date <= end_date)\
     .group_by(Category.name)\
     .all()
    
    # Produits les plus vendus
    top_products = db.session.query(
        Product.name,
        func.sum(SaleItem.quantity).label('total_quantity'),
        func.sum(SaleItem.quantity * SaleItem.unit_price).label('total_amount')
    ).join(SaleItem, Product.id == SaleItem.product_id)\
     .join(Sale, SaleItem.sale_id == Sale.id)\
     .filter(Sale.date >= start_date, Sale.date <= end_date)\
     .group_by(Product.name)\
     .order_by(desc('total_amount'))\
     .limit(5)\
     .all()
    
    # Produits en alerte de stock
    low_stock_products = Product.query.filter(
        Product.quantity <= Product.min_quantity
    ).all()
    
    # Produits en rupture de stock
    out_of_stock_products = Product.query.filter(
        Product.quantity == 0
    ).all()
    
    # Générer le HTML
    html = render_template('reports_pdf.html',
                         start_date=start_date,
                         end_date=end_date,
                         total_sales=total_sales,
                         total_expenses=total_expenses,
                         sales_by_category=sales_by_category,
                         top_products=top_products,
                         low_stock_products=low_stock_products,
                         out_of_stock_products=out_of_stock_products,
                         now=datetime.now())
    
    # Créer un fichier PDF temporaire
    with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp:
        HTML(string=html).write_pdf(tmp.name)
        tmp_path = tmp.name
    
    # Envoyer le fichier PDF
    return send_file(tmp_path,
                    as_attachment=True,
                    download_name=f'rapport_{start_date.strftime("%Y%m%d")}_{end_date.strftime("%Y%m%d")}.pdf',
                    mimetype='application/pdf')

@app.route('/settings')
@login_required
@manager_required
def settings():
    return render_template('settings.html')

if __name__ == '__main__':
    # Création du dossier database s'il n'existe pas
    if not os.path.exists('database'):
        os.makedirs('database')
    
    # Création des tables
    with app.app_context():
        db.create_all()
    
    app.run(debug=True) 