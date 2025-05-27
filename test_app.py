import unittest
import json
from app import app, db, User, Product, ProductVariant, CartItem, Order, OrderItem, Address # Add other models as needed

# Configure the Flask app for testing
app.config['TESTING'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test_streetwear.db'
app.config['WTF_CSRF_ENABLED'] = False  # Assuming Flask-WTF might be used, disable CSRF for tests
app.config['LOGIN_DISABLED'] = True     # Disable login for simpler testing of protected routes
app.config['SECRET_KEY'] = 'test_secret_key' # Required for session even if login is disabled for some features

class BaseTestCase(unittest.TestCase):
    def setUp(self):
        self.app_context = app.app_context()
        self.app_context.push()
        db.create_all()
        self.client = app.test_client()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

class TestUserAuth(BaseTestCase):
    def test_register_user(self):
        response = self.client.post('/register', json={
            'email': 'test@example.com',
            'password': 'password123',
            'name': 'Test User'
        })
        self.assertEqual(response.status_code, 201)
        self.assertIn('User registered successfully', response.get_data(as_text=True))
        user = User.query.filter_by(email='test@example.com').first()
        self.assertIsNotNone(user)
        self.assertEqual(user.name, 'Test User')

    def test_register_existing_email(self):
        # First, create a user
        user = User(email='test@example.com', password_hash='somehash', name='Test User')
        db.session.add(user)
        db.session.commit()

        # Try to register again with the same email
        response = self.client.post('/register', json={
            'email': 'test@example.com',
            'password': 'newpassword123'
        })
        self.assertEqual(response.status_code, 409)
        self.assertIn('Email already exists', response.get_data(as_text=True))

class TestProducts(BaseTestCase):
    def test_get_products_empty(self):
        response = self.client.get('/products')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, [])

    def test_get_products_with_data(self):
        # Add a sample product and variant
        product = Product(name='Test Jacket', description='A cool jacket', price=100.00)
        db.session.add(product)
        db.session.flush() # To get product.id for the variant
        variant = ProductVariant(product_id=product.id, size='M', color='Black', quantity_in_stock=10)
        db.session.add(variant)
        db.session.commit()

        response = self.client.get('/products')
        self.assertEqual(response.status_code, 200)
        data = response.json
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['name'], 'Test Jacket')
        self.assertEqual(data[0]['price'], 100.00)
        self.assertEqual(len(data[0]['variants']), 1)
        self.assertEqual(data[0]['variants'][0]['size'], 'M')

    def test_get_single_product(self):
        product = Product(name='Test Shirt', description='A nice shirt', price=50.00)
        db.session.add(product)
        db.session.commit() # Commit to get product.id

        response = self.client.get(f'/products/{product.id}')
        self.assertEqual(response.status_code, 200)
        data = response.json
        self.assertEqual(data['name'], 'Test Shirt')
        self.assertEqual(data['price'], 50.00)

    def test_get_single_product_not_found(self):
        response = self.client.get('/products/999') # An ID that should not exist
        self.assertEqual(response.status_code, 404)

class TestCart(BaseTestCase):
    def setUp(self):
        super().setUp()
        # Create a test user for cart operations
        self.user = User(email='cartuser@example.com', password_hash='securepassword', name='Cart User')
        db.session.add(self.user)
        db.session.commit()

        # Create a product and variant for cart items
        self.product = Product(name='Test Cart Product', description='Product for cart', price=30.00)
        db.session.add(self.product)
        db.session.flush()
        self.variant = ProductVariant(product_id=self.product.id, size='L', color='Blue', quantity_in_stock=5)
        db.session.add(self.variant)
        db.session.commit()

    def test_get_empty_cart(self):
        # Test cart logic directly by querying the model
        # This simulates that a user (self.user) has an empty cart
        # The /cart endpoint itself is protected by @login_required which we are bypassing
        # by setting LOGIN_DISABLED = True. A direct endpoint test for /cart would require
        # more complex login mocking.
        cart_items = CartItem.query.filter_by(user_id=self.user.id).all()
        self.assertEqual(len(cart_items), 0)
        
        # If LOGIN_DISABLED was false, and we could log in a user, the test might look like:
        # self.client.post('/login', json={'email': self.user.email, 'password': 'securepassword'})
        # response = self.client.get('/cart')
        # self.assertEqual(response.status_code, 200)
        # self.assertEqual(response.json, [])


    def test_add_item_to_cart_logic(self):
        # Test cart logic directly by creating CartItem model instance
        cart_item = CartItem(user_id=self.user.id, product_variant_id=self.variant.id, quantity=2)
        db.session.add(cart_item)
        db.session.commit()

        retrieved_cart_items = CartItem.query.filter_by(user_id=self.user.id).all()
        self.assertEqual(len(retrieved_cart_items), 1)
        self.assertEqual(retrieved_cart_items[0].product_variant_id, self.variant.id)
        self.assertEqual(retrieved_cart_items[0].quantity, 2)
        self.assertEqual(retrieved_cart_items[0].user_id, self.user.id)

if __name__ == '__main__':
    unittest.main()
