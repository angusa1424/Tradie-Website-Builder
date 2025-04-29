from flask import request, make_response
import re

class SecurityHeaders:
    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        # Process the request
        response = self.app(environ, start_response)
        
        # Add security headers
        response = make_response(response)
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'SAMEORIGIN'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        response.headers['Content-Security-Policy'] = "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval'; style-src 'self' 'unsafe-inline';"
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        response.headers['Permissions-Policy'] = 'geolocation=(), microphone=(), camera=()'
        
        return response

def sanitize_input(data):
    """Sanitize user input to prevent XSS attacks"""
    if isinstance(data, str):
        # Remove potentially dangerous characters
        data = re.sub(r'[<>]', '', data)
        # Escape special characters
        data = data.replace('&', '&amp;')
        data = data.replace('"', '&quot;')
        data = data.replace("'", '&#x27;')
        data = data.replace('/', '&#x2F;')
    return data

def validate_business_name(name):
    """Validate business name format"""
    if not name or len(name) > 100:
        return False
    # Allow letters, numbers, spaces, and basic punctuation
    return bool(re.match(r'^[a-zA-Z0-9\s\-\.\']+$', name))

def validate_service_type(service_type):
    """Validate service type format"""
    if not service_type or len(service_type) > 50:
        return False
    # Allow letters, numbers, spaces, and basic punctuation
    return bool(re.match(r'^[a-zA-Z0-9\s\-\.\']+$', service_type))

def validate_location(location):
    """Validate location format"""
    if not location or len(location) > 100:
        return False
    # Allow letters, numbers, spaces, and basic punctuation
    return bool(re.match(r'^[a-zA-Z0-9\s\-\.\',]+$', location)) 