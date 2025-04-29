import logging
from functools import wraps
from flask import jsonify
import traceback

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class APIError(Exception):
    """Base class for API errors"""
    def __init__(self, message, status_code=500, payload=None):
        super().__init__()
        self.message = message
        self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['message'] = self.message
        rv['status'] = 'error'
        return rv

class ValidationError(APIError):
    """Raised when input validation fails"""
    def __init__(self, message, payload=None):
        super().__init__(message, status_code=400, payload=payload)

class AuthenticationError(APIError):
    """Raised when authentication fails"""
    def __init__(self, message, payload=None):
        super().__init__(message, status_code=401, payload=payload)

class AuthorizationError(APIError):
    """Raised when authorization fails"""
    def __init__(self, message, payload=None):
        super().__init__(message, status_code=403, payload=payload)

class NotFoundError(APIError):
    """Raised when a resource is not found"""
    def __init__(self, message, payload=None):
        super().__init__(message, status_code=404, payload=payload)

def handle_error(error):
    """Handle and format errors consistently"""
    if isinstance(error, APIError):
        response = jsonify(error.to_dict())
        response.status_code = error.status_code
        return response
    
    # Log unexpected errors
    logger.error(f"Unexpected error: {str(error)}")
    logger.error(traceback.format_exc())
    
    # Return generic error for unexpected errors
    response = jsonify({
        'status': 'error',
        'message': 'An unexpected error occurred'
    })
    response.status_code = 500
    return response

def error_handler(f):
    """Decorator to handle errors in route handlers"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception as e:
            return handle_error(e)
    return decorated_function

def validate_required_fields(data, required_fields):
    """Validate that all required fields are present in the data"""
    missing_fields = [field for field in required_fields if field not in data]
    if missing_fields:
        raise ValidationError(
            f"Missing required fields: {', '.join(missing_fields)}"
        )

def validate_field_type(field_name, field_value, expected_type):
    """Validate that a field is of the expected type"""
    if not isinstance(field_value, expected_type):
        raise ValidationError(
            f"Field '{field_name}' must be of type {expected_type.__name__}"
        )

def validate_field_length(field_name, field_value, min_length=None, max_length=None):
    """Validate that a field's length is within the specified range"""
    if min_length is not None and len(field_value) < min_length:
        raise ValidationError(
            f"Field '{field_name}' must be at least {min_length} characters long"
        )
    if max_length is not None and len(field_value) > max_length:
        raise ValidationError(
            f"Field '{field_name}' must be at most {max_length} characters long"
        )

def validate_email(email):
    """Validate email format"""
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(pattern, email):
        raise ValidationError("Invalid email format")

def validate_password(password):
    """Validate password strength"""
    if len(password) < 8:
        raise ValidationError("Password must be at least 8 characters long")
    if not any(c.isupper() for c in password):
        raise ValidationError("Password must contain at least one uppercase letter")
    if not any(c.islower() for c in password):
        raise ValidationError("Password must contain at least one lowercase letter")
    if not any(c.isdigit() for c in password):
        raise ValidationError("Password must contain at least one number")
    if not any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
        raise ValidationError("Password must contain at least one special character") 