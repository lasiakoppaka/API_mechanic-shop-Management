from flask import request, jsonify
from flasgger import swag_from
from app import db
from app.blueprints.inventory import inventory_bp
from app.models import Inventory
from app.blueprints.inventory.schemas import inventory_schema, inventories_schema

# CREATE - POST /inventory/
@inventory_bp.route('/', methods=['POST'])
@swag_from({
    'tags': ['Inventory'],
    'summary': 'Create a new inventory item',
    'description': 'Add a new part or item to the shop inventory',
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'required': ['name', 'price'],
                'properties': {
                    'name': {
                        'type': 'string',
                        'example': 'Oil Filter',
                        'description': 'Name of the inventory item'
                    },
                    'price': {
                        'type': 'number',
                        'format': 'float',
                        'example': 15.99,
                        'description': 'Price of the item'
                    },
                    'quantity': {
                        'type': 'integer',
                        'example': 50,
                        'description': 'Quantity in stock (default: 0)'
                    }
                }
            }
        }
    ],
    'responses': {
        201: {
            'description': 'Inventory item created successfully',
            'schema': {
                'type': 'object',
                'properties': {
                    'inventory_id': {'type': 'integer', 'example': 1},
                    'name': {'type': 'string', 'example': 'Oil Filter'},
                    'price': {'type': 'number', 'example': 15.99},
                    'quantity': {'type': 'integer', 'example': 50}
                }
            }
        },
        400: {
            'description': 'Bad request - validation error',
            'schema': {
                'type': 'object',
                'properties': {
                    'error': {'type': 'string', 'example': 'Missing required field: price'}
                }
            }
        }
    }
})
def create_inventory():
    try:
        data = request.json
        new_item = Inventory(
            name=data['name'],
            price=data['price'],
            quantity=data.get('quantity', 0)
        )
        db.session.add(new_item)
        db.session.commit()
        return inventory_schema.jsonify(new_item), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

# READ ALL - GET /inventory/
@inventory_bp.route('/', methods=['GET'])
@swag_from({
    'tags': ['Inventory'],
    'summary': 'Get all inventory items',
    'description': 'Retrieve a list of all items in the shop inventory',
    'responses': {
        200: {
            'description': 'List of all inventory items',
            'schema': {
                'type': 'array',
                'items': {
                    'type': 'object',
                    'properties': {
                        'inventory_id': {'type': 'integer', 'example': 1},
                        'name': {'type': 'string', 'example': 'Oil Filter'},
                        'price': {'type': 'number', 'example': 15.99},
                        'quantity': {'type': 'integer', 'example': 50}
                    }
                }
            }
        }
    }
})
def get_inventory():
    items = Inventory.query.all()
    return inventories_schema.jsonify(items), 200

# READ ONE - GET /inventory/<id>
@inventory_bp.route('/<int:id>', methods=['GET'])
@swag_from({
    'tags': ['Inventory'],
    'summary': 'Get a specific inventory item',
    'description': 'Retrieve detailed information about a specific inventory item by ID',
    'parameters': [
        {
            'name': 'id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': 'Inventory item ID'
        }
    ],
    'responses': {
        200: {
            'description': 'Inventory item details',
            'schema': {
                'type': 'object',
                'properties': {
                    'inventory_id': {'type': 'integer', 'example': 1},
                    'name': {'type': 'string', 'example': 'Oil Filter'},
                    'price': {'type': 'number', 'example': 15.99},
                    'quantity': {'type': 'integer', 'example': 50}
                }
            }
        },
        404: {
            'description': 'Inventory item not found'
        }
    }
})
def get_inventory_item(id):
    item = Inventory.query.get_or_404(id)
    return inventory_schema.jsonify(item), 200

# UPDATE - PUT /inventory/<id>
@inventory_bp.route('/<int:id>', methods=['PUT'])
@swag_from({
    'tags': ['Inventory'],
    'summary': 'Update an inventory item',
    'description': 'Update inventory item information by ID',
    'parameters': [
        {
            'name': 'id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': 'Inventory item ID'
        },
        {
            'name': 'body',
            'in': 'body',
            'schema': {
                'type': 'object',
                'properties': {
                    'name': {'type': 'string', 'example': 'Premium Oil Filter'},
                    'price': {'type': 'number', 'example': 19.99},
                    'quantity': {'type': 'integer', 'example': 75}
                }
            }
        }
    ],
    'responses': {
        200: {
            'description': 'Inventory item updated successfully',
            'schema': {
                'type': 'object',
                'properties': {
                    'inventory_id': {'type': 'integer'},
                    'name': {'type': 'string'},
                    'price': {'type': 'number'},
                    'quantity': {'type': 'integer'}
                }
            }
        },
        400: {'description': 'Bad request'},
        404: {'description': 'Inventory item not found'}
    }
})
def update_inventory(id):
    item = Inventory.query.get_or_404(id)
    try:
        data = request.json
        item.name = data.get('name', item.name)
        item.price = data.get('price', item.price)
        item.quantity = data.get('quantity', item.quantity)
        
        db.session.commit()
        return inventory_schema.jsonify(item), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

# DELETE - DELETE /inventory/<id>
@inventory_bp.route('/<int:id>', methods=['DELETE'])
@swag_from({
    'tags': ['Inventory'],
    'summary': 'Delete an inventory item',
    'description': 'Remove an item from the shop inventory by ID',
    'parameters': [
        {
            'name': 'id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': 'Inventory item ID'
        }
    ],
    'responses': {
        200: {
            'description': 'Inventory item deleted successfully',
            'schema': {
                'type': 'object',
                'properties': {
                    'message': {'type': 'string', 'example': 'Inventory item deleted successfully'}
                }
            }
        },
        400: {'description': 'Bad request'},
        404: {'description': 'Inventory item not found'}
    }
})
def delete_inventory(id):
    item = Inventory.query.get_or_404(id)
    try:
        db.session.delete(item)
        db.session.commit()
        return jsonify({'message': 'Inventory item deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400