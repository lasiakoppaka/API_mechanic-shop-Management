from flask import Blueprint

# Create the service_tickets blueprint
service_tickets_bp = Blueprint('service_tickets', __name__)

# Import routes after blueprint creation
from app.blueprints.service_tickets import routes