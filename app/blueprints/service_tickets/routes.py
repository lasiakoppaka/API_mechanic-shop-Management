from flask import request, jsonify
from flasgger import swag_from
from app import db
from app.blueprints.service_tickets import service_tickets_bp
from app.models import ServiceTicket, Mechanic
from app.blueprints.service_tickets.schemas import service_ticket_schema, service_tickets_schema

# CREATE - POST /service-tickets/
@service_tickets_bp.route('/', methods=['POST'])
@swag_from({
    'tags': ['Service Tickets'],
    'summary': 'Create a new service ticket',
    'description': 'Create a new service ticket for a customer vehicle',
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'required': ['vin', 'description', 'customer_id'],
                'properties': {
                    'vin': {
                        'type': 'string',
                        'example': '1HGBH41JXMN109186',
                        'description': 'Vehicle Identification Number'
                    },
                    'description': {
                        'type': 'string',
                        'example': 'Oil change and brake inspection',
                        'description': 'Description of service needed'
                    },
                    'customer_id': {
                        'type': 'integer',
                        'example': 1,
                        'description': 'ID of the customer who owns the vehicle'
                    },
                    'status': {
                        'type': 'string',
                        'example': 'pending',
                        'description': 'Ticket status (default: pending)',
                        'enum': ['pending', 'in_progress', 'completed', 'cancelled']
                    }
                }
            }
        }
    ],
    'responses': {
        201: {
            'description': 'Service ticket created successfully',
            'schema': {
                'type': 'object',
                'properties': {
                    'service_ticket_id': {'type': 'integer', 'example': 1},
                    'vin': {'type': 'string', 'example': '1HGBH41JXMN109186'},
                    'description': {'type': 'string', 'example': 'Oil change and brake inspection'},
                    'customer_id': {'type': 'integer', 'example': 1},
                    'status': {'type': 'string', 'example': 'pending'}
                }
            }
        },
        400: {
            'description': 'Bad request - validation error',
            'schema': {
                'type': 'object',
                'properties': {
                    'error': {'type': 'string', 'example': 'Missing required field: vin'}
                }
            }
        }
    }
})
def create_service_ticket():
    try:
        data = request.json
        new_ticket = ServiceTicket(
            vin=data['vin'],
            description=data['description'],
            customer_id=data['customer_id'],
            status=data.get('status', 'pending')
        )
        db.session.add(new_ticket)
        db.session.commit()
        return service_ticket_schema.jsonify(new_ticket), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

# READ ALL - GET /service-tickets/
@service_tickets_bp.route('/', methods=['GET'])
@swag_from({
    'tags': ['Service Tickets'],
    'summary': 'Get all service tickets',
    'description': 'Retrieve a list of all service tickets',
    'responses': {
        200: {
            'description': 'List of all service tickets',
            'schema': {
                'type': 'array',
                'items': {
                    'type': 'object',
                    'properties': {
                        'service_ticket_id': {'type': 'integer', 'example': 1},
                        'vin': {'type': 'string', 'example': '1HGBH41JXMN109186'},
                        'description': {'type': 'string', 'example': 'Oil change and brake inspection'},
                        'customer_id': {'type': 'integer', 'example': 1},
                        'status': {'type': 'string', 'example': 'pending'},
                        'mechanics': {
                            'type': 'array',
                            'items': {
                                'type': 'object',
                                'properties': {
                                    'mechanic_id': {'type': 'integer'},
                                    'name': {'type': 'string'}
                                }
                            }
                        }
                    }
                }
            }
        }
    }
})
def get_service_tickets():
    tickets = ServiceTicket.query.all()
    return service_tickets_schema.jsonify(tickets), 200

