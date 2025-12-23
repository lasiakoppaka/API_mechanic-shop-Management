from app import ma
from app.models import Customer
from marshmallow import fields

class CustomerSchema(ma.SQLAlchemyAutoSchema):
    password = fields.String(load_only=True)  # Only used for input, never returned
    
    class Meta:
        model = Customer
        load_instance = True

# Schema for creating/updating customers
customer_schema = CustomerSchema()
customers_schema = CustomerSchema(many=True)

# Schema for login (only email and password)
class LoginSchema(ma.Schema):
    email = fields.String(required=True)
    password = fields.String(required=True)

login_schema = LoginSchema()