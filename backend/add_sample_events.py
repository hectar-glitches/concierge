#!/usr/bin/env python3
"""
Add sample events to the Concierge database for testing
"""
from datetime import datetime, timedelta
from app import create_app
from models import db, Event, Source

def add_sample_events():
    """Add sample events to the database"""
    app = create_app()
    
    with app.app_context():
        # Get existing sources
        forum_source = Source.query.filter_by(name='Forum').first()
        calendar_source = Source.query.filter_by(name='Campus Calendar').first()
        slack_source = Source.query.filter_by(name='Slack').first()
        
        # Clear existing events (optional - comment out if you want to keep old events)
        Event.query.delete()
        
        # Sample events
        now = datetime.utcnow()
        
        events = [
            Event(
                title='CS110 Office Hours',
                description='Weekly office hours for CS110 students. Come with questions!',
                start_time=now + timedelta(hours=2),
                end_time=now + timedelta(hours=3),
                location='Room 305',
                location_type='physical',
                tag='Required',
                source_id=calendar_source.id if calendar_source else 1,
                rsvp_url='https://example.com/rsvp/cs110'
            ),
            Event(
                title='Career Fair - Tech Companies',
                description='Meet recruiters from top tech companies. Bring your resume!',
                start_time=now + timedelta(days=2, hours=10),
                end_time=now + timedelta(days=2, hours=16),
                location='Main Hall',
                location_type='physical',
                tag='Career',
                source_id=forum_source.id if forum_source else 1,
                rsvp_url='https://example.com/career-fair'
            ),
            Event(
                title='Capstone Project Presentation',
                description='Final presentations for all capstone projects. Attendance mandatory.',
                start_time=now + timedelta(days=5, hours=14),
                end_time=now + timedelta(days=5, hours=17),
                location='Auditorium',
                location_type='physical',
                tag='Capstone',
                source_id=calendar_source.id if calendar_source else 1,
                rsvp_url=None
            ),
            Event(
                title='Study Group - Algorithms',
                description='Collaborative study session for algorithms. All levels welcome!',
                start_time=now + timedelta(days=1, hours=18),
                end_time=now + timedelta(days=1, hours=20),
                location='Library Study Room 3',
                location_type='physical',
                tag='Social',
                source_id=slack_source.id if slack_source else 1,
                rsvp_url='https://example.com/study-group'
            ),
            Event(
                title='Assignment 3 Deadline',
                description='Final submission deadline for Assignment 3. No late submissions accepted.',
                start_time=now + timedelta(days=3, hours=23, minutes=59),
                end_time=None,
                location=None,
                location_type='virtual',
                tag='Deadline',
                source_id=forum_source.id if forum_source else 1,
                virtual_url='https://example.com/submit',
                rsvp_url=None
            ),
            Event(
                title='Guest Lecture: AI Ethics',
                description='Distinguished speaker series on AI Ethics and Responsibility.',
                start_time=now + timedelta(days=7, hours=15),
                end_time=now + timedelta(days=7, hours=16, minutes=30),
                location='Zoom',
                location_type='virtual',
                tag='Career',
                source_id=calendar_source.id if calendar_source else 1,
                virtual_url='https://zoom.us/j/example',
                rsvp_url='https://example.com/guest-lecture'
            ),
            Event(
                title='Coffee Chat with Dean',
                description='Informal coffee chat with the Dean. Come discuss anything!',
                start_time=now + timedelta(days=4, hours=10),
                end_time=now + timedelta(days=4, hours=11),
                location='Campus Café',
                location_type='physical',
                tag='Social',
                source_id=forum_source.id if forum_source else 1,
                rsvp_url='https://example.com/coffee-chat'
            ),
            Event(
                title='Capstone Advisor Meeting',
                description='Required meeting with your capstone advisor to discuss progress.',
                start_time=now + timedelta(days=6, hours=9),
                end_time=now + timedelta(days=6, hours=10),
                location='Advisor Office',
                location_type='physical',
                tag='Capstone',
                source_id=calendar_source.id if calendar_source else 1,
                rsvp_url=None
            ),
            Event(
                title='Midterm Exam - Database Systems',
                description='Midterm examination for Database Systems course. Arrive 10 mins early.',
                start_time=now + timedelta(days=8, hours=13),
                end_time=now + timedelta(days=8, hours=15),
                location='Exam Hall B',
                location_type='physical',
                tag='Required',
                source_id=calendar_source.id if calendar_source else 1,
                rsvp_url=None
            ),
            Event(
                title='Hackathon Kickoff',
                description='24-hour hackathon starts now! Build something amazing.',
                start_time=now + timedelta(days=10, hours=18),
                end_time=now + timedelta(days=11, hours=18),
                location='Tech Lab',
                location_type='physical',
                tag='Social',
                source_id=slack_source.id if slack_source else 1,
                rsvp_url='https://example.com/hackathon'
            ),
        ]
        
        # Add all events
        for event in events:
            db.session.add(event)
        
        db.session.commit()
        
        print(f"✓ Successfully added {len(events)} sample events to the database")
        print("\nSample events:")
        for event in events:
            print(f"  - {event.title} ({event.tag}) - {event.start_time.strftime('%b %d, %Y at %H:%M')}")


if __name__ == '__main__':
    add_sample_events()
