from flask import request, jsonify
from flasgger import swag_from
from app import db, limiter, cache
from app.blueprints.customers import customers_bp
from app.models import Customer
from app.blueprints.customers.schemas import customer_schema, customers_schema, login_schema
from app.utils import encode_token, token_required

# CREATE - POST /customers/
@customers_bp.route('/', methods=['POST'])
@limiter.limit("5 per minute")
@swag_from({
    'tags': ['Customers'],
    'summary': 'Create a new customer',
    'description': 'Register a new customer account. Rate limited to 5 requests per minute to prevent spam.',
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'required': ['name', 'email', 'password'],
                'properties': {
                    'name': {
                        'type': 'string',
                        'example': 'John Doe',
                        'description': 'Customer full name'
                    },
                    'email': {
                        'type': 'string',
                        'format': 'email',
                        'example': 'john.doe@example.com',
                        'description': 'Customer email address'
                    },
                    'password': {
                        'type': 'string',
                        'example': 'SecurePass123!',
                        'description': 'Customer password'
                    },
                    'phone': {
                        'type': 'string',
                        'example': '555-123-4567',
                        'description': 'Customer phone number (optional)'
                    },
                    'address': {
                        'type': 'string',
                        'example': '123 Main St, City, State 12345',
                        'description': 'Customer address (optional)'
                    }
                }
            }
        }
    ],
    'responses': {
        201: {
            'description': 'Customer created successfully',
            'schema': {
                'type': 'object',
                'properties': {
                    'customer_id': {'type': 'integer', 'example': 1},
                    'name': {'type': 'string', 'example': 'John Doe'},
                    'email': {'type': 'string', 'example': 'john.doe@example.com'},
                    'phone': {'type': 'string', 'example': '555-123-4567'},
                    'address': {'type': 'string', 'example': '123 Main St, City, State 12345'}
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
        },
        429: {
            'description': 'Too many requests - rate limit exceeded'
        }
    }
})
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
@cache.cached(timeout=300, query_string=True)
@swag_from({
    'tags': ['Customers'],
    'summary': 'Get all customers',
    'description': 'Retrieve a paginated list of all customers. Results are cached for 5 minutes.',
    'parameters': [
        {
            'name': 'page',
            'in': 'query',
            'type': 'integer',
            'default': 1,
            'description': 'Page number'
        },
        {
            'name': 'per_page',
            'in': 'query',
            'type': 'integer',
            'default': 10,
            'description': 'Number of items per page (max 100)'
        }
    ],
    'responses': {
        200: {
            'description': 'List of customers with pagination metadata',
            'schema': {
                'type': 'object',
                'properties': {
                    'customers': {
                        'type': 'array',
                        'items': {
                            'type': 'object',
                            'properties': {
                                'customer_id': {'type': 'integer', 'example': 1},
                                'name': {'type': 'string', 'example': 'John Doe'},
                                'email': {'type': 'string', 'example': 'john.doe@example.com'},
                                'phone': {'type': 'string', 'example': '555-123-4567'},
                                'address': {'type': 'string', 'example': '123 Main St'}
                            }
                        }
                    },
                    'pagination': {
                        'type': 'object',
                        'properties': {
                            'page': {'type': 'integer', 'example': 1},
                            'per_page': {'type': 'integer', 'example': 10},
                            'total_pages': {'type': 'integer', 'example': 5},
                            'total_items': {'type': 'integer', 'example': 50},
                            'has_next': {'type': 'boolean', 'example': True},
                            'has_prev': {'type': 'boolean', 'example': False}
                        }
                    }
                }
            }
        }
    }
})
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
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    per_page = min(per_page, 100)
    
    pagination = Customer.query.paginate(
        page=page,
        per_page=per_page,
        error_out=False
    )
    
    customers = pagination.items
    
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
@swag_from({
    'tags': ['Customers'],
    'summary': 'Get a specific customer',
    'description': 'Retrieve detailed information about a specific customer by ID',
    'parameters': [
        {
            'name': 'id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': 'Customer ID'
        }
    ],
    'responses': {
        200: {
            'description': 'Customer details',
            'schema': {
                'type': 'object',
                'properties': {
                    'customer_id': {'type': 'integer', 'example': 1},
                    'name': {'type': 'string', 'example': 'John Doe'},
                    'email': {'type': 'string', 'example': 'john.doe@example.com'},
                    'phone': {'type': 'string', 'example': '555-123-4567'},
                    'address': {'type': 'string', 'example': '123 Main St'}
                }
            }
        },
        404: {
            'description': 'Customer not found'
        }
    }
})
def get_customer(id):
    customer = Customer.query.get_or_404(id)
    return customer_schema.jsonify(customer), 200

