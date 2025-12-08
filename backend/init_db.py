"""
Initialize the database with schema and seed data.
"""
from app import create_app
from models import db, Source
from datetime import datetime

def init_database():
    """Create tables and add initial sources"""
    app = create_app()
    
    with app.app_context():
        # Drop all tables and recreate (for development)
        db.drop_all()
        db.create_all()
        
        # Seed with example sources
        sources = [
            Source(
                name='Campus Events Calendar',
                type='ics',
                url='https://example.com/calendar.ics',
                active=True
            ),
            Source(
                name='Academic Announcements',
                type='slack',
                url='#announcements',
                active=True
            ),
            Source(
                name='Career Services',
                type='slack',
                url='#career',
                active=True
            ),
            Source(
                name='Community Portal',
                type='forum',
                url='https://forum.example.com',
                active=True
            ),
        ]
        
        for source in sources:
            db.session.add(source)
        
        db.session.commit()
        
        print("✓ Database initialized successfully")
        print(f"✓ Created {len(sources)} default sources")


if __name__ == '__main__':
    init_database()
