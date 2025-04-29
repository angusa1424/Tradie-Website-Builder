from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta
import sqlite3
import json
from pathlib import Path
from .auth import token_required

analytics_bp = Blueprint('analytics', __name__)

def init_analytics_db():
    """Initialize the analytics database"""
    db_path = Path('database/analytics.db')
    db_path.parent.mkdir(exist_ok=True)
    
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    # Create tables for different types of analytics
    c.execute('''
        CREATE TABLE IF NOT EXISTS errors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            type TEXT NOT NULL,
            message TEXT NOT NULL,
            source TEXT,
            lineno INTEGER,
            colno INTEGER,
            stack TEXT,
            timestamp TEXT NOT NULL,
            user_agent TEXT,
            url TEXT
        )
    ''')
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS performance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            page_load INTEGER,
            dom_content_loaded INTEGER,
            first_paint INTEGER,
            dns_lookup INTEGER,
            tcp_connection INTEGER,
            server_response INTEGER,
            dom_processing INTEGER,
            resource_loading INTEGER,
            timestamp TEXT NOT NULL,
            url TEXT
        )
    ''')
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS user_behavior (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            type TEXT NOT NULL,
            data TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            url TEXT,
            user_agent TEXT
        )
    ''')
    
    conn.commit()
    conn.close()

@analytics_bp.route('/api/analytics/error', methods=['POST'])
def track_error():
    """Track error events"""
    try:
        data = request.json
        data['timestamp'] = data.get('timestamp', datetime.now().isoformat())
        data['user_agent'] = request.headers.get('User-Agent')
        data['url'] = request.headers.get('Referer')
        
        conn = sqlite3.connect('database/analytics.db')
        c = conn.cursor()
        
        c.execute('''
            INSERT INTO errors (
                type, message, source, lineno, colno, stack, timestamp, user_agent, url
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            data['type'],
            data['message'],
            data.get('source'),
            data.get('lineno'),
            data.get('colno'),
            data.get('stack'),
            data['timestamp'],
            data['user_agent'],
            data['url']
        ))
        
        conn.commit()
        conn.close()
        
        return jsonify({'message': 'Error tracked successfully'}), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@analytics_bp.route('/api/analytics/performance', methods=['POST'])
def track_performance():
    """Track performance metrics"""
    try:
        data = request.json
        timestamp = datetime.now().isoformat()
        url = request.headers.get('Referer')
        
        conn = sqlite3.connect('database/analytics.db')
        c = conn.cursor()
        
        c.execute('''
            INSERT INTO performance (
                page_load, dom_content_loaded, first_paint, dns_lookup,
                tcp_connection, server_response, dom_processing,
                resource_loading, timestamp, url
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            data.get('pageLoad'),
            data.get('domContentLoaded'),
            data.get('firstPaint'),
            data.get('dnsLookup'),
            data.get('tcpConnection'),
            data.get('serverResponse'),
            data.get('domProcessing'),
            data.get('resourceLoading'),
            timestamp,
            url
        ))
        
        conn.commit()
        conn.close()
        
        return jsonify({'message': 'Performance data tracked successfully'}), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@analytics_bp.route('/api/analytics/behavior', methods=['POST'])
def track_behavior():
    """Track user behavior"""
    try:
        data = request.json
        data['timestamp'] = data.get('timestamp', datetime.now().isoformat())
        data['user_agent'] = request.headers.get('User-Agent')
        data['url'] = request.headers.get('Referer')
        
        conn = sqlite3.connect('database/analytics.db')
        c = conn.cursor()
        
        c.execute('''
            INSERT INTO user_behavior (
                type, data, timestamp, url, user_agent
            ) VALUES (?, ?, ?, ?, ?)
        ''', (
            data['type'],
            json.dumps(data['data']),
            data['timestamp'],
            data['url'],
            data['user_agent']
        ))
        
        conn.commit()
        conn.close()
        
        return jsonify({'message': 'User behavior tracked successfully'}), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@analytics_bp.route('/api/analytics/stats', methods=['GET'])
