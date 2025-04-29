from flask import Blueprint, jsonify
import sqlite3
import os
import psutil
import time

health_bp = Blueprint('health', __name__)

@health_bp.route('/health')
def health_check():
    """Check the health of the application"""
    status = {
        'status': 'healthy',
        'timestamp': time.time(),
        'components': {
            'database': check_database(),
            'disk': check_disk_space(),
            'memory': check_memory_usage(),
            'uptime': get_uptime()
        }
    }
    
    # Check if any component is unhealthy
    if any(comp.get('status') == 'unhealthy' for comp in status['components'].values()):
        status['status'] = 'unhealthy'
    
    return jsonify(status)

def check_database():
    """Check database connection and size"""
    try:
        conn = sqlite3.connect('database/3clickbuilder.db')
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM websites')
        count = cursor.fetchone()[0]
        conn.close()
        
        return {
            'status': 'healthy',
            'message': 'Database connection successful',
            'websites_count': count
        }
    except Exception as e:
        return {
            'status': 'unhealthy',
            'message': f'Database error: {str(e)}'
        }

def check_disk_space():
    """Check available disk space"""
    try:
        disk = psutil.disk_usage('/')
        return {
            'status': 'healthy' if disk.percent < 90 else 'unhealthy',
            'message': f'Disk usage: {disk.percent}%',
            'free_space': f'{disk.free / (1024**3):.2f} GB'
        }
    except Exception as e:
        return {
            'status': 'unhealthy',
            'message': f'Disk check error: {str(e)}'
        }

def check_memory_usage():
    """Check memory usage"""
    try:
        memory = psutil.virtual_memory()
        return {
            'status': 'healthy' if memory.percent < 90 else 'unhealthy',
            'message': f'Memory usage: {memory.percent}%',
            'available': f'{memory.available / (1024**3):.2f} GB'
        }
    except Exception as e:
        return {
            'status': 'unhealthy',
            'message': f'Memory check error: {str(e)}'
        }

def get_uptime():
    """Get system uptime"""
    try:
        uptime = time.time() - psutil.boot_time()
        return {
            'status': 'healthy',
            'message': f'System uptime: {uptime:.2f} seconds'
        }
    except Exception as e:
        return {
            'status': 'unhealthy',
            'message': f'Uptime check error: {str(e)}'
        } 