#!/usr/bin/env python3
"""
Manually add events from Telegram Buenos Aires Fall 2025 group.
Run this script to add events discussed in the group chat.
"""
import sys
from datetime import datetime
from app import create_app
from models import db, Event, Source

# Buenos Aires timezone offset from UTC (ART is UTC-3)
BUENOS_AIRES_TZ = "America/Argentina/Buenos_Aires"

def add_telegram_events():
    app = create_app()
    
    with app.app_context():
        # Get or create Telegram source
        source = Source.query.filter_by(name='Telegram - Buenos Aires').first()
        if not source:
            source = Source(
                name='Telegram - Buenos Aires',
                type='telegram',
                url='Buenos Aires Fall 2025 group',
                active=True
            )
            db.session.add(source)
            db.session.commit()
        
        events_to_add = [
            {
                'title': 'AI Night in Candlelight w/ Pizza & Grape Juice',
                'description': 'ASM is collaborating with AIC to host a really special evening to learn about what the cohort thinks about AI, ways you use it in Minerva and our collective vision as a community. Room 4105',
                'start_time': datetime(2025, 12, 9, 20, 0),  # Dec 9, 8pm
                'location': 'Room 4105',
                'tag': 'Social',
                'timezone': BUENOS_AIRES_TZ,
                'source_id': source.id
            },
            {
                'title': 'Neurodivergency Discussion & Awareness',
                'description': 'Host: Yours truly. Quiet Room, 708. I will probably get food. Discussion about disability being socially constructed and the global neurodivergency movement.',
                'start_time': datetime(2025, 12, 11, 20, 0),  # Wednesday Dec 11, 8pm
                'location': 'Quiet Room 708',
                'tag': 'Social',
                'timezone': BUENOS_AIRES_TZ,
                'source_id': source.id
            },
            {
                'title': 'CTD 10-Week Challenge - Weekly Deadline',
                'description': 'Complete the weekly task by Saturday 11:59 PM. Each week releases new challenges. Win a mystery box filled with iconic souvenirs from your rotation city. https://minarashad.github.io/CTD-leaderboard/',
                'start_time': datetime(2025, 12, 13, 23, 59),  # Saturday Dec 13, 11:59 PM
                'meeting_link': 'https://minarashad.github.io/CTD-leaderboard/',
                'tag': 'Deadline',
                'timezone': BUENOS_AIRES_TZ,
                'source_id': source.id
            },
            {
                'title': 'December Dash for B.R.E.A.K.',
                'description': 'December 5K run for Boosting Resilience, Energy, Attitude, and Kindness. Running, walking, hiking, biking - anything that gets your heart rate up! Submit participation to Google Form.',
                'start_time': datetime(2025, 12, 19, 23, 59),  # Dec 19 end date
                'tag': 'Social',
                'timezone': BUENOS_AIRES_TZ,
                'source_id': source.id
            },
            {
                'title': 'Unit Condition Report - Check Out',
                'description': 'SLT will be sending calendar invitations to perform check-out Unit Condition Reports. Replace any missing or broken items with the exact same model.',
                'start_time': datetime(2025, 12, 11, 12, 0),  # Wednesday Dec 11
                'tag': 'Required',
                'timezone': BUENOS_AIRES_TZ,
                'source_id': source.id
            },
            {
                'title': 'Spring26 Room Assignments Info',
                'description': 'Information about Spring26 room assignments and further check-out indications, including luggage storing.',
                'start_time': datetime(2025, 12, 11, 12, 0),  # Wednesday Dec 11
                'tag': 'Required',
                'timezone': BUENOS_AIRES_TZ,
                'source_id': source.id
            },
            {
                'title': 'Making (Academic) Major Choices - Majors Fair',
                'description': 'Created by Professor Terrana. Academic advising event for major selection.',
                'start_time': datetime(2025, 12, 12, 9, 0),  # Dec 12, 9am
                'end_time': datetime(2025, 12, 12, 11, 0),  # Dec 12, 11am
                'tag': 'Career',
                'timezone': BUENOS_AIRES_TZ,
                'source_id': source.id
            },
            {
                'title': 'Tokyo Spring 2026 - Pre-Departure Orientation',
                'description': 'Pre-Departure Orientation for incoming Tokyo students. Buenos Aires time: Monday, December 8 at 9:00 PM. Join Zoom Meeting.',
                'start_time': datetime(2025, 12, 8, 21, 0),  # Dec 8, 9pm
                'meeting_link': 'https://minerva-edu.zoom.us/j/97421917685',
                'tag': 'Required',
                'timezone': BUENOS_AIRES_TZ,
                'source_id': source.id
            },
            {
                'title': 'Indian Visa Pickup Deadline',
                'description': 'Last day to pick up Indian visa documents.',
                'start_time': datetime(2025, 12, 13, 17, 0),  # Friday Dec 13, 5pm
                'tag': 'Deadline',
                'timezone': BUENOS_AIRES_TZ,
                'source_id': source.id
            },
            {
                'title': 'Last Day of Fall Classes',
                'description': 'Final day of Fall 2025 semester classes.',
                'start_time': datetime(2025, 12, 13, 23, 59),  # Friday Dec 13
                'tag': 'General',
                'timezone': BUENOS_AIRES_TZ,
                'source_id': source.id
            }
        ]
        
        added = 0
        skipped = 0
        
        for event_data in events_to_add:
            # Check if event already exists (by title and start time)
            existing = Event.query.filter_by(
                title=event_data['title'],
                start_time=event_data['start_time']
            ).first()
            
            if existing:
                print(f"  Skipped (already exists): {event_data['title']}")
                skipped += 1
                continue
            
            event = Event(**event_data)
            db.session.add(event)
            added += 1
            print(f"  Added: {event_data['title']} - {event_data['start_time']}")
        
        db.session.commit()
        
        print(f"\n✓ Added {added} new events")
        print(f"  Skipped {skipped} duplicates")
        
        # Show all upcoming events from this source
        print(f"\nAll upcoming Telegram events:")
        telegram_events = Event.query.filter(
            Event.source_id == source.id,
            Event.start_time >= datetime.now()
        ).order_by(Event.start_time).all()
        
        for e in telegram_events:
            print(f"  - {e.start_time.strftime('%b %d, %I:%M %p')} | {e.title}")

if __name__ == '__main__':
    add_telegram_events()
