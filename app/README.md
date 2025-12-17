# Mechanic Shop API

A RESTful API for managing a mechanic shop built with Flask, SQLAlchemy, and MySQL.

## Features

- Customer management (CRUD operations)
- Mechanic management (CRUD operations)
- Service ticket management
- Assign/remove mechanics to service tickets
- Many-to-many relationship between mechanics and service tickets

## Technologies Used

- **Flask** - Web framework
- **Flask-SQLAlchemy** - ORM
- **Flask-Marshmallow** - Serialization/Deserialization
- **MySQL** - Database
- **Postman** - API testing

## Project Structure
```
mechanic_shop_api/
├── app/
│   ├── __init__.py                 # Application factory
│   ├── models.py                   # Database models
│   └── blueprints/
│       ├── customers/
│       │   ├── __init__.py
│       │   ├── routes.py          # Customer CRUD routes
│       │   └── schemas.py         # Customer schemas
│       ├── mechanics/
│       │   ├── __init__.py
│       │   ├── routes.py          # Mechanic CRUD routes
│       │   └── schemas.py         # Mechanic schemas
│       └── service_tickets/
│           ├── __init__.py
│           ├── routes.py          # Service ticket routes
│           └── schemas.py         # Service ticket schemas
├── venv/                           # Virtual environment (not in repo)
├── run.py                          # Application entry point
├── Mechanic_Shop_API.postman_collection.json
└── README.md
```

## Setup Instructions

1. Install dependencies:
```bash
pip install flask flask-sqlalchemy mysql-connector-python flask-marshmallow marshmallow-sqlalchemy
```

2. Create MySQL database:
```sql
CREATE DATABASE mechanic_shop;
```

3. Update database credentials in `app/__init__.py`:
```python
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:YOUR_PASSWORD@localhost/mechanic_shop'
```

4. Run the application:
```bash
python3 run.py
```

The API will be available at `http://127.0.0.1:5000`

## API Endpoints

### Customers

- `POST /customers/` - Create a new customer
- `GET /customers/` - Get all customers
- `GET /customers/<id>` - Get a single customer
- `PUT /customers/<id>` - Update a customer
- `DELETE /customers/<id>` - Delete a customer

### Mechanics

- `POST /mechanics/` - Create a new mechanic
- `GET /mechanics/` - Get all mechanics
- `PUT /mechanics/<id>` - Update a mechanic
- `DELETE /mechanics/<id>` - Delete a mechanic

### Service Tickets

- `POST /service-tickets/` - Create a new service ticket
- `GET /service-tickets/` - Get all service tickets
- `PUT /service-tickets/<ticket_id>/assign-mechanic/<mechanic_id>` - Assign a mechanic to a ticket
- `PUT /service-tickets/<ticket_id>/remove-mechanic/<mechanic_id>` - Remove a mechanic from a ticket

## Testing with Postman

1. Import the Postman collection: `Mechanic_Shop_API.postman_collection.json`
2. Make sure the Flask application is running
3. Test each endpoint using the provided collection

## Database Schema

### Customers
- customer_id (Primary Key)
- name
- email (Unique)
- phone
- address

### Mechanics
- mechanic_id (Primary Key)
- name
- email (Unique)
- phone
- address
- salary

### Service Tickets
- ticket_id (Primary Key)
- vin
- service_date
- description
- status
- customer_id (Foreign Key)

### Mechanic-Service (Junction Table)
- mechanic_id (Foreign Key)
- ticket_id (Foreign Key)

## Author

Lasia Koppaka
```

