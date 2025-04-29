from datetime import datetime
import json
from ..database import get_db
from ..utils.error_handlers import handle_error

def create_version(website_id, content):
    """Create a new version of a website"""
    try:
        db = get_db()
        
        # Get current version number
        current_version = db.execute(
            '''
            SELECT MAX(version_number) as max_version 
            FROM website_versions 
            WHERE website_id = ?
            ''',
            (website_id,)
        ).fetchone()
        
        version_number = (current_version['max_version'] or 0) + 1
        
        # Create new version
        db.execute(
            '''
            INSERT INTO website_versions (
                website_id, version_number, content, created_at
            )
            VALUES (?, ?, ?, ?)
            ''',
            (website_id, version_number, json.dumps(content), datetime.now())
        )
        db.commit()
        
        return version_number
        
    except Exception as e:
        raise handle_error(e)

def get_versions(website_id):
    """Get all versions of a website"""
    try:
        db = get_db()
        
        versions = db.execute(
            '''
            SELECT * FROM website_versions 
            WHERE website_id = ? 
            ORDER BY version_number DESC
            ''',
            (website_id,)
        ).fetchall()
        
        return [dict(version) for version in versions]
        
    except Exception as e:
        raise handle_error(e)

def get_version(website_id, version_number):
    """Get a specific version of a website"""
    try:
        db = get_db()
        
        version = db.execute(
            '''
            SELECT * FROM website_versions 
            WHERE website_id = ? AND version_number = ?
            ''',
            (website_id, version_number)
        ).fetchone()
        
        if not version:
            raise ValueError(f'Version {version_number} not found')
        
        return dict(version)
        
    except Exception as e:
        raise handle_error(e)

def restore_version(website_id, version_number):
    """Restore a website to a specific version"""
    try:
        # Get version content
        version = get_version(website_id, version_number)
        
        # Create new version with restored content
        create_version(website_id, json.loads(version['content']))
        
        return json.loads(version['content'])
        
    except Exception as e:
        raise handle_error(e)

def compare_versions(website_id, version1, version2):
    """Compare two versions of a website"""
    try:
        v1 = get_version(website_id, version1)
        v2 = get_version(website_id, version2)
        
        content1 = json.loads(v1['content'])
        content2 = json.loads(v2['content'])
        
        # Compare content
        differences = {
            'added': {},
            'removed': {},
            'modified': {}
        }
        
        # Compare each field
        for key in set(content1.keys()) | set(content2.keys()):
            if key not in content1:
                differences['added'][key] = content2[key]
            elif key not in content2:
                differences['removed'][key] = content1[key]
            elif content1[key] != content2[key]:
                differences['modified'][key] = {
                    'old': content1[key],
                    'new': content2[key]
                }
        
        return {
            'version1': version1,
            'version2': version2,
            'differences': differences,
            'compared_at': datetime.now().isoformat()
        }
        
    except Exception as e:
        raise handle_error(e)

def delete_version(website_id, version_number):
    """Delete a specific version of a website"""
    try:
        db = get_db()
        
        # Verify version exists
        version = get_version(website_id, version_number)
        
        # Delete version
        db.execute(
            '''
            DELETE FROM website_versions 
            WHERE website_id = ? AND version_number = ?
            ''',
            (website_id, version_number)
        )
        db.commit()
        
        return {'message': f'Version {version_number} deleted successfully'}
        
    except Exception as e:
        raise handle_error(e) 