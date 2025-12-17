from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from datetime import datetime

app = Flask(__name__)

# Configure database connection
# Remember your password has %40 instead of @
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:40Lamonerie%40@localhost/mechanic_shop'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
ma = Marshmallow(app)

# Junction table for many-to-many relationship
mechanic_service = db.Table('mechanic_service',
    db.Column('mechanic_id', db.Integer, db.ForeignKey('mechanics.mechanic_id'), primary_key=True),
    db.Column('ticket_id', db.Integer, db.ForeignKey('service_tickets.ticket_id'), primary_key=True)
)

# Customer Model
class Customer(db.Model):
    __tablename__ = 'customers'
    customer_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    phone = db.Column(db.String(20))
    address = db.Column(db.String(200))
    
    # Relationship: one customer can have many service tickets
    service_tickets = db.relationship('ServiceTicket', backref='customer', lazy=True)

# Mechanic Model
class Mechanic(db.Model):
    __tablename__ = 'mechanics'
    mechanic_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    phone = db.Column(db.String(20))
    address = db.Column(db.String(200))
    salary = db.Column(db.Float)
    
    # Many-to-many relationship with service tickets
    service_tickets = db.relationship('ServiceTicket', secondary=mechanic_service, backref='mechanics')

# Service Ticket Model
class ServiceTicket(db.Model):
    __tablename__ = 'service_tickets'
    ticket_id = db.Column(db.Integer, primary_key=True)
    vin = db.Column(db.String(17), nullable=False)
    service_date = db.Column(db.DateTime, default=datetime.utcnow)
    description = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(50), default='pending')
    
    # Foreign key to customer
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.customer_id'), nullable=False)

# ============================================
# MARSHMALLOW SCHEMAS
# ============================================

class CustomerSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Customer
        load_instance = True

customer_schema = CustomerSchema()
customers_schema = CustomerSchema(many=True)

# ============================================
# CUSTOMER CRUD ROUTES
# ============================================

# CREATE - POST /customers
@app.route('/customers', methods=['POST'])
def create_customer():
    try:
        data = request.json
        new_customer = Customer(
            name=data['name'],
            email=data['email'],
            phone=data.get('phone'),
            address=data.get('address')
        )
        db.session.add(new_customer)
        db.session.commit()
        return customer_schema.jsonify(new_customer), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

# READ ALL - GET /customers
@app.route('/customers', methods=['GET'])
def get_customers():
    customers = Customer.query.all()
    return customers_schema.jsonify(customers), 200

# READ ONE - GET /customers/<id>
@app.route('/customers/<int:id>', methods=['GET'])
def get_customer(id):
    customer = Customer.query.get_or_404(id)
    return customer_schema.jsonify(customer), 200

# UPDATE - PUT /customers/<id>
@app.route('/customers/<int:id>', methods=['PUT'])
def update_customer(id):
    customer = Customer.query.get_or_404(id)
    try:
        data = request.json
        customer.name = data.get('name', customer.name)
        customer.email = data.get('email', customer.email)
        customer.phone = data.get('phone', customer.phone)
        customer.address = data.get('address', customer.address)
        
        db.session.commit()
        return customer_schema.jsonify(customer), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

# DELETE - DELETE /customers/<id>
@app.route('/customers/<int:id>', methods=['DELETE'])
def delete_customer(id):
    customer = Customer.query.get_or_404(id)
    try:
        db.session.delete(customer)
        db.session.commit()
        return jsonify({'message': 'Customer deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

# ============================================
# RUN APPLICATION
# ============================================

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        print("Database tables created!")
    app.run(debug=True)