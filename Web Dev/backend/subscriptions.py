from flask import Blueprint, request, jsonify
import stripe
import sqlite3
from datetime import datetime
import os
from dotenv import load_dotenv
from .auth import token_required

load_dotenv()

stripe.api_key = os.getenv('STRIPE_SECRET_KEY')
subscriptions_bp = Blueprint('subscriptions', __name__)

def get_db():
    conn = sqlite3.connect('database/3clickbuilder.db')
    conn.row_factory = sqlite3.Row
    return conn

@subscriptions_bp.route('/plans', methods=['GET'])
def get_plans():
    """Get available subscription plans"""
    plans = [
        {
            'id': 'basic',
            'name': 'Basic',
            'price': 9.99,
            'features': [
                '1 Website',
                'Basic Templates',
                'PDF Generation',
                'Email Support'
            ]
        },
        {
            'id': 'pro',
            'name': 'Professional',
            'price': 19.99,
            'features': [
                '5 Websites',
                'Premium Templates',
                'PDF Generation',
                'Priority Support',
                'Custom Domain'
            ]
        },
        {
            'id': 'enterprise',
            'name': 'Enterprise',
            'price': 49.99,
            'features': [
                'Unlimited Websites',
                'All Templates',
                'PDF Generation',
                '24/7 Support',
                'Custom Domain',
                'API Access'
            ]
        }
    ]
    return jsonify(plans)

@subscriptions_bp.route('/subscribe', methods=['POST'])
@token_required
def create_subscription(current_user):
    """Create a new subscription"""
    data = request.get_json()
    
    if not data or not data.get('plan_id'):
        return jsonify({'message': 'Missing plan ID!'}), 400
    
    try:
        # Create Stripe customer
        customer = stripe.Customer.create(
            email=current_user['email'],
            source=data.get('payment_method')
        )
        
        # Create subscription
        subscription = stripe.Subscription.create(
            customer=customer.id,
            items=[{'price': data['plan_id']}]
        )
        
        # Store subscription in database
        conn = get_db()
        conn.execute('''
            INSERT INTO subscriptions (user_id, stripe_customer_id, stripe_subscription_id, status)
            VALUES (?, ?, ?, ?)
        ''', (
            current_user['id'],
            customer.id,
            subscription.id,
            subscription.status
        ))
        conn.commit()
        conn.close()
        
        return jsonify({
            'message': 'Subscription created successfully!',
            'subscription_id': subscription.id
        })
    except Exception as e:
        return jsonify({'message': str(e)}), 400

@subscriptions_bp.route('/subscription', methods=['GET'])
@token_required
def get_subscription(current_user):
    """Get current subscription details"""
    conn = get_db()
    subscription = conn.execute('''
        SELECT * FROM subscriptions 
        WHERE user_id = ? 
        ORDER BY created_at DESC 
        LIMIT 1
    ''', (current_user['id'],)).fetchone()
    conn.close()
    
    if not subscription:
        return jsonify({'message': 'No active subscription!'}), 404
    
    try:
        stripe_subscription = stripe.Subscription.retrieve(subscription['stripe_subscription_id'])
        return jsonify({
            'status': stripe_subscription.status,
            'current_period_end': stripe_subscription.current_period_end,
            'plan': stripe_subscription.plan.id
        })
    except Exception as e:
        return jsonify({'message': str(e)}), 400

@subscriptions_bp.route('/subscription/cancel', methods=['POST'])
@token_required
def cancel_subscription(current_user):
    """Cancel current subscription"""
    conn = get_db()
    subscription = conn.execute('''
        SELECT * FROM subscriptions 
        WHERE user_id = ? 
        ORDER BY created_at DESC 
        LIMIT 1
    ''', (current_user['id'],)).fetchone()
    conn.close()
    
    if not subscription:
        return jsonify({'message': 'No active subscription!'}), 404
    
    try:
        stripe.Subscription.delete(subscription['stripe_subscription_id'])
        
        conn = get_db()
        conn.execute('''
            UPDATE subscriptions 
            SET status = 'canceled' 
            WHERE id = ?
        ''', (subscription['id'],))
        conn.commit()
        conn.close()
        
        return jsonify({'message': 'Subscription canceled successfully!'})
    except Exception as e:
        return jsonify({'message': str(e)}), 400 