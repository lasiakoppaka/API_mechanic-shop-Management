import unittest
import json
from app import create_app, db
from app.models import Customer

class TestCustomers(unittest.TestCase):
    
    def setUp(self):
        """Set up test client and initialize test database before each test"""
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'  # In-memory test database
        self.client = self.app.test_client()
        
        with self.app.app_context():
            db.create_all()
            
            # Create test customer for login tests
            test_customer = Customer(
                name='Test User',
                email='test@example.com',
                password='testpass123',
                phone='555-0000',
                address='123 Test St'
            )
            db.session.add(test_customer)
            db.session.commit()
    
    def tearDown(self):
        """Clean up database after each test"""
        with self.app.app_context():
            db.session.remove()
            db.drop_all()
    
    # POSITIVE TESTS
    
    def test_create_customer_success(self):
        """Test creating a new customer with valid data"""
        response = self.client.post('/customers/', 
            json={
                'name': 'John Doe',
                'email': 'john@example.com',
                'password': 'password123',
                'phone': '555-1234',
                'address': '456 Main St'
            }
        )
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertEqual(data['name'], 'John Doe')
        self.assertEqual(data['email'], 'john@example.com')
    
    def test_get_all_customers_success(self):
        """Test retrieving all customers"""
        response = self.client.get('/customers/')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('customers', data)
        self.assertIn('pagination', data)
    
    def test_get_single_customer_success(self):
        """Test retrieving a specific customer by ID"""
        response = self.client.get('/customers/1')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['email'], 'test@example.com')
    
    def test_login_success(self):
        """Test customer login with valid credentials"""
        response = self.client.post('/customers/login',
            json={
                'email': 'test@example.com',
                'password': 'testpass123'
            }
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('token', data)
        self.assertIn('customer_id', data)
        self.assertEqual(data['message'], 'Login successful')
    
    def test_update_customer_success(self):
        """Test updating customer information with valid token"""
        # First login to get token
        login_response = self.client.post('/customers/login',
            json={
                'email': 'test@example.com',
                'password': 'testpass123'
            }
        )
        token = json.loads(login_response.data)['token']
        
        # Update customer
        response = self.client.put('/customers/1',
            headers={'Authorization': f'Bearer {token}'},
            json={
                'name': 'Updated Name',
                'phone': '555-9999'
            }
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['name'], 'Updated Name')
    
    def test_delete_customer_success(self):
        """Test deleting a customer with valid token"""
        # First login to get token
        login_response = self.client.post('/customers/login',
            json={
                'email': 'test@example.com',
                'password': 'testpass123'
            }
        )
        token = json.loads(login_response.data)['token']
        
        # Delete customer
        response = self.client.delete('/customers/1',
            headers={'Authorization': f'Bearer {token}'}
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['message'], 'Customer deleted successfully')
    
    def test_pagination_success(self):
        """Test pagination with custom page and per_page parameters"""
        response = self.client.get('/customers/?page=1&per_page=5')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['pagination']['page'], 1)
        self.assertEqual(data['pagination']['per_page'], 5)
    
    # NEGATIVE TESTS
    
    def test_create_customer_missing_required_field(self):
        """Test creating customer without required email field"""
        response = self.client.post('/customers/',
            json={
                'name': 'John Doe',
                'password': 'password123'
                # Missing email
            }
        )
        self.assertEqual(response.status_code, 400)
    
    def test_get_nonexistent_customer(self):
        """Test retrieving a customer that doesn't exist"""
        response = self.client.get('/customers/9999')
        self.assertEqual(response.status_code, 404)
    
    def test_login_invalid_credentials(self):
        """Test login with incorrect password"""
        response = self.client.post('/customers/login',
            json={
                'email': 'test@example.com',
                'password': 'wrongpassword'
            }
        )
        self.assertEqual(response.status_code, 401)
        data = json.loads(response.data)
        self.assertEqual(data['message'], 'Invalid email or password')
    
    def test_login_nonexistent_email(self):
        """Test login with email that doesn't exist"""
        response = self.client.post('/customers/login',
            json={
                'email': 'nonexistent@example.com',
                'password': 'password123'
            }
        )
        self.assertEqual(response.status_code, 401)
    
    def test_update_customer_without_token(self):
        """Test updating customer without authentication token"""
        response = self.client.put('/customers/1',
            json={'name': 'Updated Name'}
        )
        self.assertEqual(response.status_code, 401)
    
    def test_update_customer_wrong_id(self):
        """Test updating a different customer's information (should be forbidden)"""
        # Login as customer 1
        login_response = self.client.post('/customers/login',
            json={
                'email': 'test@example.com',
                'password': 'testpass123'
            }
        )
        token = json.loads(login_response.data)['token']
        
        # Try to update customer 2
        response = self.client.put('/customers/2',
            headers={'Authorization': f'Bearer {token}'},
            json={'name': 'Hacked Name'}
        )
        # Should return 403 Forbidden or 404 Not Found
        self.assertIn(response.status_code, [403, 404])
    
    def test_delete_customer_without_token(self):
        """Test deleting customer without authentication token"""
        response = self.client.delete('/customers/1')
        self.assertEqual(response.status_code, 401)
    
    def test_create_customer_duplicate_email(self):
        """Test creating customer with duplicate email (if unique constraint exists)"""
        # Create first customer
        self.client.post('/customers/',
            json={
                'name': 'First User',
                'email': 'duplicate@example.com',
                'password': 'pass123'
            }
        )
        
        # Try to create second customer with same email
        response = self.client.post('/customers/',
            json={
                'name': 'Second User',
                'email': 'duplicate@example.com',
                'password': 'pass456'
            }
        )
        self.assertEqual(response.status_code, 400)

if __name__ == '__main__':
    unittest.main()