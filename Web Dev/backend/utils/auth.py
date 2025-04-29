from functools import wraps
from flask import request, jsonify
import jwt
import os
from datetime import datetime, timedelta
from .error_handlers import AuthenticationError, AuthorizationError

def generate_token(user_id):
    """Generate JWT token for user"""
    payload = {
        'user_id': user_id,
        'exp': datetime.utcnow() + timedelta(days=1)
    }
    return jwt.encode(
        payload,
        os.getenv('JWT_SECRET_KEY'),
        algorithm='HS256'
    )

def verify_token(token):
    """Verify JWT token"""
    try:
        payload = jwt.decode(
            token,
            os.getenv('JWT_SECRET_KEY'),
            algorithms=['HS256']
        )
        return payload
    except jwt.ExpiredSignatureError:
        raise AuthenticationError('Token has expired')
    except jwt.InvalidTokenError:
        raise AuthenticationError('Invalid token')

def login_required(f):
    """Decorator to require authentication for routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        
        if not auth_header or not auth_header.startswith('Bearer '):
            raise AuthenticationError('Missing or invalid token')
        
        token = auth_header.split(' ')[1]
        payload = verify_token(token)
        
        # Add user info to request
        request.user = {'id': payload['user_id']}
        
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    """Decorator to require admin privileges for routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        
        if not auth_header or not auth_header.startswith('Bearer '):
            raise AuthenticationError('Missing or invalid token')
        
        token = auth_header.split(' ')[1]
        payload = verify_token(token)
        
        # Verify admin status
        from ..database import get_db
        db = get_db()
        user = db.execute(
            'SELECT * FROM users WHERE id = ?',
            (payload['user_id'],)
        ).fetchone()
        
        if not user or not user['is_admin']:
            raise AuthorizationError('Admin privileges required')
        
        # Add user info to request
        request.user = {
            'id': payload['user_id'],
            'is_admin': True
        }
        
        return f(*args, **kwargs)
    return decorated_function

def subscription_required(required_plan):
    """Decorator to require specific subscription plan"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            auth_header = request.headers.get('Authorization')
            
            if not auth_header or not auth_header.startswith('Bearer '):
                raise AuthenticationError('Missing or invalid token')
            
            token = auth_header.split(' ')[1]
            payload = verify_token(token)
            
            # Verify subscription
            from ..database import get_db
            db = get_db()
            user = db.execute(
                '''
                SELECT u.*, s.plan_type, s.end_date 
                FROM users u
                LEFT JOIN subscriptions s ON u.id = s.user_id
                WHERE u.id = ?
                ''',
                (payload['user_id'],)
            ).fetchone()
            
            if not user:
                raise AuthenticationError('User not found')
            
            if not user['plan_type'] or user['plan_type'] != required_plan:
                raise AuthorizationError(f'{required_plan} subscription required')
            
            if user['end_date'] and user['end_date'] < datetime.now():
                raise AuthorizationError('Subscription has expired')
            
            # Add user info to request
            request.user = {
                'id': payload['user_id'],
                'subscription': user['plan_type']
            }
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def rate_limit(limit, period):
    """Decorator to implement rate limiting"""
    from flask_limiter import Limiter
    from flask_limiter.util import get_remote_address
    
    limiter = Limiter(
        key_func=get_remote_address,
        default_limits=[f"{limit} per {period}"]
    )
    
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            return limiter.limit(f"{limit} per {period}")(f)(*args, **kwargs)
        return decorated_function
    return decorator 