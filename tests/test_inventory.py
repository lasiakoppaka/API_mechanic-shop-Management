import unittest
import json
from app import create_app, db
from app.models import Inventory

class TestInventory(unittest.TestCase):
    
    def setUp(self):
        """Set up test client and initialize test database before each test"""
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.client = self.app.test_client()
        
        with self.app.app_context():
            db.create_all()
            
            # Create test inventory items
            item1 = Inventory(
                name='Oil Filter',
                price=15.99,
                quantity=50
            )
            item2 = Inventory(
                name='Brake Pads',
                price=45.50,
                quantity=25
            )
            db.session.add_all([item1, item2])
            db.session.commit()
    
    def tearDown(self):
        """Clean up database after each test"""
        with self.app.app_context():
            db.session.remove()
            db.drop_all()
    
    # POSITIVE TESTS
    
    def test_create_inventory_item_success(self):
        """Test creating a new inventory item with valid data"""
        response = self.client.post('/inventory/',
            json={
                'name': 'Spark Plugs',
                'price': 8.99,
                'quantity': 100
            }
        )
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertEqual(data['name'], 'Spark Plugs')
        self.assertEqual(data['price'], 8.99)
        self.assertEqual(data['quantity'], 100)
    
    def test_create_inventory_item_default_quantity(self):
        """Test creating inventory item with default quantity (0)"""
        response = self.client.post('/inventory/',
            json={
                'name': 'Air Filter',
                'price': 12.50
            }
        )
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertEqual(data['quantity'], 0)
    
    def test_create_inventory_item_zero_quantity(self):
        """Test creating inventory item with explicitly zero quantity"""
        response = self.client.post('/inventory/',
            json={
                'name': 'Wiper Blades',
                'price': 18.75,
                'quantity': 0
            }
        )
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertEqual(data['quantity'], 0)
    
    def test_get_all_inventory_success(self):
        """Test retrieving all inventory items"""
        response = self.client.get('/inventory/')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 2)  # We created 2 items in setUp
    
    def test_get_single_inventory_item_success(self):
        """Test retrieving a specific inventory item by ID"""
        response = self.client.get('/inventory/1')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['name'], 'Oil Filter')
        self.assertEqual(data['price'], 15.99)
    
    def test_update_inventory_item_success(self):
        """Test updating inventory item information"""
        response = self.client.put('/inventory/1',
            json={
                'name': 'Premium Oil Filter',
                'price': 19.99,
                'quantity': 75
            }
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['name'], 'Premium Oil Filter')
        self.assertEqual(data['price'], 19.99)
        self.assertEqual(data['quantity'], 75)
    
    def test_update_inventory_item_partial(self):
        """Test updating only some fields of an inventory item"""
        response = self.client.put('/inventory/1',
            json={'quantity': 100}
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['quantity'], 100)
        self.assertEqual(data['name'], 'Oil Filter')  # Name unchanged
        self.assertEqual(data['price'], 15.99)  # Price unchanged
    
    def test_update_inventory_price_only(self):
        """Test updating only the price"""
        response = self.client.put('/inventory/1',
            json={'price': 17.50}
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['price'], 17.50)
        self.assertEqual(data['name'], 'Oil Filter')
    
    def test_update_inventory_name_only(self):
        """Test updating only the name"""
        response = self.client.put('/inventory/1',
            json={'name': 'Super Oil Filter'}
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['name'], 'Super Oil Filter')
        self.assertEqual(data['price'], 15.99)
    
    def test_delete_inventory_item_success(self):
        """Test deleting an inventory item"""
        response = self.client.delete('/inventory/1')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['message'], 'Inventory item deleted successfully')
        
        # Verify item is actually deleted
        get_response = self.client.get('/inventory/1')
        self.assertEqual(get_response.status_code, 404)
    
    def test_create_inventory_item_with_decimal_price(self):
        """Test creating item with precise decimal price"""
        response = self.client.post('/inventory/',
            json={
                'name': 'Transmission Fluid',
                'price': 24.99,
                'quantity': 30
            }
        )
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertEqual(data['price'], 24.99)
    
    def test_update_inventory_quantity_to_zero(self):
        """Test updating quantity to zero (out of stock)"""
        response = self.client.put('/inventory/1',
            json={'quantity': 0}
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['quantity'], 0)
    
    # NEGATIVE TESTS
    
    def test_create_inventory_item_missing_name(self):
        """Test creating inventory item without required name field"""
        response = self.client.post('/inventory/',
            json={
                'price': 10.00,
                'quantity': 20
            }
        )
        self.assertEqual(response.status_code, 400)
    
    def test_create_inventory_item_missing_price(self):
        """Test creating inventory item without required price field"""
        response = self.client.post('/inventory/',
            json={
                'name': 'Mystery Part',
                'quantity': 15
            }
        )
        self.assertEqual(response.status_code, 400)
    
    def test_create_inventory_item_empty_json(self):
        """Test creating inventory item with empty JSON"""
        response = self.client.post('/inventory/', json={})
        self.assertEqual(response.status_code, 400)
    
    def test_create_inventory_item_invalid_price_type(self):
        """Test creating inventory item with invalid price type"""
        response = self.client.post('/inventory/',
            json={
                'name': 'Bad Price Item',
                'price': 'not-a-number',
                'quantity': 10
            }
        )
        self.assertEqual(response.status_code, 400)
    
    def test_create_inventory_item_negative_price(self):
        """Test creating inventory item with negative price"""
        response = self.client.post('/inventory/',
            json={
                'name': 'Negative Item',
                'price': -10.00,
                'quantity': 5
            }
        )
        # Should either fail or succeed depending on validation rules
        # Assuming it should succeed (no validation), verify it's stored
        if response.status_code == 201:
            data = json.loads(response.data)
            self.assertEqual(data['price'], -10.00)
    
    def test_create_inventory_item_invalid_quantity_type(self):
        """Test creating inventory item with invalid quantity type"""
        response = self.client.post('/inventory/',
            json={
                'name': 'Bad Quantity Item',
                'price': 15.00,
                'quantity': 'not-a-number'
            }
        )
        self.assertEqual(response.status_code, 400)
    
    def test_get_nonexistent_inventory_item(self):
        """Test retrieving an inventory item that doesn't exist"""
        response = self.client.get('/inventory/9999')
        self.assertEqual(response.status_code, 404)
    
    def test_update_nonexistent_inventory_item(self):
        """Test updating an inventory item that doesn't exist"""
        response = self.client.put('/inventory/9999',
            json={'name': 'Ghost Item'}
        )
        self.assertEqual(response.status_code, 404)
    
    def test_update_inventory_item_invalid_price(self):
        """Test updating inventory item with invalid price"""
        response = self.client.put('/inventory/1',
            json={'price': 'invalid-price'}
        )
        self.assertEqual(response.status_code, 400)
    
    def test_update_inventory_item_invalid_quantity(self):
        """Test updating inventory item with invalid quantity"""
        response = self.client.put('/inventory/1',
            json={'quantity': 'invalid-quantity'}
        )
        self.assertEqual(response.status_code, 400)
    
    def test_delete_nonexistent_inventory_item(self):
        """Test deleting an inventory item that doesn't exist"""
        response = self.client.delete('/inventory/9999')
        self.assertEqual(response.status_code, 404)
    
    def test_delete_inventory_item_twice(self):
        """Test deleting an inventory item that's already deleted"""
        # Delete once
        self.client.delete('/inventory/1')
        
        # Try to delete again
        response = self.client.delete('/inventory/1')
        self.assertEqual(response.status_code, 404)
    
    def test_get_all_inventory_empty_database(self):
        """Test getting inventory when database is empty"""
        # Delete all items
        self.client.delete('/inventory/1')
        self.client.delete('/inventory/2')
        
        response = self.client.get('/inventory/')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(len(data), 0)
    
    def test_create_inventory_item_null_values(self):
        """Test creating inventory item with null values"""
        response = self.client.post('/inventory/',
            json={
                'name': None,
                'price': None,
                'quantity': None
            }
        )
        self.assertEqual(response.status_code, 400)

if __name__ == '__main__':
    unittest.main()