"""
Database models for the Concierge event aggregation system.
"""
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func

db = SQLAlchemy()


class Source(db.Model):
    """Event sources (ICS feeds, Slack channels, Forum, etc.)"""
    __tablename__ = 'sources'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    type = db.Column(db.String(50), nullable=False)  # 'ics', 'slack', 'telegram', 'forum', 'manual'
    url = db.Column(db.String(500))  # ICS URL or API endpoint
    credentials = db.Column(db.Text)  # JSON string for API tokens (encrypted in production)
    active = db.Column(db.Boolean, default=True)
    last_fetched = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    events = db.relationship('Event', back_populates='source', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Source {self.name} ({self.type})>'


class Event(db.Model):
    """Normalized event schema"""
    __tablename__ = 'events'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Core fields
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    start_time = db.Column(db.DateTime, nullable=False, index=True)
    end_time = db.Column(db.DateTime)
    timezone = db.Column(db.String(50), default='UTC')
    
    # Location
    location = db.Column(db.String(200))
    is_virtual = db.Column(db.Boolean, default=False)
    meeting_link = db.Column(db.String(500))
    
    # Metadata
    tag = db.Column(db.String(50), index=True)  # Required, Career, Capstone, Social, Deadline
    rsvp_link = db.Column(db.String(500))
    why_matters = db.Column(db.Text)  # One-line explanation
    
    # Source tracking
    source_id = db.Column(db.Integer, db.ForeignKey('sources.id'), nullable=False)
    source_event_id = db.Column(db.String(200))  # Original ID from source (for dedup)
    
    # Deduplication
    fingerprint = db.Column(db.String(64), unique=True, index=True)  # Hash for dedup
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    source = db.relationship('Source', back_populates='events')
    
    def __repr__(self):
        return f'<Event {self.title} at {self.start_time}>'
    
    def to_dict(self):
        """Convert to dictionary for API responses"""
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'timezone': self.timezone,
            'location': self.location,
            'is_virtual': self.is_virtual,
            'meeting_link': self.meeting_link,
            'tag': self.tag,
            'rsvp_link': self.rsvp_link,
            'why_matters': self.why_matters,
            'source': {
                'id': self.source.id,
                'name': self.source.name,
                'type': self.source.type
            } if self.source else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class User(db.Model):
    """Users who subscribe to digests"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    name = db.Column(db.String(100))
    
    # Digest preferences
    digest_08_enabled = db.Column(db.Boolean, default=True)
    digest_15_enabled = db.Column(db.Boolean, default=False)
    timezone = db.Column(db.String(50), default='America/Los_Angeles')
    
    # Telegram (optional)
    telegram_chat_id = db.Column(db.String(50))
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    subscriptions = db.relationship('Subscription', back_populates='user', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<User {self.email}>'


class Subscription(db.Model):
    """User tag subscriptions (Required, Career, Capstone, Social, Deadline)"""
    __tablename__ = 'subscriptions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    tag = db.Column(db.String(50), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', back_populates='subscriptions')
    
    __table_args__ = (
        db.UniqueConstraint('user_id', 'tag', name='unique_user_tag'),
    )
    
    def __repr__(self):
        return f'<Subscription user={self.user_id} tag={self.tag}>'


class DigestLog(db.Model):
    """Track digest deliveries for monitoring"""
    __tablename__ = 'digest_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    digest_type = db.Column(db.String(20), nullable=False)  # '08:00' or '15:00'
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    event_count = db.Column(db.Integer, default=0)
    sent_at = db.Column(db.DateTime, default=datetime.utcnow)
    success = db.Column(db.Boolean, default=True)
    error_message = db.Column(db.Text)
    
    def __repr__(self):
        return f'<DigestLog {self.digest_type} sent={self.sent_at}>'
