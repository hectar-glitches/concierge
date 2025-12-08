#!/usr/bin/env python3
"""
Add a Google Calendar ICS feed as a source and fetch events.
"""
import sys
from app import create_app
from models import db, Source
from ingestion.ingest import ingest_all_sources

if len(sys.argv) < 2:
    print("Usage: python add_calendar.py <ICS_URL>")
    print("\nGet your ICS URL from:")
    print("Google Calendar → Settings → Your Calendar → Integrate calendar")
    print("Copy the 'Secret address in iCal format' URL")
    sys.exit(1)

ics_url = sys.argv[1]

app = create_app()
with app.app_context():
    # Check if source already exists
    source = Source.query.filter_by(name='Google Calendar').first()
    
    if source:
        print(f'Calendar source already exists (ID: {source.id})')
        print(f'Updating URL to: {ics_url}')
        source.url = ics_url
        source.active = True
        db.session.commit()
    else:
        # Add source
        source = Source(
            name='Google Calendar',
            type='ics',
            url=ics_url,
            active=True
        )
        db.session.add(source)
        db.session.commit()
        print(f'✓ Calendar source added (ID: {source.id})')
    
    # Fetch events
    print('\nFetching events from calendar...')
    ingest_all_sources()
    print('\n✓ Done! Check your frontend to see events.')
