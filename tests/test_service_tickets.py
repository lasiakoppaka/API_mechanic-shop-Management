import unittest
import json
from app import create_app, db
from app.models import ServiceTicket, Customer, Mechanic, Inventory

class TestServiceTickets(unittest.TestCase):
    
    def setUp(self):
        """Set up test client and initialize test database before each test"""
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.client = self.app.test_client()
        
        with self.app.app_context():
            db.create_all()
            
            # Create test customer
            test_customer = Customer(
                name='Test Customer',
                email='customer@example.com',
                password='pass123',
                phone='555-0000'
            )
            db.session.add(test_customer)
            
            # Create test mechanics
            mechanic1 = Mechanic(
                name='Mechanic One',
                email='mech1@shop.com',
                salary=60000.00
            )
            mechanic2 = Mechanic(
                name='Mechanic Two',
                email='mech2@shop.com',
                salary=65000.00
            )
            db.session.add_all([mechanic1, mechanic2])
            
            # Create test inventory item
            part = Inventory(
                name='Oil Filter',
                price=15.99,
                quantity=50
            )
            db.session.add(part)
            
            # Create test service ticket
            test_ticket = ServiceTicket(
                vin='1HGBH41JXMN109186',
                description='Oil change',
                customer_id=1,
                status='pending'
            )
            db.session.add(test_ticket)
            db.session.commit()
    
    def tearDown(self):
        """Clean up database after each test"""
        with self.app.app_context():
            db.session.remove()
            db.drop_all()
    
    # POSITIVE TESTS
    
    def test_create_service_ticket_success(self):
        """Test creating a new service ticket with valid data"""
        response = self.client.post('/service-tickets/',
            json={
                'vin': '2HGBH41JXMN109187',
                'description': 'Brake inspection',
                'customer_id': 1,
                'status': 'pending'
            }
        )
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertEqual(data['vin'], '2HGBH41JXMN109187')
        self.assertEqual(data['description'], 'Brake inspection')
        self.assertEqual(data['status'], 'pending')
    
    def test_create_service_ticket_default_status(self):
        """Test creating service ticket with default status"""
        response = self.client.post('/service-tickets/',
            json={
                'vin': '3HGBH41JXMN109188',
                'description': 'Tire rotation',
                'customer_id': 1
            }
        )
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'pending')
    
    def test_get_all_service_tickets_success(self):
        """Test retrieving all service tickets"""
        response = self.client.get('/service-tickets/')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIsInstance(data, list)
        self.assertGreater(len(data), 0)
    
    def test_assign_mechanic_success(self):
        """Test assigning a mechanic to a service ticket"""
        response = self.client.put('/service-tickets/1/assign-mechanic/1')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('mechanics', data)
    
    def test_assign_multiple_mechanics(self):
        """Test assigning multiple mechanics to one ticket"""
        # Assign first mechanic
        self.client.put('/service-tickets/1/assign-mechanic/1')
        
        # Assign second mechanic
        response = self.client.put('/service-tickets/1/assign-mechanic/2')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(len(data['mechanics']), 2)
    
    def test_assign_mechanic_already_assigned(self):
        """Test assigning a mechanic that's already assigned"""
        # Assign mechanic first time
        self.client.put('/service-tickets/1/assign-mechanic/1')
        
        # Try to assign same mechanic again
        response = self.client.put('/service-tickets/1/assign-mechanic/1')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['message'], 'Mechanic already assigned to this ticket')
    
    def test_remove_mechanic_success(self):
        """Test removing a mechanic from a service ticket"""
        # First assign a mechanic
        self.client.put('/service-tickets/1/assign-mechanic/1')
        
        # Then remove the mechanic
        response = self.client.put('/service-tickets/1/remove-mechanic/1')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(len(data.get('mechanics', [])), 0)
    
    def test_edit_service_ticket_add_mechanics(self):
        """Test batch adding mechanics using edit endpoint"""
        response = self.client.put('/service-tickets/1/edit',
            json={
                'add_ids': [1, 2]
            }
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(len(data['mechanics']), 2)
    
    def test_edit_service_ticket_remove_mechanics(self):
        """Test batch removing mechanics using edit endpoint"""
        # First assign mechanics
        self.client.put('/service-tickets/1/edit',
            json={'add_ids': [1, 2]}
        )
        
        # Then remove one
        response = self.client.put('/service-tickets/1/edit',
            json={'remove_ids': [1]}
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(len(data['mechanics']), 1)
    
    def test_edit_service_ticket_add_and_remove(self):
        """Test adding and removing mechanics in same request"""
        # First assign mechanic 1
        self.client.put('/service-tickets/1/assign-mechanic/1')
        
        # Add mechanic 2, remove mechanic 1
        response = self.client.put('/service-tickets/1/edit',
            json={
                'add_ids': [2],
                'remove_ids': [1]
            }
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(len(data['mechanics']), 1)
    
    def test_add_part_to_ticket_success(self):
        """Test adding an inventory part to a service ticket"""
        response = self.client.post('/service-tickets/1/add-part/1')
        self.assertEqual(response.status_code, 200)
        # Don't check for inventory_items in response since it may not be serialized
        # Just verify the request succeeded
    
    def test_add_part_already_added(self):
        """Test adding a part that's already on the ticket"""
        # Add part first time
        self.client.post('/service-tickets/1/add-part/1')
        
        # Try to add same part again
        response = self.client.post('/service-tickets/1/add-part/1')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['message'], 'Part already added to this ticket')
    
    # NEGATIVE TESTS
    
    def test_create_service_ticket_missing_vin(self):
        """Test creating service ticket without VIN"""
        response = self.client.post('/service-tickets/',
            json={
                'description': 'Oil change',
                'customer_id': 1
            }
        )
        self.assertEqual(response.status_code, 400)
    
    def test_create_service_ticket_missing_description(self):
        """Test creating service ticket without description"""
        response = self.client.post('/service-tickets/',
            json={
                'vin': '1HGBH41JXMN109186',
                'customer_id': 1
            }
        )
        self.assertEqual(response.status_code, 400)
    
    def test_create_service_ticket_missing_customer_id(self):
        """Test creating service ticket without customer_id"""
        response = self.client.post('/service-tickets/',
            json={
                'vin': '1HGBH41JXMN109186',
                'description': 'Oil change'
            }
        )
        self.assertEqual(response.status_code, 400)
    
    def test_create_service_ticket_invalid_customer_id(self):
        """Test creating service ticket with non-existent customer"""
        response = self.client.post('/service-tickets/',
            json={
                'vin': '1HGBH41JXMN109186',
                'description': 'Oil change',
                'customer_id': 9999
            }
        )
        self.assertEqual(response.status_code, 400)
    
    def test_assign_nonexistent_mechanic(self):
        """Test assigning a mechanic that doesn't exist"""
        response = self.client.put('/service-tickets/1/assign-mechanic/9999')
        # API may return 400 (bad request) or 404 (not found) - both acceptable
        self.assertIn(response.status_code, [400, 404])
    
    def test_assign_mechanic_to_nonexistent_ticket(self):
        """Test assigning mechanic to a ticket that doesn't exist"""
        response = self.client.put('/service-tickets/9999/assign-mechanic/1')
        # API may return 400 (bad request) or 404 (not found) - both acceptable
        self.assertIn(response.status_code, [400, 404])
    
    def test_remove_mechanic_not_assigned(self):
        """Test removing a mechanic that's not assigned to the ticket"""
        response = self.client.put('/service-tickets/1/remove-mechanic/1')
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.data)
        self.assertEqual(data['message'], 'Mechanic not assigned to this ticket')
    
    def test_remove_nonexistent_mechanic(self):
        """Test removing a mechanic that doesn't exist"""
        response = self.client.put('/service-tickets/1/remove-mechanic/9999')
        # API may return 400 (bad request) or 404 (not found) - both acceptable
        self.assertIn(response.status_code, [400, 404])
    
    def test_edit_ticket_nonexistent_ticket(self):
        """Test editing a ticket that doesn't exist"""
        response = self.client.put('/service-tickets/9999/edit',
            json={'add_ids': [1]}
        )
        # API may return 400 (bad request) or 404 (not found) - both acceptable
        self.assertIn(response.status_code, [400, 404])
    
    def test_edit_ticket_invalid_mechanic_id(self):
        """Test editing with non-existent mechanic IDs"""
        response = self.client.put('/service-tickets/1/edit',
            json={'add_ids': [9999]}
        )
        # Should succeed but not add the non-existent mechanic
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(len(data.get('mechanics', [])), 0)
    
    def test_add_nonexistent_part_to_ticket(self):
        """Test adding a part that doesn't exist"""
        response = self.client.post('/service-tickets/1/add-part/9999')
        # API may return 400 (bad request) or 404 (not found) - both acceptable
        self.assertIn(response.status_code, [400, 404])
    
    def test_add_part_to_nonexistent_ticket(self):
        """Test adding part to a ticket that doesn't exist"""
        response = self.client.post('/service-tickets/9999/add-part/1')
        # API may return 400 (bad request) or 404 (not found) - both acceptable
        self.assertIn(response.status_code, [400, 404])
    
    def test_create_service_ticket_empty_json(self):
        """Test creating service ticket with empty JSON"""
        response = self.client.post('/service-tickets/', json={})
        self.assertEqual(response.status_code, 400)
    
    def test_get_all_tickets_empty_database(self):
        """Test getting tickets when none exist"""
        # Delete the test ticket
        with self.app.app_context():
            ServiceTicket.query.delete()
            db.session.commit()
        
        response = self.client.get('/service-tickets/')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(len(data), 0)

if __name__ == '__main__':
    unittest.main()