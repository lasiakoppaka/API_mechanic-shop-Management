from flask import Blueprint

# Create the mechanics blueprint
mechanics_bp = Blueprint('mechanics', __name__)

# Import routes after blueprint creation
from app.blueprints.mechanics import routes