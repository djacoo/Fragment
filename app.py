from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///streetwear.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your_secret_key' # Replace with a strong secret key
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login' # Redirect to login page if user is not authenticated

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String, unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False) # Increased length for hash
    name = db.Column(db.String, nullable=True)
    phone = db.Column(db.String, nullable=True)
    default_address_id = db.Column(db.Integer, db.ForeignKey('address.id'), nullable=True)
    addresses = db.relationship('Address', backref='user', lazy=True)
    orders = db.relationship('Order', backref='user', lazy=True)
    cart_items = db.relationship('CartItem', backref='user', lazy=True)

class Address(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    full_name = db.Column(db.String, nullable=False)
    street_address = db.Column(db.String, nullable=False)
    city = db.Column(db.String, nullable=False)
    state = db.Column(db.String, nullable=False)
    zip_code = db.Column(db.String, nullable=False)
    country = db.Column(db.String, nullable=False, default='USA')
    is_default = db.Column(db.Boolean, default=False)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'full_name': self.full_name,
            'street_address': self.street_address,
            'city': self.city,
            'state': self.state,
            'zip_code': self.zip_code,
            'country': self.country,
            'is_default': self.is_default
        }

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    description = db.Column(db.Text, nullable=False)
    price = db.Column(db.Float, nullable=False)
    image_url = db.Column(db.String, nullable=True)
    material = db.Column(db.String, nullable=True)
    fit = db.Column(db.String, nullable=True)
    care_instructions = db.Column(db.Text, nullable=True)
    variants = db.relationship('ProductVariant', backref='product', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'price': self.price,
            'image_url': self.image_url,
            'material': self.material,
            'fit': self.fit,
            'care_instructions': self.care_instructions,
            'variants': [variant.to_dict() for variant in self.variants]
        }

