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

### Prerequisites

- Python 3.11+
- MySQL Server
- MySQL Workbench (optional)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/YourUsername/mechanic_shop_api.git
cd mechanic_shop_api
```

2. Create and activate virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Mac/Linux
# venv\Scripts\activate   # On Windows
```

3. Install dependencies:
```bash
pip install flask flask-sqlalchemy mysql-connector-python flask-marshmallow marshmallow-sqlalchemy
```

4. Create MySQL database:
```sql
CREATE DATABASE mechanic_shop;
```

5. Update database credentials in `app/__init__.py`:
```python
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:YOUR_PASSWORD@localhost/mechanic_shop'
```

6. Run the application:
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

**Save the file** (Cmd + S)

---

## **STEP 3: Create .gitignore File**

Create a `.gitignore` file to exclude unnecessary files from Git:

In VS Code, create `.gitignore` in the project root and paste:
```
# Virtual Environment
venv/
env/
ENV/

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Database
*.db
*.sqlite
*.sqlite3

# Environment variables
.env
```

**Save the file**

---

## **STEP 4: Verify Your Final Project Structure**

Your project should look like this:
```
mechanic_shop_api/
├── app/
│   ├── __init__.py
│   ├── models.py
│   └── blueprints/
│       ├── __init__.py
│       ├── customers/
│       │   ├── __init__.py
│       │   ├── routes.py
│       │   └── schemas.py
│       ├── mechanics/
│       │   ├── __init__.py
│       │   ├── routes.py
│       │   └── schemas.py
│       └── service_tickets/
│           ├── __init__.py
│           ├── routes.py
│           └── schemas.py
├── venv/ (don't commit this)
├── app.py (old file - can keep for reference)
├── run.py
├── README.md
├── .gitignore
└── Mechanic_Shop_API.postman_collection.json