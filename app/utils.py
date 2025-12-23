from jose import JWTError, jwt
from datetime import datetime, timedelta
from flask import request, jsonify
from functools import wraps

# Secret key for encoding/decoding JWT tokens
# In production, this should be in environment variables!
SECRET_KEY = "your-secret-key-change-this-in-production"
ALGORITHM = "HS256"

def encode_token(customer_id):
    """
    Create a JWT token for a customer
    
    Args:
        customer_id: The customer's ID
    
    Returns:
        A JWT token string
    """
    payload = {
        'exp': datetime.utcnow() + timedelta(days=1),  # Token expires in 1 day
        'iat': datetime.utcnow(),  # Token issued at
        'sub': str(customer_id)  # Convert to string - JWT requires this
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def token_required(func):
    """
    Decorator to protect routes with token authentication
    The decorated function will receive customer_id as first argument
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        token = None
        
        # Check if Authorization header is present
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            print(f"DEBUG: Auth header received: {auth_header[:50]}...")  # Print first 50 chars
            try:
                # Expected format: "Bearer <token>"
                token = auth_header.split(" ")[1]
                print(f"DEBUG: Token extracted: {token[:50]}...")  # Print first 50 chars
            except IndexError:
                print("DEBUG: Token format invalid!")
                return jsonify({'message': 'Token format invalid. Use: Bearer <token>'}), 401
        
        if not token:
            print("DEBUG: No token found!")
            return jsonify({'message': 'Token is missing!'}), 401
        
        try:
            # Decode the token
            print(f"DEBUG: Attempting to decode token...")
            print(f"DEBUG: Using SECRET_KEY: {SECRET_KEY}")
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            customer_id = int(payload['sub'])  # Convert back to int
            print(f"DEBUG: Token decoded successfully! customer_id: {customer_id}")
            
            # Pass customer_id to the decorated function
            return func(customer_id, *args, **kwargs)
        
        except JWTError as e:
            print(f"DEBUG: JWT Error: {str(e)}")
            return jsonify({'message': 'Token is invalid or expired!'}), 401
    
    return wrapper