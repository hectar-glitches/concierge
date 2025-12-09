"""
Flask application for Concierge event aggregation system.
"""
from flask import Flask, jsonify, request
from flask_cors import CORS
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

from models import db, Event, Source, User, Subscription

# Load environment variables
load_dotenv()


def create_app():
    """Application factory"""
    app = Flask(__name__)
    
    # Configuration
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///concierge.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Initialize extensions
    db.init_app(app)
    CORS(app)
    
    return app


app = create_app()

# Initialize database tables on startup
with app.app_context():
    db.create_all()
    print("Database tables initialized")


# ============================================================================
# API Routes
# ============================================================================

@app.route('/')
def index():
    """Root endpoint - API info"""
    return jsonify({
        'name': 'Concierge API',
        'version': '1.0.0',
        'endpoints': {
            'health': '/api/health',
            'events': '/api/events',
            'sources': '/api/sources'
        }
    })

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat()
    })


@app.route('/api/events', methods=['GET'])
def get_events():
    """
    Get upcoming events with optional filters.
    
    Query parameters:
    - tag: Filter by tag (Required, Career, Capstone, Social, Deadline)
    - days: Number of days ahead (default: 7)
    - source_id: Filter by source
    """
    # Parse query parameters
    tag = request.args.get('tag')
    days = int(request.args.get('days', 7))
    source_id = request.args.get('source_id', type=int)
    
    # Build query
    query = Event.query.filter(Event.start_time >= datetime.utcnow())
    
    if tag:
        query = query.filter(Event.tag == tag)
    
    if source_id:
        query = query.filter(Event.source_id == source_id)
    
    # Filter by date range
    end_date = datetime.utcnow() + timedelta(days=days)
    query = query.filter(Event.start_time <= end_date)
    
    # Order by start time
    query = query.order_by(Event.start_time.asc())
    
    events = query.all()
    
    return jsonify({
        'events': [event.to_dict() for event in events],
        'count': len(events),
        'filters': {
            'tag': tag,
            'days': days,
            'source_id': source_id
        }
    })


@app.route('/api/events/today', methods=['GET'])
def get_today_events():
    """Get events happening today"""
    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    today_end = today_start + timedelta(days=1)
    
    events = Event.query.filter(
        Event.start_time >= today_start,
        Event.start_time < today_end
    ).order_by(Event.start_time.asc()).all()
    
    return jsonify({
        'events': [event.to_dict() for event in events],
        'count': len(events),
        'date': today_start.isoformat()
    })


@app.route('/api/events/<int:event_id>', methods=['GET'])
def get_event(event_id):
    """Get a single event by ID"""
    event = Event.query.get_or_404(event_id)
    return jsonify(event.to_dict())


@app.route('/api/sources', methods=['GET'])
def get_sources():
    """Get all event sources"""
    sources = Source.query.filter_by(active=True).all()
    
    return jsonify({
        'sources': [{
            'id': source.id,
            'name': source.name,
            'type': source.type,
            'last_fetched': source.last_fetched.isoformat() if source.last_fetched else None
        } for source in sources]
    })


@app.route('/api/tags', methods=['GET'])
def get_tags():
    """Get all available tags"""
    tags = db.session.query(Event.tag).distinct().filter(Event.tag.isnot(None)).all()
    
    return jsonify({
        'tags': [tag[0] for tag in tags]
    })


@app.route('/api/users', methods=['POST'])
def create_user():
    """Create a new user subscription"""
    data = request.get_json()
    
    if not data.get('email'):
        return jsonify({'error': 'Email is required'}), 400
    
    # Check if user exists
    existing_user = User.query.filter_by(email=data['email']).first()
    if existing_user:
        return jsonify({'error': 'User already exists'}), 400
    
    user = User(
        email=data['email'],
        name=data.get('name'),
        digest_08_enabled=data.get('digest_08_enabled', True),
        digest_15_enabled=data.get('digest_15_enabled', False),
        timezone=data.get('timezone', 'America/Los_Angeles'),
        telegram_chat_id=data.get('telegram_chat_id')
    )
    
    db.session.add(user)
    db.session.commit()
    
    return jsonify({
        'id': user.id,
        'email': user.email,
        'message': 'User created successfully'
    }), 201


@app.route('/api/users/<int:user_id>/subscriptions', methods=['POST'])
def add_subscription(user_id):
    """Add a tag subscription for a user"""
    user = User.query.get_or_404(user_id)
    data = request.get_json()
    
    if not data.get('tag'):
        return jsonify({'error': 'Tag is required'}), 400
    
    # Check if subscription exists
    existing = Subscription.query.filter_by(
        user_id=user_id,
        tag=data['tag']
    ).first()
    
    if existing:
        return jsonify({'error': 'Subscription already exists'}), 400
    
    subscription = Subscription(
        user_id=user_id,
        tag=data['tag']
    )
    
    db.session.add(subscription)
    db.session.commit()
    
    return jsonify({
        'id': subscription.id,
        'tag': subscription.tag,
        'message': 'Subscription added'
    }), 201


@app.route('/api/users/<int:user_id>/subscriptions', methods=['GET'])
def get_user_subscriptions(user_id):
    """Get all subscriptions for a user"""
    user = User.query.get_or_404(user_id)
    
    return jsonify({
        'user_id': user.id,
        'email': user.email,
        'subscriptions': [{'id': sub.id, 'tag': sub.tag} for sub in user.subscriptions]
    })


@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get system statistics"""
    total_events = Event.query.count()
    upcoming_events = Event.query.filter(Event.start_time >= datetime.utcnow()).count()
    total_sources = Source.query.filter_by(active=True).count()
    total_users = User.query.count()
    
    return jsonify({
        'total_events': total_events,
        'upcoming_events': upcoming_events,
        'active_sources': total_sources,
        'total_users': total_users
    })


if __name__ == '__main__':
    # Use debug=False when running in background, or use Ctrl+C to stop
    import sys
    debug_mode = sys.stdin.isatty()  # Only debug if running interactively
    app.run(debug=debug_mode, host='0.0.0.0', port=5001)
