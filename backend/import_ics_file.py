#!/usr/bin/env python3
"""
Import events from an exported .ics calendar file.
"""
import sys
from app import create_app
from models import db, Source, Event
from ingestion.ics_parser import parse_ics_from_file
from utils.deduplication import normalize_event_data

if len(sys.argv) < 2:
    print("Usage: python import_ics_file.py <path_to_ics_file>")
    print("\nExport your calendar from Google Calendar:")
    print("Settings → Import & Export → Export")
    print("Then run: python import_ics_file.py ~/Downloads/calendar.ics")
    sys.exit(1)

ics_file_path = sys.argv[1]

app = create_app()
with app.app_context():
    # Create a source for this file
    source = Source.query.filter_by(name='Imported Calendar').first()
    if not source:
        source = Source(
            name='Imported Calendar',
            type='ics',
            url=f'file://{ics_file_path}',
            active=True
        )
        db.session.add(source)
        db.session.commit()
    
    print(f'Reading events from: {ics_file_path}')
    
    # Parse the ICS file
    try:
        events = parse_ics_from_file(ics_file_path)
        print(f'Found {len(events)} events in file')
        
        # Store events
        ingested = 0
        duplicates = 0
        
        for event_data in events:
            try:
                normalized = normalize_event_data(event_data)
                normalized['source_id'] = source.id
                
                # Check for duplicate
                if normalized.get('fingerprint'):
                    existing = Event.query.filter_by(
                        fingerprint=normalized['fingerprint']
                    ).first()
                    
                    if existing:
                        duplicates += 1
                        continue
                
                # Create new event
                event = Event(**normalized)
                db.session.add(event)
                db.session.commit()
                ingested += 1
                
            except Exception as e:
                print(f"  Error storing event: {e}")
                db.session.rollback()
                continue
        
        print(f'\n✓ Imported: {ingested} events')
        print(f'  Duplicates skipped: {duplicates}')
        print('\n✓ Done! Check your frontend to see events.')
        
    except Exception as e:
        print(f'✗ Error reading file: {e}')
        sys.exit(1)
