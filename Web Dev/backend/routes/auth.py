from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
from datetime import datetime, timedelta
import os
from ..models.user import User
from ..database import get_db
from ..utils.validators import validate_email, validate_password
from ..utils.error_handlers import handle_error

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        
        # Validate input
        if not all(k in data for k in ('email', 'password', 'full_name')):
            return jsonify({'error': 'Missing required fields'}), 400
            
        if not validate_email(data['email']):
            return jsonify({'error': 'Invalid email format'}), 400
            
        if not validate_password(data['password']):
            return jsonify({'error': 'Password must be at least 8 characters long'}), 400
        
        # Check if user already exists
        db = get_db()
        existing_user = db.execute(
            'SELECT id FROM users WHERE email = ?', 
            (data['email'],)
        ).fetchone()
        
        if existing_user:
            return jsonify({'error': 'Email already registered'}), 409
        
        # Create new user
        hashed_password = generate_password_hash(data['password'])
        cursor = db.execute(
            '''
            INSERT INTO users (email, password_hash, full_name, created_at)
            VALUES (?, ?, ?, ?)
            ''',
            (data['email'], hashed_password, data['full_name'], datetime.now())
        )
        db.commit()
        
        # Generate token
        user_id = cursor.lastrowid
        token = generate_token(user_id)
        
        return jsonify({
            'token': token,
            'user': {
                'id': user_id,
                'email': data['email'],
                'full_name': data['full_name']
            }
        }), 201
        
    except Exception as e:
        return handle_error(e)

@auth_bp.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        
        if not all(k in data for k in ('email', 'password')):
            return jsonify({'error': 'Missing email or password'}), 400
        
        # Get user from database
        db = get_db()
        user = db.execute(
            'SELECT * FROM users WHERE email = ?',
            (data['email'],)
        ).fetchone()
        
        if not user or not check_password_hash(user['password_hash'], data['password']):
            return jsonify({'error': 'Invalid email or password'}), 401
        
        # Update last login
        db.execute(
            'UPDATE users SET last_login = ? WHERE id = ?',
            (datetime.now(), user['id'])
        )
        db.commit()
        
        # Generate token
        token = generate_token(user['id'])
        
        return jsonify({
            'token': token,
            'user': {
                'id': user['id'],
                'email': user['email'],
                'full_name': user['full_name']
            }
        })
        
    except Exception as e:
        return handle_error(e)

@auth_bp.route('/logout', methods=['POST'])
def logout():
    try:
        # In a real application, you might want to blacklist the token
        # For now, we'll just return a success message
        return jsonify({'message': 'Successfully logged out'})
        
    except Exception as e:
        return handle_error(e)

@auth_bp.route('/me', methods=['GET'])
def get_current_user():
    try:
        # Get token from header
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'error': 'Missing or invalid token'}), 401
            
        token = auth_header.split(' ')[1]
        
        # Verify token
        try:
            payload = jwt.decode(
                token,
                os.getenv('JWT_SECRET_KEY'),
                algorithms=['HS256']
            )
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Invalid token'}), 401
        
        # Get user from database
        db = get_db()
        user = db.execute(
            'SELECT * FROM users WHERE id = ?',
            (payload['user_id'],)
        ).fetchone()
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        return jsonify({
            'id': user['id'],
            'email': user['email'],
            'full_name': user['full_name'],
            'created_at': user['created_at'],
            'last_login': user['last_login']
        })
        
    except Exception as e:
        return handle_error(e)

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