from app import ma
from app.models import ServiceTicket
from app.blueprints.mechanics.schemas import MechanicSchema

class ServiceTicketSchema(ma.SQLAlchemyAutoSchema):
    mechanics = ma.Nested(MechanicSchema, many=True)
    
    class Meta:
        model = ServiceTicket
        load_instance = True
        include_fk = True

service_ticket_schema = ServiceTicketSchema()
service_tickets_schema = ServiceTicketSchema(many=True)