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
# EDIT TICKET - PUT /service-tickets/<ticket_id>/edit
@service_tickets_bp.route('/<int:ticket_id>/edit', methods=['PUT'])
def edit_service_ticket(ticket_id):
    """
    Add or remove mechanics from a service ticket
    Accepts: { "add_ids": [1, 2], "remove_ids": [3] }
    """
    try:
        ticket = ServiceTicket.query.get_or_404(ticket_id)
        data = request.json
        
        # Get lists of mechanic IDs to add and remove
        add_ids = data.get('add_ids', [])
        remove_ids = data.get('remove_ids', [])
        
        # Add mechanics to ticket
        for mechanic_id in add_ids:
            mechanic = Mechanic.query.get(mechanic_id)
            if mechanic and mechanic not in ticket.mechanics:
                ticket.mechanics.append(mechanic)
        
        # Remove mechanics from ticket
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

