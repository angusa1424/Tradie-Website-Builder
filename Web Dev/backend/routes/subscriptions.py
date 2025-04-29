from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta
import stripe
import os
from ..database import get_db
from ..utils.error_handlers import handle_error
from ..utils.auth import login_required, subscription_required

subscriptions_bp = Blueprint('subscriptions', __name__)

# Initialize Stripe
stripe.api_key = os.getenv('STRIPE_SECRET_KEY')

# Define subscription plans
SUBSCRIPTION_PLANS = {
    'tradie': {
        'name': 'Tradie Website Package',
        'setup_fee': 299.95,
        'monthly_fee': 29.95,
        'stripe_price_id': os.getenv('STRIPE_TRADIE_PRICE_ID'),
        'features': [
            'Professional tradie website',
            'Mobile-friendly design',
            'Custom domain (.com.au)',
            'Contact form',
            'Service showcase',
            'Photo gallery',
            'Customer testimonials',
            'Google Maps integration',
            'Business hours display',
            'Emergency contact section',
            'SSL security certificate',
            'Basic SEO setup',
            'Social media integration',
            'Monthly backups',
            'Email support',
            'Free updates'
        ],
        'limits': {
            'websites': 1,
            'page_views': 10000,
            'storage': '5GB',
            'bandwidth': '50GB'
        }
    }
}

@subscriptions_bp.route('/plans', methods=['GET'])
def get_plans():
    """Get available subscription plans"""
    try:
        return jsonify({
            'plans': SUBSCRIPTION_PLANS
        })
    except Exception as e:
        return handle_error(e)

@subscriptions_bp.route('/subscribe', methods=['POST'])
@login_required
def create_subscription():
    try:
        data = request.get_json()
        user_id = request.user['id']
        
        if 'payment_method_id' not in data:
            return jsonify({'error': 'Payment method is required'}), 400
            
        # Get or create Stripe customer
        db = get_db()
        user = db.execute(
            'SELECT * FROM users WHERE id = ?',
            (user_id,)
        ).fetchone()
        
        if not user['stripe_customer_id']:
            customer = stripe.Customer.create(
                email=user['email'],
                payment_method=data['payment_method_id'],
                invoice_settings={'default_payment_method': data['payment_method_id']}
            )
            db.execute(
                'UPDATE users SET stripe_customer_id = ? WHERE id = ?',
                (customer.id, user_id)
            )
        else:
            customer = stripe.Customer.retrieve(user['stripe_customer_id'])
        
        # Create setup fee invoice
        setup_invoice = stripe.Invoice.create(
            customer=customer.id,
            collection_method='charge_automatically',
            pending_invoice_items_behavior='exclude',
            items=[{
                'price_data': {
                    'unit_amount': int(SUBSCRIPTION_PLANS['tradie']['setup_fee'] * 100),
                    'currency': 'aud',
                    'product_data': {
                        'name': 'Website Setup Fee',
                        'description': 'One-time setup fee for your tradie website'
                    }
                },
                'quantity': 1
            }]
        )
        
        # Create monthly subscription
        subscription = stripe.Subscription.create(
            customer=customer.id,
            items=[{
                'price_data': {
                    'unit_amount': int(SUBSCRIPTION_PLANS['tradie']['monthly_fee'] * 100),
                    'currency': 'aud',
                    'recurring': {
                        'interval': 'month'
                    },
                    'product_data': {
                        'name': 'Monthly Website Hosting',
                        'description': 'Monthly hosting and maintenance for your tradie website'
                    }
                },
                'quantity': 1
            }],
            expand=['latest_invoice.payment_intent']
        )
        
        # Update user's subscription in database
        db.execute(
            '''
            INSERT INTO subscriptions (
                user_id, stripe_customer_id, stripe_subscription_id,
                plan_type, status, start_date, end_date
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ''',
            (
                user_id,
                customer.id,
                subscription.id,
                'tradie',
                subscription.status,
                datetime.now(),
                datetime.fromtimestamp(subscription.current_period_end)
            )
        )
        db.commit()
        
        return jsonify({
            'message': 'Subscription created successfully',
            'subscription': subscription,
            'setup_invoice': setup_invoice,
            'plan': SUBSCRIPTION_PLANS['tradie']
        })
        
    except Exception as e:
        return handle_error(e)

@subscriptions_bp.route('/cancel', methods=['POST'])
@login_required
def cancel_subscription():
    try:
        user_id = request.user['id']
        
        # Get user's subscription
        db = get_db()
        subscription = db.execute(
            '''
            SELECT * FROM subscriptions 
            WHERE user_id = ? AND status = 'active'
            ''',
            (user_id,)
        ).fetchone()
        
        if not subscription:
            return jsonify({'error': 'No active subscription found'}), 404
        
        # Cancel Stripe subscription
        stripe.Subscription.delete(subscription['stripe_subscription_id'])
        
        # Update subscription in database
        db.execute(
            '''
            UPDATE subscriptions 
            SET status = 'canceled', end_date = ?
            WHERE id = ?
            ''',
            (datetime.now(), subscription['id'])
        )
        db.commit()
        
        return jsonify({
            'message': 'Subscription canceled successfully'
        })
        
    except Exception as e:
        return handle_error(e)

@subscriptions_bp.route('/current', methods=['GET'])
@login_required
def get_current_subscription():
    try:
        user_id = request.user['id']
        
        # Get user's subscription
        db = get_db()
        subscription = db.execute(
            '''
            SELECT * FROM subscriptions 
            WHERE user_id = ? AND status = 'active'
            ''',
            (user_id,)
        ).fetchone()
        
        if not subscription:
            return jsonify({
                'plan': SUBSCRIPTION_PLANS['free'],
                'status': 'free'
            })
        
        return jsonify({
            'subscription': dict(subscription),
            'plan': SUBSCRIPTION_PLANS[subscription['plan_type']]
        })
        
    except Exception as e:
        return handle_error(e) 