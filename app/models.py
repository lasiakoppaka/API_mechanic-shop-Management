from app import db
from datetime import datetime

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