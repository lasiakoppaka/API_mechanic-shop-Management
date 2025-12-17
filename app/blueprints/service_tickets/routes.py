from flask import request, jsonify
from app import db
from app.blueprints.service_tickets import service_tickets_bp
from app.models import ServiceTicket, Mechanic
from app.blueprints.service_tickets.schemas import service_ticket_schema, service_tickets_schema

# CREATE - POST /service-tickets/
@service_tickets_bp.route('/', methods=['POST'])
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
def get_service_tickets():
    tickets = ServiceTicket.query.all()
    return service_tickets_schema.jsonify(tickets), 200

# ASSIGN MECHANIC - PUT /service-tickets/<ticket_id>/assign-mechanic/<mechanic_id>
@service_tickets_bp.route('/<int:ticket_id>/assign-mechanic/<int:mechanic_id>', methods=['PUT'])
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