def get_analytics_stats():
    """Get analytics statistics"""
    try:
        conn = sqlite3.connect('database/analytics.db')
        c = conn.cursor()
        
        # Get error statistics
        c.execute('SELECT COUNT(*) FROM errors')
        total_errors = c.fetchone()[0]
        
        c.execute('''
            SELECT type, COUNT(*) as count
            FROM errors
            GROUP BY type
        ''')
        error_types = dict(c.fetchall())
        
        # Get performance statistics
        c.execute('''
            SELECT AVG(page_load) as avg_page_load,
                   AVG(dom_content_loaded) as avg_dom_content_loaded,
                   AVG(first_paint) as avg_first_paint
            FROM performance
        ''')
        performance_stats = dict(zip(['avg_page_load', 'avg_dom_content_loaded', 'avg_first_paint'], c.fetchone()))
        
        # Get user behavior statistics
        c.execute('''
            SELECT type, COUNT(*) as count
            FROM user_behavior
            GROUP BY type
        ''')
        behavior_types = dict(c.fetchall())
        
        # Get recent errors
        c.execute('''
            SELECT type, message, timestamp
            FROM errors
            ORDER BY timestamp DESC
            LIMIT 5
        ''')
        recent_errors = [
            {
                'type': row[0],
                'message': row[1],
                'timestamp': row[2]
            }
            for row in c.fetchall()
        ]
        
        conn.close()
        
        return jsonify({
            'errors': {
                'total': total_errors,
                'by_type': error_types,
                'recent': recent_errors
            },
            'performance': performance_stats,
            'behavior': behavior_types
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@analytics_bp.route('/analytics/website/<int:website_id>', methods=['GET'])
@token_required
def get_website_analytics(current_user, website_id):
    """Get analytics for a specific website"""
    conn = sqlite3.connect('database/3clickbuilder.db')
    conn.row_factory = sqlite3.Row
    website = conn.execute('SELECT * FROM websites WHERE id = ?', (website_id,)).fetchone()
    
    if not website:
        conn.close()
        return jsonify({'message': 'Website not found!'}), 404
    
    # Get views in the last 30 days
    views = conn.execute('''
        SELECT date(created_at) as date, COUNT(*) as count
        FROM website_views
        WHERE website_id = ?
        AND created_at >= date('now', '-30 days')
        GROUP BY date(created_at)
        ORDER BY date
    ''', (website_id,)).fetchall()
    
    # Get unique visitors
    unique_visitors = conn.execute('''
        SELECT COUNT(DISTINCT visitor_id) as count
        FROM website_views
        WHERE website_id = ?
        AND created_at >= date('now', '-30 days')
    ''', (website_id,)).fetchone()
    
    # Get average time on site
    avg_time = conn.execute('''
        SELECT AVG(time_spent) as avg_time
        FROM website_views
        WHERE website_id = ?
        AND created_at >= date('now', '-30 days')
    ''', (website_id,)).fetchone()
    
    conn.close()
    
    return jsonify({
        'website_id': website_id,
        'views': [dict(row) for row in views],
        'unique_visitors': unique_visitors['count'],
        'average_time_on_site': avg_time['avg_time'] or 0
    })

@analytics_bp.route('/analytics/track', methods=['POST'])
def track_visit():
    """Track a website visit"""
    data = request.get_json()
    
    if not data or not data.get('website_id'):
        return jsonify({'message': 'Missing website ID!'}), 400
    
    conn = sqlite3.connect('database/3clickbuilder.db')
    conn.execute('''
        INSERT INTO website_views (
            website_id,
            visitor_id,
            time_spent,
            created_at
        ) VALUES (?, ?, ?, ?)
    ''', (
        data['website_id'],
        data.get('visitor_id'),
        data.get('time_spent', 0),
        datetime.now()
    ))
    conn.commit()
    conn.close()
    
    return jsonify({'message': 'Visit tracked successfully!'})

@analytics_bp.route('/analytics/summary', methods=['GET'])
@token_required
def get_analytics_summary(current_user):
    """Get analytics summary for all user's websites"""
    conn = sqlite3.connect('database/3clickbuilder.db')
    
    # Get total websites
    total_websites = conn.execute('''
        SELECT COUNT(*) as count
        FROM websites
        WHERE user_id = ?
    ''', (current_user['id'],)).fetchone()
    
    # Get total views
    total_views = conn.execute('''
        SELECT COUNT(*) as count
        FROM website_views v
        JOIN websites w ON v.website_id = w.id
        WHERE w.user_id = ?
        AND v.created_at >= date('now', '-30 days')
    ''', (current_user['id'],)).fetchone()
    
    # Get top performing websites
    top_websites = conn.execute('''
        SELECT w.id, w.business_name, COUNT(v.id) as views
        FROM websites w
        LEFT JOIN website_views v ON w.id = v.website_id
        WHERE w.user_id = ?
        AND v.created_at >= date('now', '-30 days')
        GROUP BY w.id
        ORDER BY views DESC
        LIMIT 5
    ''', (current_user['id'],)).fetchall()
    
    conn.close()
    
    return jsonify({
        'total_websites': total_websites['count'],
        'total_views_30d': total_views['count'],
        'top_websites': [dict(row) for row in top_websites]
    })

# Initialize database when module is imported
init_analytics_db() 