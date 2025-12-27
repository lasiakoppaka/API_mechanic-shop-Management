import unittest
import json
from app import create_app, db
from app.models import Mechanic

class TestMechanics(unittest.TestCase):
    
    def setUp(self):
        """Set up test client and initialize test database before each test"""
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.client = self.app.test_client()
        
        with self.app.app_context():
            db.create_all()
            
            # Create test mechanic
            test_mechanic = Mechanic(
                name='Test Mechanic',
                email='mechanic@example.com',
                phone='555-1111',
                address='789 Garage St',
                salary=55000.00
            )
            db.session.add(test_mechanic)
            db.session.commit()
    
    def tearDown(self):
        """Clean up database after each test"""
        with self.app.app_context():
            db.session.remove()
            db.drop_all()
    
    # POSITIVE TESTS
    
    def test_create_mechanic_success(self):
        """Test creating a new mechanic with valid data"""
        response = self.client.post('/mechanics/',
            json={
                'name': 'Jane Smith',
                'email': 'jane@mechanicshop.com',
                'phone': '555-2222',
                'address': '456 Workshop Ave',
                'salary': 65000.00
            }
        )
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertEqual(data['name'], 'Jane Smith')
        self.assertEqual(data['email'], 'jane@mechanicshop.com')
        self.assertEqual(data['salary'], 65000.00)
    
    def test_create_mechanic_minimal_data(self):
        """Test creating mechanic with only required fields"""
        response = self.client.post('/mechanics/',
            json={
                'name': 'Bob Jones',
                'email': 'bob@mechanicshop.com'
            }
        )
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertEqual(data['name'], 'Bob Jones')
        self.assertIsNone(data.get('phone'))
    
    def test_get_all_mechanics_success(self):
        """Test retrieving all mechanics"""
        response = self.client.get('/mechanics/')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIsInstance(data, list)
        self.assertGreater(len(data), 0)
    
    def test_update_mechanic_success(self):
        """Test updating mechanic information"""
        response = self.client.put('/mechanics/1',
            json={
                'name': 'Updated Mechanic',
                'salary': 70000.00
            }
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['name'], 'Updated Mechanic')
        self.assertEqual(data['salary'], 70000.00)
    
    def test_update_mechanic_partial(self):
        """Test updating only some fields of a mechanic"""
        response = self.client.put('/mechanics/1',
            json={'phone': '555-9999'}
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['phone'], '555-9999')
        self.assertEqual(data['name'], 'Test Mechanic')  # Name unchanged
    
    def test_delete_mechanic_success(self):
        """Test deleting a mechanic"""
        response = self.client.delete('/mechanics/1')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['message'], 'Mechanic deleted successfully')
    
        # Verify mechanic is actually deleted by checking the list
        get_all_response = self.client.get('/mechanics/')
        data = json.loads(get_all_response.data)
        mechanic_ids = [m['mechanic_id'] for m in data]
        self.assertNotIn(1, mechanic_ids)
    
    def test_get_mechanics_by_tickets_success(self):
        """Test retrieving mechanics sorted by tickets worked"""
        response = self.client.get('/mechanics/by-tickets')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIsInstance(data, list)
        
        # Verify each mechanic has tickets_worked field
        if len(data) > 0:
            self.assertIn('tickets_worked', data[0])
    
    def test_get_mechanics_by_tickets_ordering(self):
        """Test that mechanics are ordered by ticket count (descending)"""
        # Create multiple mechanics
        with self.app.app_context():
            mechanic2 = Mechanic(name='Mechanic 2', email='m2@shop.com')
            mechanic3 = Mechanic(name='Mechanic 3', email='m3@shop.com')
            db.session.add_all([mechanic2, mechanic3])
            db.session.commit()
        
        response = self.client.get('/mechanics/by-tickets')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        
        # Verify ordering (higher or equal ticket counts come first)
        for i in range(len(data) - 1):
            self.assertGreaterEqual(
                data[i]['tickets_worked'],
                data[i + 1]['tickets_worked']
            )
    
    # NEGATIVE TESTS
    
    def test_create_mechanic_missing_name(self):
        """Test creating mechanic without required name field"""
        response = self.client.post('/mechanics/',
            json={
                'email': 'noemail@example.com',
                'salary': 50000.00
            }
        )
        self.assertEqual(response.status_code, 400)
    
    def test_create_mechanic_missing_email(self):
        """Test creating mechanic without required email field"""
        response = self.client.post('/mechanics/',
            json={
                'name': 'No Email Guy',
                'salary': 50000.00
            }
        )
        self.assertEqual(response.status_code, 400)
    
    def test_create_mechanic_invalid_salary(self):
        """Test creating mechanic with invalid salary type"""
        response = self.client.post('/mechanics/',
            json={
                'name': 'Bad Salary',
                'email': 'bad@example.com',
                'salary': 'not-a-number'
            }
        )
        self.assertEqual(response.status_code, 400)
    
    def test_update_nonexistent_mechanic(self):
        """Test updating a mechanic that doesn't exist"""
        response = self.client.put('/mechanics/9999',
            json={'name': 'Ghost Mechanic'}
        )
        self.assertEqual(response.status_code, 404)
    
    def test_delete_nonexistent_mechanic(self):
        """Test deleting a mechanic that doesn't exist"""
        response = self.client.delete('/mechanics/9999')
        self.assertEqual(response.status_code, 404)
    
    def test_create_mechanic_empty_request(self):
        """Test creating mechanic with empty JSON"""
        response = self.client.post('/mechanics/', json={})
        self.assertEqual(response.status_code, 400)
    
    def test_update_mechanic_invalid_data(self):
        """Test updating mechanic with invalid data type"""
        response = self.client.put('/mechanics/1',
            json={'salary': 'invalid-salary'}
        )
        self.assertEqual(response.status_code, 400)
    
    def test_create_mechanic_duplicate_email(self):
        """Test creating mechanic with duplicate email"""
        # Create first mechanic
        self.client.post('/mechanics/',
            json={
                'name': 'First Mechanic',
                'email': 'duplicate@shop.com'
            }
        )
        
        # Try to create second mechanic with same email
        response = self.client.post('/mechanics/',
            json={
                'name': 'Second Mechanic',
                'email': 'duplicate@shop.com'
            }
        )
        self.assertEqual(response.status_code, 400)
    
    def test_get_all_mechanics_empty_database(self):
        """Test getting mechanics when none exist"""
        # Delete the test mechanic
        self.client.delete('/mechanics/1')
        
        response = self.client.get('/mechanics/')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(len(data), 0)

if __name__ == '__main__':
    unittest.main()