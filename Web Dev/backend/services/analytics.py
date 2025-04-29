from datetime import datetime, timedelta
from ..database import get_db
from ..utils.error_handlers import handle_error

def track_page_view(website_id):
    """Track a page view for a website"""
    try:
        db = get_db()
        today = datetime.now().date()
        
        # Check if there's already a record for today
        existing_record = db.execute(
            '''
            SELECT * FROM website_analytics 
            WHERE website_id = ? AND date = ?
            ''',
            (website_id, today)
        ).fetchone()
        
        if existing_record:
            # Update existing record
            db.execute(
                '''
                UPDATE website_analytics 
                SET page_views = page_views + 1
                WHERE id = ?
                ''',
                (existing_record['id'],)
            )
        else:
            # Create new record
            db.execute(
                '''
                INSERT INTO website_analytics (website_id, page_views, date)
                VALUES (?, 1, ?)
                ''',
                (website_id, today)
            )
        
        db.commit()
        
    except Exception as e:
        raise handle_error(e)

def track_unique_visitor(website_id, visitor_id):
    """Track a unique visitor for a website"""
    try:
        db = get_db()
        today = datetime.now().date()
        
        # Check if there's already a record for today
        existing_record = db.execute(
            '''
            SELECT * FROM website_analytics 
            WHERE website_id = ? AND date = ?
            ''',
            (website_id, today)
        ).fetchone()
        
        if existing_record:
            # Update existing record
            db.execute(
                '''
                UPDATE website_analytics 
                SET unique_visitors = unique_visitors + 1
                WHERE id = ?
                ''',
                (existing_record['id'],)
            )
        else:
            # Create new record
            db.execute(
                '''
                INSERT INTO website_analytics (website_id, unique_visitors, date)
                VALUES (?, 1, ?)
                ''',
                (website_id, today)
            )
        
        db.commit()
        
    except Exception as e:
        raise handle_error(e)

def get_website_analytics(website_id, start_date=None, end_date=None):
    """Get analytics data for a website"""
    try:
        db = get_db()
        
        # Set default date range if not provided
        if not end_date:
            end_date = datetime.now().date()
        if not start_date:
            start_date = end_date - timedelta(days=30)
        
        # Get analytics data
        analytics = db.execute(
            '''
            SELECT * FROM website_analytics 
            WHERE website_id = ? AND date BETWEEN ? AND ?
            ORDER BY date DESC
            ''',
            (website_id, start_date, end_date)
        ).fetchall()
        
        # Calculate totals
        total_views = sum(record['page_views'] for record in analytics)
        total_visitors = sum(record['unique_visitors'] for record in analytics)
        
        # Calculate daily averages
        days = (end_date - start_date).days + 1
        avg_daily_views = total_views / days if days > 0 else 0
        avg_daily_visitors = total_visitors / days if days > 0 else 0
        
        return {
            'total_views': total_views,
            'total_visitors': total_visitors,
            'avg_daily_views': avg_daily_views,
            'avg_daily_visitors': avg_daily_visitors,
            'daily_data': [dict(record) for record in analytics]
        }
        
    except Exception as e:
        raise handle_error(e)

def generate_analytics_report(website_id, start_date=None, end_date=None):
    """Generate a detailed analytics report for a website"""
    try:
        analytics_data = get_website_analytics(website_id, start_date, end_date)
        
        # Get website info
        db = get_db()
        website = db.execute(
            'SELECT * FROM websites WHERE id = ?',
            (website_id,)
        ).fetchone()
        
        if not website:
            raise ValueError('Website not found')
        
        # Generate report
        report = {
            'website_name': website['business_name'],
            'report_period': {
                'start_date': start_date,
                'end_date': end_date
            },
            'overview': {
                'total_page_views': analytics_data['total_views'],
                'total_unique_visitors': analytics_data['total_visitors'],
                'avg_daily_views': analytics_data['avg_daily_views'],
                'avg_daily_visitors': analytics_data['avg_daily_visitors']
            },
            'daily_breakdown': analytics_data['daily_data'],
            'generated_at': datetime.now().isoformat()
        }
        
        return report
        
    except Exception as e:
        raise handle_error(e) 