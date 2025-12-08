#!/usr/bin/env python3
"""
Manually add events from Telegram messages.
Paste event text when prompted.
"""
from app import create_app
from models import db, Event, Source
from ingestion.telegram_ingest import TelegramIngester
from utils.deduplication import normalize_event_data
from datetime import datetime

app = create_app()

with app.app_context():
    # Get or create a manual Telegram source
    source = Source.query.filter_by(name='Manual Telegram Import').first()
    if not source:
        source = Source(
            name='Manual Telegram Import',
            type='telegram',
            url='manual',
            active=True
        )
        db.session.add(source)
        db.session.commit()
    
    print("=" * 60)
    print("MANUAL TELEGRAM EVENT IMPORT")
    print("=" * 60)
    print("\nPaste Telegram event message (press Ctrl+D when done):")
    print("-" * 60)
    
    # Read multiline input
    lines = []
    try:
        while True:
            line = input()
            lines.append(line)
    except EOFError:
        pass
    
    text = '\n'.join(lines)
    
    if not text.strip():
        print("No text provided. Exiting.")
        exit(1)
    
    # Parse the message
    ingester = TelegramIngester('dummy_token')  # Token not needed for parsing
    message = {'text': text, 'message_id': 0}
    event_data = ingester.parse_event_from_message(message)
    
    if not event_data:
        print("\n✗ Could not parse event from message.")
        print("Make sure the message contains:")
        print("  - Event title (first line)")
        print("  - Date and time (e.g., 'Dec 15, 2025 at 2:00 PM')")
        exit(1)
    
    # Normalize and store
    normalized = normalize_event_data(event_data)
    normalized['source_id'] = source.id
    
    event = Event(**normalized)
    db.session.add(event)
    db.session.commit()
    
    print("\n" + "=" * 60)
    print("✓ EVENT ADDED SUCCESSFULLY!")
    print("=" * 60)
    print(f"Title: {event.title}")
    print(f"Date: {event.start_time}")
    print(f"Location: {event.location or 'N/A'}")
    print(f"Tag: {event.tag or 'None'}")
    print(f"URL: {event.virtual_url or 'N/A'}")
    print("=" * 60)
