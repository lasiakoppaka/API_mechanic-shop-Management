from flask import request, jsonify
from app import db
from app.blueprints.inventory import inventory_bp
from app.models import Inventory
from app.blueprints.inventory.schemas import inventory_schema, inventories_schema

# CREATE - POST /inventory/
@inventory_bp.route('/', methods=['POST'])
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
def get_inventory():
    items = Inventory.query.all()
    return inventories_schema.jsonify(items), 200

# READ ONE - GET /inventory/<id>
@inventory_bp.route('/<int:id>', methods=['GET'])
def get_inventory_item(id):
    item = Inventory.query.get_or_404(id)
    return inventory_schema.jsonify(item), 200

# UPDATE - PUT /inventory/<id>
@inventory_bp.route('/<int:id>', methods=['PUT'])
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
def delete_inventory(id):
    item = Inventory.query.get_or_404(id)
    try:
        db.session.delete(item)
        db.session.commit()
        return jsonify({'message': 'Inventory item deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400