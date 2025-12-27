from flask import request, jsonify
from flasgger import swag_from
from app import db
from app.blueprints.mechanics import mechanics_bp
from app.models import Mechanic
from app.blueprints.mechanics.schemas import mechanic_schema, mechanics_schema

# CREATE - POST /mechanics/
@mechanics_bp.route('/', methods=['POST'])
@swag_from({
    'tags': ['Mechanics'],
    'summary': 'Create a new mechanic',
    'description': 'Add a new mechanic to the shop staff',
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'required': ['name', 'email'],
                'properties': {
                    'name': {
                        'type': 'string',
                        'example': 'Jane Smith',
                        'description': 'Mechanic full name'
                    },
                    'email': {
                        'type': 'string',
                        'format': 'email',
                        'example': 'jane.smith@mechanicshop.com',
                        'description': 'Mechanic email address'
                    },
                    'phone': {
                        'type': 'string',
                        'example': '555-987-6543',
                        'description': 'Mechanic phone number (optional)'
                    },
                    'address': {
                        'type': 'string',
                        'example': '789 Shop Blvd, City, State 12345',
                        'description': 'Mechanic address (optional)'
                    },
                    'salary': {
                        'type': 'number',
                        'format': 'float',
                        'example': 65000.00,
                        'description': 'Mechanic annual salary (optional)'
                    }
                }
            }
        }
    ],
    'responses': {
        201: {
            'description': 'Mechanic created successfully',
            'schema': {
                'type': 'object',
                'properties': {
                    'mechanic_id': {'type': 'integer', 'example': 1},
                    'name': {'type': 'string', 'example': 'Jane Smith'},
                    'email': {'type': 'string', 'example': 'jane.smith@mechanicshop.com'},
                    'phone': {'type': 'string', 'example': '555-987-6543'},
                    'address': {'type': 'string', 'example': '789 Shop Blvd'},
                    'salary': {'type': 'number', 'example': 65000.00}
                }
            }
        },
        400: {
            'description': 'Bad request - validation error',
            'schema': {
                'type': 'object',
                'properties': {
                    'error': {'type': 'string', 'example': 'Missing required field: email'}
                }
            }
        }
    }
})
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
@swag_from({
    'tags': ['Mechanics'],
    'summary': 'Get all mechanics',
    'description': 'Retrieve a list of all mechanics in the shop',
    'responses': {
        200: {
            'description': 'List of all mechanics',
            'schema': {
                'type': 'array',
                'items': {
                    'type': 'object',
                    'properties': {
                        'mechanic_id': {'type': 'integer', 'example': 1},
                        'name': {'type': 'string', 'example': 'Jane Smith'},
                        'email': {'type': 'string', 'example': 'jane.smith@mechanicshop.com'},
                        'phone': {'type': 'string', 'example': '555-987-6543'},
                        'address': {'type': 'string', 'example': '789 Shop Blvd'},
                        'salary': {'type': 'number', 'example': 65000.00}
                    }
                }
            }
        }
    }
})
def get_mechanics():
    mechanics = Mechanic.query.all()
    return mechanics_schema.jsonify(mechanics), 200

# UPDATE - PUT /mechanics/<id>
@mechanics_bp.route('/<int:id>', methods=['PUT'])
@swag_from({
    'tags': ['Mechanics'],
    'summary': 'Update a mechanic',
    'description': 'Update mechanic information by ID',
    'parameters': [
        {
            'name': 'id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': 'Mechanic ID'
        },
        {
            'name': 'body',
            'in': 'body',
            'schema': {
                'type': 'object',
                'properties': {
                    'name': {'type': 'string', 'example': 'Jane Updated'},
                    'email': {'type': 'string', 'example': 'jane.updated@mechanicshop.com'},
                    'phone': {'type': 'string', 'example': '555-111-2222'},
                    'address': {'type': 'string', 'example': '999 New Address'},
                    'salary': {'type': 'number', 'example': 70000.00}
                }
            }
        }
    ],
    'responses': {
        200: {
            'description': 'Mechanic updated successfully',
            'schema': {
                'type': 'object',
                'properties': {
                    'mechanic_id': {'type': 'integer'},
                    'name': {'type': 'string'},
                    'email': {'type': 'string'},
                    'phone': {'type': 'string'},
                    'address': {'type': 'string'},
                    'salary': {'type': 'number'}
                }
            }
        },
        400: {'description': 'Bad request'},
        404: {'description': 'Mechanic not found'}
    }
})
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
@swag_from({
    'tags': ['Mechanics'],
    'summary': 'Delete a mechanic',
    'description': 'Remove a mechanic from the shop by ID',
    'parameters': [
        {
            'name': 'id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': 'Mechanic ID'
        }
    ],
    'responses': {
        200: {
            'description': 'Mechanic deleted successfully',
            'schema': {
                'type': 'object',
                'properties': {
                    'message': {'type': 'string', 'example': 'Mechanic deleted successfully'}
                }
            }
        },
        400: {'description': 'Bad request'},
        404: {'description': 'Mechanic not found'}
    }
})
def delete_mechanic(id):
    mechanic = Mechanic.query.get_or_404(id)
    try:
        db.session.delete(mechanic)
        db.session.commit()
        return jsonify({'message': 'Mechanic deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

# GET MECHANICS BY TICKETS WORKED - GET /mechanics/by-tickets
@mechanics_bp.route('/by-tickets', methods=['GET'])
@swag_from({
    'tags': ['Mechanics'],
    'summary': 'Get mechanics sorted by tickets worked',
    'description': 'Retrieve all mechanics sorted by the number of service tickets they have worked on (most to least)',
    'responses': {
        200: {
            'description': 'List of mechanics with ticket counts',
            'schema': {
                'type': 'array',
                'items': {
                    'type': 'object',
                    'properties': {
                        'mechanic_id': {'type': 'integer', 'example': 1},
                        'name': {'type': 'string', 'example': 'Jane Smith'},
                        'email': {'type': 'string', 'example': 'jane.smith@mechanicshop.com'},
                        'phone': {'type': 'string', 'example': '555-987-6543'},
                        'address': {'type': 'string', 'example': '789 Shop Blvd'},
                        'salary': {'type': 'number', 'example': 65000.00},
                        'tickets_worked': {'type': 'integer', 'example': 15, 'description': 'Number of service tickets worked on'}
                    }
                }
            }
        }
    }
})
def get_mechanics_by_tickets():
    """
    Get all mechanics sorted by number of service tickets they've worked on (most to least)
    """
    from sqlalchemy import func
    from app.models import mechanic_service
    
    mechanics_with_counts = db.session.query(
        Mechanic,
        func.count(mechanic_service.c.ticket_id).label('ticket_count')
    ).outerjoin(
        mechanic_service,
        Mechanic.mechanic_id == mechanic_service.c.mechanic_id
    ).group_by(
        Mechanic.mechanic_id
    ).order_by(
        func.count(mechanic_service.c.ticket_id).desc()
    ).all()
    
    result = []
    for mechanic, count in mechanics_with_counts:
        mechanic_data = mechanic_schema.dump(mechanic)
        mechanic_data['tickets_worked'] = count
        result.append(mechanic_data)
    
    return jsonify(result), 200