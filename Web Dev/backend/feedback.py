from flask import Blueprint, request, jsonify
from datetime import datetime
import sqlite3
import json
import os
from pathlib import Path

feedback_bp = Blueprint('feedback', __name__)

def init_feedback_db():
    """Initialize the feedback database"""
    db_path = Path('database/feedback.db')
    db_path.parent.mkdir(exist_ok=True)
    
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            type TEXT NOT NULL,
            message TEXT NOT NULL,
            email TEXT,
            rating INTEGER,
            timestamp TEXT NOT NULL,
            user_agent TEXT,
            url TEXT,
            status TEXT DEFAULT 'new'
        )
    ''')
    conn.commit()
    conn.close()

@feedback_bp.route('/api/feedback', methods=['POST'])
def submit_feedback():
    """Handle feedback submissions"""
    try:
        data = request.json
        
        # Validate required fields
        required_fields = ['type', 'message']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Connect to database
        conn = sqlite3.connect('database/feedback.db')
        c = conn.cursor()
        
        # Insert feedback
        c.execute('''
            INSERT INTO feedback (
                type, message, email, rating, timestamp, user_agent, url
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            data['type'],
            data['message'],
            data.get('email'),
            data.get('rating', 0),
            data.get('timestamp', datetime.now().isoformat()),
            data.get('userAgent'),
            data.get('url')
        ))
        
        conn.commit()
        feedback_id = c.lastrowid
        
        # Log feedback to file for backup
        log_feedback(data, feedback_id)
        
        conn.close()
        
        return jsonify({
            'message': 'Feedback submitted successfully',
            'id': feedback_id
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def log_feedback(data, feedback_id):
    """Log feedback to a JSON file for backup"""
    log_dir = Path('logs')
    log_dir.mkdir(exist_ok=True)
    
    log_file = log_dir / 'feedback.json'
    
    # Create or load existing log
    if log_file.exists():
        with open(log_file, 'r') as f:
            logs = json.load(f)
    else:
        logs = []
    
    # Add new feedback
    logs.append({
        'id': feedback_id,
        'timestamp': datetime.now().isoformat(),
        'data': data
    })
    
    # Save updated log
    with open(log_file, 'w') as f:
        json.dump(logs, f, indent=2)

@feedback_bp.route('/api/feedback/stats', methods=['GET'])
def get_feedback_stats():
    """Get feedback statistics"""
    try:
        conn = sqlite3.connect('database/feedback.db')
        c = conn.cursor()
        
        # Get total feedback count
        c.execute('SELECT COUNT(*) FROM feedback')
        total_count = c.fetchone()[0]
        
        # Get feedback by type
        c.execute('''
            SELECT type, COUNT(*) as count
            FROM feedback
            GROUP BY type
        ''')
        type_stats = dict(c.fetchall())
        
        # Get average rating
        c.execute('SELECT AVG(rating) FROM feedback WHERE rating > 0')
        avg_rating = c.fetchone()[0] or 0
        
        # Get recent feedback
        c.execute('''
            SELECT id, type, message, rating, timestamp
            FROM feedback
            ORDER BY timestamp DESC
            LIMIT 5
        ''')
        recent_feedback = [
            {
                'id': row[0],
                'type': row[1],
                'message': row[2],
                'rating': row[3],
                'timestamp': row[4]
            }
            for row in c.fetchall()
        ]
        
        conn.close()
        
        return jsonify({
            'total_count': total_count,
            'type_stats': type_stats,
            'average_rating': round(avg_rating, 1),
            'recent_feedback': recent_feedback
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Initialize database when module is imported
init_feedback_db() 