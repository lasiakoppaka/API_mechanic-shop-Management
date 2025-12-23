from flask import request, jsonify
from app import db, limiter, cache
from app.blueprints.customers import customers_bp
from app.models import Customer
from app.blueprints.customers.schemas import customer_schema, customers_schema, login_schema
from app.utils import encode_token, token_required

# CREATE - POST /customers/
@customers_bp.route('/', methods=['POST'])
@limiter.limit("5 per minute")
def create_customer():
    """
    Rate limiting applied here because:
    - Prevents spam account creation
    - Protects against automated bot attacks
    - Ensures database isn't overwhelmed with new customers
    """
    try:
        data = request.json
        new_customer = Customer(
            name=data['name'],
            email=data['email'],
            password=data['password'],
            phone=data.get('phone'),
            address=data.get('address')
        )
        db.session.add(new_customer)
        db.session.commit()
        return customer_schema.jsonify(new_customer), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

# READ ALL - GET /customers/ (with pagination)
@customers_bp.route('/', methods=['GET'])
@cache.cached(timeout=300, query_string=True)  # Cache includes query params
def get_customers():
    """
    Get all customers with pagination
    Query params: page (default 1), per_page (default 10)
    Example: /customers/?page=2&per_page=5
    
    Caching applied here because:
    - Customer list doesn't change frequently
    - Reduces database load for repeated requests
    - Improves response time for frequently accessed data
    """
    # Get pagination parameters from query string
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    # Limit per_page to max 100
    per_page = min(per_page, 100)
    
    # Query with pagination
    pagination = Customer.query.paginate(
        page=page,
        per_page=per_page,
        error_out=False
    )
    
    customers = pagination.items
    
    # Build response with pagination metadata
    result = {
        'customers': customers_schema.dump(customers),
        'pagination': {
            'page': pagination.page,
            'per_page': pagination.per_page,
            'total_pages': pagination.pages,
            'total_items': pagination.total,
            'has_next': pagination.has_next,
            'has_prev': pagination.has_prev
        }
    }
    
    return jsonify(result), 200

# READ ONE - GET /customers/<id>
@customers_bp.route('/<int:id>', methods=['GET'])
def get_customer(id):
    customer = Customer.query.get_or_404(id)
    return customer_schema.jsonify(customer), 200

# UPDATE - PUT /customers/<id>
@customers_bp.route('/<int:id>', methods=['PUT'])
@token_required
def update_customer(customer_id, id):
    """
    Update customer - requires token authentication
    Customers can only update their own information
    """
    # Verify the customer is updating their own info
    if customer_id != id:
        return jsonify({'message': 'Unauthorized to update this customer'}), 403
    
    customer = Customer.query.get_or_404(id)
    try:
        data = request.json
        customer.name = data.get('name', customer.name)
        customer.email = data.get('email', customer.email)
        customer.phone = data.get('phone', customer.phone)
        customer.address = data.get('address', customer.address)
        if 'password' in data:
            customer.password = data['password']
        
        db.session.commit()
        return customer_schema.jsonify(customer), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

# DELETE - DELETE /customers/<id>
@customers_bp.route('/<int:id>', methods=['DELETE'])
@token_required
def delete_customer(customer_id, id):
    """
    Delete customer - requires token authentication
    Customers can only delete their own account
    """
    # Verify the customer is deleting their own account
    if customer_id != id:
        return jsonify({'message': 'Unauthorized to delete this customer'}), 403
    
    customer = Customer.query.get_or_404(id)
    try:
        db.session.delete(customer)
        db.session.commit()
        return jsonify({'message': 'Customer deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

# LOGIN - POST /customers/login
@customers_bp.route('/login', methods=['POST'])
def login():
    """
    Customer login endpoint
    Accepts email and password, returns JWT token
    """
    try:
        # Validate input with login schema
        data = login_schema.load(request.json)
        
        # Find customer by email
        customer = Customer.query.filter_by(email=data['email']).first()
        
        # Check if customer exists and password matches
        if customer and customer.password == data['password']:
            # Generate token
            token = encode_token(customer.customer_id)
            return jsonify({
                'message': 'Login successful',
                'token': token,
                'customer_id': customer.customer_id
            }), 200
        else:
            return jsonify({'message': 'Invalid email or password'}), 401
    
    except Exception as e:
        return jsonify({'error': str(e)}), 400

# GET MY TICKETS - GET /customers/my-tickets
@customers_bp.route('/my-tickets', methods=['GET'])
@token_required
def get_my_tickets(customer_id):
    """
    Get all service tickets for the logged-in customer
    Requires valid Bearer token
    """
    customer = Customer.query.get_or_404(customer_id)
    
    # Get all service tickets for this customer
    from app.blueprints.service_tickets.schemas import service_tickets_schema
    tickets = customer.service_tickets
    
    return service_tickets_schema.jsonify(tickets), 200