# ASSIGN MECHANIC - PUT /service-tickets/<ticket_id>/assign-mechanic/<mechanic_id>
@service_tickets_bp.route('/<int:ticket_id>/assign-mechanic/<int:mechanic_id>', methods=['PUT'])
@swag_from({
    'tags': ['Service Tickets'],
    'summary': 'Assign a mechanic to a service ticket',
    'description': 'Assign a mechanic to work on a specific service ticket',
    'parameters': [
        {
            'name': 'ticket_id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': 'Service ticket ID'
        },
        {
            'name': 'mechanic_id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': 'Mechanic ID'
        }
    ],
    'responses': {
        200: {
            'description': 'Mechanic assigned successfully or already assigned',
            'schema': {
                'type': 'object',
                'properties': {
                    'service_ticket_id': {'type': 'integer'},
                    'vin': {'type': 'string'},
                    'description': {'type': 'string'},
                    'mechanics': {
                        'type': 'array',
                        'items': {'type': 'object'}
                    }
                }
            }
        },
        400: {'description': 'Bad request'},
        404: {'description': 'Ticket or mechanic not found'}
    }
})
def assign_mechanic(ticket_id, mechanic_id):
    try:
        ticket = ServiceTicket.query.get_or_404(ticket_id)
        mechanic = Mechanic.query.get_or_404(mechanic_id)
        
        if mechanic not in ticket.mechanics:
            ticket.mechanics.append(mechanic)
            db.session.commit()
            return service_ticket_schema.jsonify(ticket), 200
        else:
            return jsonify({'message': 'Mechanic already assigned to this ticket'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

# REMOVE MECHANIC - PUT /service-tickets/<ticket_id>/remove-mechanic/<mechanic_id>
@service_tickets_bp.route('/<int:ticket_id>/remove-mechanic/<int:mechanic_id>', methods=['PUT'])
@swag_from({
    'tags': ['Service Tickets'],
    'summary': 'Remove a mechanic from a service ticket',
    'description': 'Remove an assigned mechanic from a specific service ticket',
    'parameters': [
        {
            'name': 'ticket_id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': 'Service ticket ID'
        },
        {
            'name': 'mechanic_id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': 'Mechanic ID'
        }
    ],
    'responses': {
        200: {
            'description': 'Mechanic removed successfully',
            'schema': {
                'type': 'object',
                'properties': {
                    'service_ticket_id': {'type': 'integer'},
                    'vin': {'type': 'string'},
                    'description': {'type': 'string'},
                    'mechanics': {'type': 'array'}
                }
            }
        },
        400: {'description': 'Bad request'},
        404: {
            'description': 'Ticket/mechanic not found or mechanic not assigned',
            'schema': {
                'type': 'object',
                'properties': {
                    'message': {'type': 'string', 'example': 'Mechanic not assigned to this ticket'}
                }
            }
        }
    }
})
def remove_mechanic(ticket_id, mechanic_id):
    try:
        ticket = ServiceTicket.query.get_or_404(ticket_id)
        mechanic = Mechanic.query.get_or_404(mechanic_id)
        
        if mechanic in ticket.mechanics:
            ticket.mechanics.remove(mechanic)
            db.session.commit()
            return service_ticket_schema.jsonify(ticket), 200
        else:
            return jsonify({'message': 'Mechanic not assigned to this ticket'}), 404
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

# EDIT TICKET - PUT /service-tickets/<ticket_id>/edit
@service_tickets_bp.route('/<int:ticket_id>/edit', methods=['PUT'])
@swag_from({
    'tags': ['Service Tickets'],
    'summary': 'Batch edit ticket mechanics',
    'description': 'Add or remove multiple mechanics from a service ticket in one request',
    'parameters': [
        {
            'name': 'ticket_id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': 'Service ticket ID'
        },
        {
            'name': 'body',
            'in': 'body',
            'schema': {
                'type': 'object',
                'properties': {
                    'add_ids': {
                        'type': 'array',
                        'items': {'type': 'integer'},
                        'example': [1, 2],
                        'description': 'Array of mechanic IDs to add'
                    },
                    'remove_ids': {
                        'type': 'array',
                        'items': {'type': 'integer'},
                        'example': [3],
                        'description': 'Array of mechanic IDs to remove'
                    }
                }
            }
        }
    ],
    'responses': {
        200: {
            'description': 'Ticket updated successfully',
            'schema': {
                'type': 'object',
                'properties': {
                    'service_ticket_id': {'type': 'integer'},
                    'mechanics': {
                        'type': 'array',
                        'description': 'Updated list of assigned mechanics'
                    }
                }
            }
        },
        400: {'description': 'Bad request'},
        404: {'description': 'Ticket not found'}
    }
})
def edit_service_ticket(ticket_id):
    """
    Add or remove mechanics from a service ticket
    Accepts: { "add_ids": [1, 2], "remove_ids": [3] }
    """
    try:
        ticket = ServiceTicket.query.get_or_404(ticket_id)
        data = request.json
        
        add_ids = data.get('add_ids', [])
        remove_ids = data.get('remove_ids', [])
        
        for mechanic_id in add_ids:
            mechanic = Mechanic.query.get(mechanic_id)
            if mechanic and mechanic not in ticket.mechanics:
                ticket.mechanics.append(mechanic)
        
        for mechanic_id in remove_ids:
            mechanic = Mechanic.query.get(mechanic_id)
            if mechanic and mechanic in ticket.mechanics:
                ticket.mechanics.remove(mechanic)
        
        db.session.commit()
        return service_ticket_schema.jsonify(ticket), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

# ADD PART TO TICKET - POST /service-tickets/<ticket_id>/add-part/<inventory_id>
@service_tickets_bp.route('/<int:ticket_id>/add-part/<int:inventory_id>', methods=['POST'])
@swag_from({
    'tags': ['Service Tickets'],
    'summary': 'Add a part to a service ticket',
    'description': 'Add an inventory item (part) to a service ticket',
    'parameters': [
        {
            'name': 'ticket_id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': 'Service ticket ID'
        },
        {
            'name': 'inventory_id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': 'Inventory item ID'
        }
    ],
    'responses': {
        200: {
            'description': 'Part added successfully or already added',
            'schema': {
                'type': 'object',
                'properties': {
                    'service_ticket_id': {'type': 'integer'},
                    'inventory_items': {
                        'type': 'array',
                        'items': {'type': 'object'}
                    }
                }
            }
        },
        400: {'description': 'Bad request'},
        404: {'description': 'Ticket or inventory item not found'}
    }
})
def add_part_to_ticket(ticket_id, inventory_id):
    """
    Add an inventory item (part) to a service ticket
    """
    try:
        from app.models import Inventory
        
        ticket = ServiceTicket.query.get_or_404(ticket_id)
        part = Inventory.query.get_or_404(inventory_id)
        
        if part not in ticket.inventory_items:
            ticket.inventory_items.append(part)
            db.session.commit()
            return service_ticket_schema.jsonify(ticket), 200
        else:
            return jsonify({'message': 'Part already added to this ticket'}), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400