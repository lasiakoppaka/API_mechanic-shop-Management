from flask import Blueprint

# Create the customers blueprint
customers_bp = Blueprint('customers', __name__)

# Import routes after blueprint creation to avoid circular imports
from app.blueprints.customers import routes