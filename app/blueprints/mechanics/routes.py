from flask import request, jsonify
from app import db
from app.blueprints.mechanics import mechanics_bp
from app.models import Mechanic
from app.blueprints.mechanics.schemas import mechanic_schema, mechanics_schema

# CREATE - POST /mechanics/
@mechanics_bp.route('/', methods=['POST'])
def create_mechanic():
    try:
        data = request.json
        new_mechanic = Mechanic(
            name=data['name'],
            email=data['email'],
            phone=data.get('phone'),
            address=data.get('address'),
            salary=data.get('salary')
        )
        db.session.add(new_mechanic)
        db.session.commit()
        return mechanic_schema.jsonify(new_mechanic), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

# READ ALL - GET /mechanics/
@mechanics_bp.route('/', methods=['GET'])
def get_mechanics():
    mechanics = Mechanic.query.all()
    return mechanics_schema.jsonify(mechanics), 200

# UPDATE - PUT /mechanics/<id>
@mechanics_bp.route('/<int:id>', methods=['PUT'])
def update_mechanic(id):
    mechanic = Mechanic.query.get_or_404(id)
    try:
        data = request.json
        mechanic.name = data.get('name', mechanic.name)
        mechanic.email = data.get('email', mechanic.email)
        mechanic.phone = data.get('phone', mechanic.phone)
        mechanic.address = data.get('address', mechanic.address)
        mechanic.salary = data.get('salary', mechanic.salary)
        
        db.session.commit()
        return mechanic_schema.jsonify(mechanic), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

# DELETE - DELETE /mechanics/<id>
@mechanics_bp.route('/<int:id>', methods=['DELETE'])
def delete_mechanic(id):
    mechanic = Mechanic.query.get_or_404(id)
    try:
        db.session.delete(mechanic)
        db.session.commit()
        return jsonify({'message': 'Mechanic deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400