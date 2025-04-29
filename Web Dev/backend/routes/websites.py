from flask import Blueprint, request, jsonify
from datetime import datetime
import json
from ..database import get_db
from ..utils.error_handlers import handle_error
from ..utils.auth import login_required
from ..services.website_generator import generate_website_html
from ..services.analytics import track_page_view
from ..services.version_control import create_version, get_versions, restore_version

websites_bp = Blueprint('websites', __name__)

@websites_bp.route('/create', methods=['POST'])
@login_required
def create_website():
    try:
        data = request.get_json()
        user_id = request.user['id']
        
        # Validate required fields
        required_fields = [
            'businessName', 'phone', 'email', 'address',
            'services', 'businessHours', 'location', 'template'
        ]
        
        if not all(field in data for field in required_fields):
            return jsonify({'error': 'Missing required fields'}), 400
        
        # Generate website HTML
        html_content = generate_website_html(data)
        
        # Create website in database
        db = get_db()
        cursor = db.execute(
            '''
            INSERT INTO websites (
                user_id, business_name, template, content, 
                published_url, created_at, updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ''',
            (
                user_id,
                data['businessName'],
                data['template'],
                json.dumps(data),
                f"{data['businessName'].lower().replace(' ', '-')}",
                datetime.now(),
                datetime.now()
            )
        )
        db.commit()
        
        website_id = cursor.lastrowid
        
        return jsonify({
            'id': website_id,
            'message': 'Website created successfully',
            'url': f"https://{data['businessName'].lower().replace(' ', '-')}"
        }), 201
        
    except Exception as e:
        return handle_error(e)

@websites_bp.route('/', methods=['GET'])
@login_required
def get_websites():
    try:
        user_id = request.user['id']
        db = get_db()
        
        websites = db.execute(
            '''
            SELECT * FROM websites 
            WHERE user_id = ?
            ORDER BY created_at DESC
            ''',
            (user_id,)
        ).fetchall()
        
        return jsonify([dict(website) for website in websites])
        
    except Exception as e:
        return handle_error(e)

@websites_bp.route('/<int:website_id>', methods=['GET'])
def get_website(website_id):
    try:
        db = get_db()
        website = db.execute(
            'SELECT * FROM websites WHERE id = ?',
            (website_id,)
        ).fetchone()
        
        if not website:
            return jsonify({'error': 'Website not found'}), 404
        
        # Track page view if website is published
        if website['is_published']:
            track_page_view(website_id)
        
        return jsonify(dict(website))
        
    except Exception as e:
        return handle_error(e)

@websites_bp.route('/<int:website_id>', methods=['PUT'])
@login_required
def update_website(website_id):
    try:
        data = request.get_json()
        user_id = request.user['id']
        
        # Verify ownership
        db = get_db()
        website = db.execute(
            'SELECT * FROM websites WHERE id = ? AND user_id = ?',
            (website_id, user_id)
        ).fetchone()
        
        if not website:
            return jsonify({'error': 'Website not found'}), 404
        
        # Generate new HTML
        html_content = generate_website_html(data)
        
        # Update website
        db.execute(
            '''
            UPDATE websites 
            SET content = ?, updated_at = ?
            WHERE id = ?
            ''',
            (json.dumps(data), datetime.now(), website_id)
        )
        db.commit()
        
        return jsonify({'message': 'Website updated successfully'})
        
    except Exception as e:
        return handle_error(e)

@websites_bp.route('/<int:website_id>', methods=['DELETE'])
@login_required
def delete_website(website_id):
    try:
        user_id = request.user['id']
        
        # Verify ownership
        db = get_db()
        website = db.execute(
            'SELECT * FROM websites WHERE id = ? AND user_id = ?',
            (website_id, user_id)
        ).fetchone()
        
        if not website:
            return jsonify({'error': 'Website not found'}), 404
        
        # Delete website
        db.execute('DELETE FROM websites WHERE id = ?', (website_id,))
        db.commit()
        
        return jsonify({'message': 'Website deleted successfully'})
        
    except Exception as e:
        return handle_error(e)

@websites_bp.route('/<int:website_id>/publish', methods=['POST'])
@login_required
def publish_website(website_id):
    try:
        user_id = request.user['id']
        
        # Verify ownership
        db = get_db()
        website = db.execute(
            'SELECT * FROM websites WHERE id = ? AND user_id = ?',
            (website_id, user_id)
        ).fetchone()
        
        if not website:
            return jsonify({'error': 'Website not found'}), 404
        
        # Update publish status
        db.execute(
            'UPDATE websites SET is_published = TRUE WHERE id = ?',
            (website_id,)
        )
        db.commit()
        
        return jsonify({
            'message': 'Website published successfully',
            'url': f"https://{website['published_url']}"
        })
        
    except Exception as e:
        return handle_error(e)

@websites_bp.route('/<int:website_id>/versions', methods=['GET'])
@login_required
def get_website_versions(website_id):
    try:
        user_id = request.user['id']
        
        # Verify ownership
        db = get_db()
        website = db.execute(
            'SELECT * FROM websites WHERE id = ? AND user_id = ?',
            (website_id, user_id)
        ).fetchone()
        
        if not website:
            return jsonify({'error': 'Website not found'}), 404
        
        versions = get_versions(website_id)
        return jsonify(versions)
        
    except Exception as e:
        return handle_error(e)

@websites_bp.route('/<int:website_id>/versions/<int:version_id>/restore', methods=['POST'])
@login_required
def restore_website_version(website_id, version_id):
    try:
        user_id = request.user['id']
        
        # Verify ownership
        db = get_db()
        website = db.execute(
            'SELECT * FROM websites WHERE id = ? AND user_id = ?',
            (website_id, user_id)
        ).fetchone()
        
        if not website:
            return jsonify({'error': 'Website not found'}), 404
        
        # Restore version
        content = restore_version(website_id, version_id)
        
        # Update website content
        db.execute(
            '''
            UPDATE websites 
            SET content = ?, updated_at = ?
            WHERE id = ?
            ''',
            (json.dumps(content), datetime.now(), website_id)
        )
        db.commit()
        
        return jsonify({'message': 'Version restored successfully'})
        
    except Exception as e:
        return handle_error(e) 