# UPDATE - PUT /customers/<id>
@customers_bp.route('/<int:id>', methods=['PUT'])
@token_required
@swag_from({
    'tags': ['Customers'],
    'summary': 'Update a customer',
    'description': 'Update customer information. Requires authentication. Customers can only update their own information.',
    'security': [{'Bearer': []}],
    'parameters': [
        {
            'name': 'id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': 'Customer ID'
        },
        {
            'name': 'Authorization',
            'in': 'header',
            'type': 'string',
            'required': True,
            'description': 'Bearer token',
            'example': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...'
        },
        {
            'name': 'body',
            'in': 'body',
            'schema': {
                'type': 'object',
                'properties': {
                    'name': {'type': 'string', 'example': 'John Updated'},
                    'email': {'type': 'string', 'example': 'john.updated@example.com'},
                    'password': {'type': 'string', 'example': 'NewPass123!'},
                    'phone': {'type': 'string', 'example': '555-999-8888'},
                    'address': {'type': 'string', 'example': '456 New St'}
                }
            }
        }
    ],
    'responses': {
        200: {
            'description': 'Customer updated successfully',
            'schema': {
                'type': 'object',
                'properties': {
                    'customer_id': {'type': 'integer'},
                    'name': {'type': 'string'},
                    'email': {'type': 'string'},
                    'phone': {'type': 'string'},
                    'address': {'type': 'string'}
                }
            }
        },
        400: {'description': 'Bad request'},
        401: {'description': 'Unauthorized - invalid or missing token'},
        403: {'description': 'Forbidden - cannot update another customer'},
        404: {'description': 'Customer not found'}
    }
})
def update_customer(customer_id, id):
    """
    Update customer - requires token authentication
    Customers can only update their own information
    """
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
@swag_from({
    'tags': ['Customers'],
    'summary': 'Delete a customer',
    'description': 'Delete a customer account. Requires authentication. Customers can only delete their own account.',
    'security': [{'Bearer': []}],
    'parameters': [
        {
            'name': 'id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': 'Customer ID'
        },
        {
            'name': 'Authorization',
            'in': 'header',
            'type': 'string',
            'required': True,
            'description': 'Bearer token',
            'example': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...'
        }
    ],
    'responses': {
        200: {
            'description': 'Customer deleted successfully',
            'schema': {
                'type': 'object',
                'properties': {
                    'message': {'type': 'string', 'example': 'Customer deleted successfully'}
                }
            }
        },
        400: {'description': 'Bad request'},
        401: {'description': 'Unauthorized - invalid or missing token'},
        403: {'description': 'Forbidden - cannot delete another customer'},
        404: {'description': 'Customer not found'}
    }
})
def delete_customer(customer_id, id):
    """
    Delete customer - requires token authentication
    Customers can only delete their own account
    """
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
@swag_from({
    'tags': ['Customers'],
    'summary': 'Customer login',
    'description': 'Authenticate a customer and receive a JWT token',
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'required': ['email', 'password'],
                'properties': {
                    'email': {
                        'type': 'string',
                        'example': 'john.doe@example.com',
                        'description': 'Customer email'
                    },
                    'password': {
                        'type': 'string',
                        'example': 'SecurePass123!',
                        'description': 'Customer password'
                    }
                }
            }
        }
    ],
    'responses': {
        200: {
            'description': 'Login successful',
            'schema': {
                'type': 'object',
                'properties': {
                    'message': {'type': 'string', 'example': 'Login successful'},
                    'token': {'type': 'string', 'example': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...'},
                    'customer_id': {'type': 'integer', 'example': 1}
                }
            }
        },
        400: {'description': 'Bad request - validation error'},
        401: {
            'description': 'Unauthorized - invalid credentials',
            'schema': {
                'type': 'object',
                'properties': {
                    'message': {'type': 'string', 'example': 'Invalid email or password'}
                }
            }
        }
    }
})
def login():
    """
    Customer login endpoint
    Accepts email and password, returns JWT token
    """
    try:
        data = login_schema.load(request.json)
        customer = Customer.query.filter_by(email=data['email']).first()
        
        if customer and customer.password == data['password']:
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
@swag_from({
    'tags': ['Customers'],
    'summary': 'Get my service tickets',
    'description': 'Retrieve all service tickets for the authenticated customer',
    'security': [{'Bearer': []}],
    'parameters': [
        {
            'name': 'Authorization',
            'in': 'header',
            'type': 'string',
            'required': True,
            'description': 'Bearer token',
            'example': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...'
        }
    ],
    'responses': {
        200: {
            'description': 'List of customer service tickets',
            'schema': {
                'type': 'array',
                'items': {
                    'type': 'object',
                    'properties': {
                        'service_ticket_id': {'type': 'integer'},
                        'vin': {'type': 'string'},
                        'description': {'type': 'string'},
                        'customer_id': {'type': 'integer'}
                    }
                }
            }
        },
        401: {'description': 'Unauthorized - invalid or missing token'},
        404: {'description': 'Customer not found'}
    }
})
def get_my_tickets(customer_id):
    """
    Get all service tickets for the logged-in customer
    Requires valid Bearer token
    """
    customer = Customer.query.get_or_404(customer_id)
    from app.blueprints.service_tickets.schemas import service_tickets_schema
    tickets = customer.service_tickets
    return service_tickets_schema.jsonify(tickets), 200