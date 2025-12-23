from flask import Blueprint

# Create the inventory blueprint
inventory_bp = Blueprint('inventory', __name__)

# Import routes after blueprint creation
from app.blueprints.inventory import routes