class ProductVariant(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    size = db.Column(db.String, nullable=True)
    color = db.Column(db.String, nullable=True)
    quantity_in_stock = db.Column(db.Integer, nullable=False, default=0)
    __table_args__ = (db.UniqueConstraint('product_id', 'size', 'color', name='_product_size_color_uc'),)

    def to_dict(self):
        return {
            'id': self.id,
            'product_id': self.product_id,
            'size': self.size,
            'color': self.color,
            'quantity_in_stock': self.quantity_in_stock
        }

class CartItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    product_variant_id = db.Column(db.Integer, db.ForeignKey('product_variant.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    product_variant = db.relationship('ProductVariant')

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'product_variant_id': self.product_variant_id,
            'quantity': self.quantity,
            'product_variant': self.product_variant.to_dict() if self.product_variant else None
        }

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    order_date = db.Column(db.DateTime, nullable=False, default=datetime.datetime.utcnow)
    total_amount = db.Column(db.Float, nullable=False)
    shipping_address_id = db.Column(db.Integer, db.ForeignKey('address.id'), nullable=False)
    status = db.Column(db.String, nullable=False, default='Pending') # e.g., Pending, Shipped, Delivered, Cancelled
    shipping_address = db.relationship('Address')
    items = db.relationship('OrderItem', backref='order', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'order_date': self.order_date.isoformat() if self.order_date else None,
            'total_amount': self.total_amount,
            'status': self.status,
            'shipping_address_id': self.shipping_address_id,
            'shipping_address': self.shipping_address.to_dict() if self.shipping_address else None,
            'items': [item.to_dict() for item in self.items]
        }

class OrderItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    product_variant_id = db.Column(db.Integer, db.ForeignKey('product_variant.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price_at_purchase = db.Column(db.Float, nullable=False)
    product_variant = db.relationship('ProductVariant')

    def to_dict(self):
        return {
            'id': self.id,
            'order_id': self.order_id,
            'product_variant_id': self.product_variant_id,
            'quantity': self.quantity,
            'price_at_purchase': self.price_at_purchase,
            'product_variant': self.product_variant.to_dict() if self.product_variant else None
        }

class NewsletterSubscription(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String, unique=True, nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email
        }

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({'message': 'Email and password are required'}), 400

    if User.query.filter_by(email=data['email']).first():
        return jsonify({'message': 'Email already exists'}), 409

    hashed_password = generate_password_hash(data['password'], method='pbkdf2:sha256')
    new_user = User(
        email=data['email'],
        password_hash=hashed_password,
        name=data.get('name')
    )
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'message': 'User registered successfully'}), 201

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({'message': 'Email and password are required'}), 400

    user = User.query.filter_by(email=data['email']).first()

    if user and check_password_hash(user.password_hash, data['password']):
        login_user(user)
        return jsonify({'message': 'Logged in successfully', 'user': {'id': user.id, 'email': user.email, 'name': user.name}}), 200
    
    return jsonify({'message': 'Invalid email or password'}), 401

@app.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    return jsonify({'message': 'Logged out successfully'}), 200

@app.route('/account/profile', methods=['GET', 'POST'])
@login_required
def account_profile():
    if request.method == 'GET':
        return jsonify({
            'name': current_user.name,
            'email': current_user.email,
            'phone': current_user.phone
        }), 200
    elif request.method == 'POST':
        data = request.get_json()
        if not data:
            return jsonify({'message': 'No input data provided'}), 400

        # Validate email uniqueness if changed
        new_email = data.get('email')
        if new_email and new_email != current_user.email:
            if User.query.filter_by(email=new_email).first():
                return jsonify({'message': 'Email already exists'}), 409
            current_user.email = new_email
        
        if data.get('name'):
            current_user.name = data.get('name')
        if data.get('phone'):
            current_user.phone = data.get('phone')
        
        db.session.commit()
        return jsonify({'message': 'Profile updated successfully'}), 200

@app.route('/account/addresses', methods=['GET', 'POST'])
@login_required
def account_addresses():
    if request.method == 'GET':
        addresses = Address.query.filter_by(user_id=current_user.id).all()
        return jsonify([{
            'id': addr.id,
            'full_name': addr.full_name,
            'street_address': addr.street_address,
            'city': addr.city,
            'state': addr.state,
            'zip_code': addr.zip_code,
            'country': addr.country,
            'is_default': addr.is_default
        } for addr in addresses]), 200
    elif request.method == 'POST':
        data = request.get_json()
        if not data or not all(k in data for k in ['full_name', 'street_address', 'city', 'state', 'zip_code']):
            return jsonify({'message': 'Missing required address fields'}), 400

        if data.get('is_default'):
            Address.query.filter_by(user_id=current_user.id, is_default=True).update({'is_default': False})

        new_address = Address(
            user_id=current_user.id,
            full_name=data['full_name'],
            street_address=data['street_address'],
            city=data['city'],
            state=data['state'],
            zip_code=data['zip_code'],
            country=data.get('country', 'USA'),
            is_default=data.get('is_default', False)
        )
        db.session.add(new_address)
        db.session.commit()
        return jsonify({'message': 'Address added successfully', 'address_id': new_address.id}), 201

@app.route('/account/password', methods=['POST'])
@login_required
def account_password():
    data = request.get_json()
    if not data or not data.get('current_password') or not data.get('new_password'):
        return jsonify({'message': 'Current password and new password are required'}), 400

    if not check_password_hash(current_user.password_hash, data['current_password']):
        return jsonify({'message': 'Invalid current password'}), 401

    current_user.password_hash = generate_password_hash(data['new_password'], method='pbkdf2:sha256')
    db.session.commit()
    return jsonify({'message': 'Password updated successfully'}), 200

@app.route('/products', methods=['GET'])
def get_products():
    query = Product.query.join(ProductVariant) # Join to filter by variant attributes

    # Filtering
    name = request.args.get('name')
    if name:
        query = query.filter(Product.name.ilike(f'%{name}%'))
    
    min_price = request.args.get('min_price', type=float)
    if min_price is not None:
        query = query.filter(Product.price >= min_price)

    max_price = request.args.get('max_price', type=float)
    if max_price is not None:
        query = query.filter(Product.price <= max_price)

    size = request.args.get('size')
    if size:
        query = query.filter(ProductVariant.size == size)

    color = request.args.get('color')
    if color:
        query = query.filter(ProductVariant.color == color)

    # Sorting
    sort_by = request.args.get('sort_by')
    if sort_by:
        if sort_by == 'price_asc':
            query = query.order_by(Product.price.asc())
        elif sort_by == 'price_desc':
            query = query.order_by(Product.price.desc())
        elif sort_by == 'name_asc':
            query = query.order_by(Product.name.asc())
        elif sort_by == 'name_desc':
            query = query.order_by(Product.name.desc())
    
    # Ensure distinct products if joining with variants caused duplicates
    query = query.distinct()

    products = query.all()
    return jsonify([product.to_dict() for product in products]), 200

@app.route('/products/<int:product_id>', methods=['GET'])
def get_product(product_id):
    product = Product.query.get_or_404(product_id)
    return jsonify(product.to_dict()), 200

@app.route('/cart', methods=['GET'])
@login_required
def get_cart():
    cart_items = CartItem.query.filter_by(user_id=current_user.id).all()
    return jsonify([item.to_dict() for item in cart_items]), 200

@app.route('/cart/add', methods=['POST'])
@login_required
def add_to_cart():
    data = request.get_json()
    if not data or not data.get('product_variant_id') or not data.get('quantity'):
        return jsonify({'message': 'Product variant ID and quantity are required'}), 400

    product_variant_id = data['product_variant_id']
    quantity = data['quantity']

    if not isinstance(quantity, int) or quantity <= 0:
        return jsonify({'message': 'Quantity must be a positive integer'}), 400

    product_variant = ProductVariant.query.get(product_variant_id)
    if not product_variant:
        return jsonify({'message': 'Product variant not found'}), 404

    if product_variant.quantity_in_stock < quantity:
        return jsonify({'message': 'Not enough stock'}), 400

    cart_item = CartItem.query.filter_by(user_id=current_user.id, product_variant_id=product_variant_id).first()

    if cart_item:
        if product_variant.quantity_in_stock < cart_item.quantity + quantity:
             return jsonify({'message': 'Not enough stock to add to existing quantity in cart'}), 400
        cart_item.quantity += quantity
    else:
        cart_item = CartItem(
            user_id=current_user.id,
            product_variant_id=product_variant_id,
            quantity=quantity
        )
        db.session.add(cart_item)
    
    db.session.commit()
    return jsonify(cart_item.to_dict()), 201 # 201 for created, could be 200 if only updated

@app.route('/cart/update/<int:item_id>', methods=['POST'])
@login_required
def update_cart_item(item_id):
    data = request.get_json()
    if not data or not data.get('quantity'):
        return jsonify({'message': 'Quantity is required'}), 400

    quantity = data['quantity']
    if not isinstance(quantity, int) or quantity <= 0:
        return jsonify({'message': 'Quantity must be a positive integer'}), 400

    cart_item = CartItem.query.get(item_id)
    if not cart_item:
        return jsonify({'message': 'Cart item not found'}), 404
    
    if cart_item.user_id != current_user.id:
        return jsonify({'message': 'Unauthorized to update this cart item'}), 403

    product_variant = ProductVariant.query.get(cart_item.product_variant_id)
    if not product_variant: # Should ideally not happen if DB is consistent
        return jsonify({'message': 'Product variant not found for this cart item'}), 500 

    if product_variant.quantity_in_stock < quantity:
        return jsonify({'message': 'Not enough stock'}), 400

    cart_item.quantity = quantity
    db.session.commit()
    return jsonify(cart_item.to_dict()), 200

@app.route('/cart/remove/<int:item_id>', methods=['POST'])
@login_required
def remove_from_cart(item_id):
    cart_item = CartItem.query.get(item_id)
    if not cart_item:
        return jsonify({'message': 'Cart item not found'}), 404
    
    if cart_item.user_id != current_user.id:
        return jsonify({'message': 'Unauthorized to remove this cart item'}), 403

    db.session.delete(cart_item)
    db.session.commit()
    return jsonify({'message': 'Cart item removed successfully'}), 200

@app.route('/orders/create', methods=['POST'])
@login_required
def create_order():
    data = request.get_json()
    if not data or not data.get('shipping_address_id'):
        return jsonify({'message': 'Shipping address ID is required'}), 400

    shipping_address_id = data['shipping_address_id']
    address = Address.query.filter_by(id=shipping_address_id, user_id=current_user.id).first()
    if not address:
        return jsonify({'message': 'Shipping address not found or does not belong to user'}), 404 # Or 403

    cart_items = CartItem.query.filter_by(user_id=current_user.id).all()
    if not cart_items:
        return jsonify({'message': 'Cannot create order with an empty cart'}), 400

    total_amount = 0
    order_items_to_create = [] # Temporary list to hold items before committing

    try:
        # First pass: Calculate total and check stock for all items
        for cart_item in cart_items:
            product_variant = ProductVariant.query.get(cart_item.product_variant_id)
            if not product_variant: # Should not happen if DB is consistent
                db.session.rollback()
                return jsonify({'message': f'Product variant for item ID {cart_item.product_variant_id} not found.'}), 500
            
            if product_variant.quantity_in_stock < cart_item.quantity:
                db.session.rollback() # Not strictly necessary here as no changes made yet, but good practice
                return jsonify({'message': f'Not enough stock for item {product_variant.product.name} (Variant ID: {product_variant.id})'}), 400
            
            total_amount += cart_item.quantity * product_variant.price # Assuming ProductVariant has price
            # Store details for OrderItem creation
            order_items_to_create.append({
                'product_variant_id': cart_item.product_variant_id,
                'quantity': cart_item.quantity,
                'price_at_purchase': product_variant.price # Store current price
            })

        # Create Order
        new_order = Order(
            user_id=current_user.id,
            shipping_address_id=shipping_address_id,
            total_amount=total_amount,
            status='Pending'
        )
        db.session.add(new_order)
        # Flush to get new_order.id for OrderItems if needed, or add OrderItems directly to new_order.items
        # and they will be associated when session is committed.

        # Second pass: Create OrderItems and update stock
        for item_data in order_items_to_create:
            product_variant = ProductVariant.query.get(item_data['product_variant_id']) # Re-fetch for safety or pass object
            
            # Re-check stock (important for concurrent requests, though less critical in this single transaction)
            if product_variant.quantity_in_stock < item_data['quantity']:
                 db.session.rollback()
                 return jsonify({'message': f'Stock changed for {product_variant.product.name} (Variant ID: {product_variant.id}) during order processing. Please try again.'}), 400

            order_item = OrderItem(
                order=new_order, # Associate with the new order
                product_variant_id=item_data['product_variant_id'],
                quantity=item_data['quantity'],
                price_at_purchase=item_data['price_at_purchase']
            )
            db.session.add(order_item)
            product_variant.quantity_in_stock -= item_data['quantity']
            db.session.add(product_variant) # Mark for update

        # Clear cart
        CartItem.query.filter_by(user_id=current_user.id).delete()
        
        db.session.commit()
        return jsonify(new_order.to_dict()), 201

    except Exception as e:
        db.session.rollback()
        # Log the exception e
        return jsonify({'message': 'An error occurred while creating the order.'}), 500

@app.route('/account/orders', methods=['GET'])
@login_required
def get_user_orders():
    orders = Order.query.filter_by(user_id=current_user.id).order_by(Order.order_date.desc()).all()
    return jsonify([order.to_dict() for order in orders]), 200

@app.route('/account/orders/<int:order_id>', methods=['GET'])
@login_required
def get_user_order(order_id):
    order = Order.query.get_or_404(order_id)
    if order.user_id != current_user.id:
        return jsonify({'message': 'Order not found or you do not have permission to view it'}), 404 # Or 403
    return jsonify(order.to_dict()), 200

@app.route('/subscribe', methods=['POST'])
def subscribe_newsletter():
    data = request.get_json()
    if not data or not data.get('email'):
        return jsonify({'message': 'Email is required'}), 400

    email = data['email']
    # Basic email validation
    if '@' not in email or '.' not in email.split('@')[-1]:
        return jsonify({'message': 'Invalid email format'}), 400

    existing_subscription = NewsletterSubscription.query.filter_by(email=email).first()
    if existing_subscription:
        return jsonify({'message': 'Email already subscribed', 'subscription': existing_subscription.to_dict()}), 200 # Or 409

    new_subscription = NewsletterSubscription(email=email)
    try:
        db.session.add(new_subscription)
        db.session.commit()
        return jsonify({'message': 'Successfully subscribed to newsletter', 'subscription': new_subscription.to_dict()}), 201
    except Exception as e:
        db.session.rollback()
        # Log the exception e
        return jsonify({'message': 'An error occurred while subscribing.'}), 500

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
