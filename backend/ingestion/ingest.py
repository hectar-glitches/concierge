"""
Ingest events from all active sources and store in database.
"""
import os
from datetime import datetime
from app import create_app
from models import db, Source, Event
from ingestion.ics_parser import parse_ics_url
from ingestion.telegram_ingest import ingest_telegram_events
from utils.deduplication import normalize_event_data


def ingest_all_sources():
    """
    Fetch events from all active sources and store in database.
    """
    app = create_app()
    
    with app.app_context():
        sources = Source.query.filter_by(active=True).all()
        
        total_ingested = 0
        total_duplicates = 0
        
        for source in sources:
            print(f"\nIngesting from: {source.name} ({source.type})")
            
            try:
                events = fetch_events_from_source(source)
                ingested, duplicates = store_events(events, source.id)
                
                total_ingested += ingested
                total_duplicates += duplicates
                
                # Update last fetched time
                source.last_fetched = datetime.utcnow()
                db.session.commit()
                
                print(f"  ✓ Ingested: {ingested}, Duplicates: {duplicates}")
                
            except Exception as e:
                print(f"  ✗ Error: {e}")
                continue
        
        print(f"\n{'='*50}")
        print(f"Total ingested: {total_ingested}")
        print(f"Total duplicates skipped: {total_duplicates}")
        print(f"{'='*50}\n")


def fetch_events_from_source(source: Source) -> list:
    """
    Fetch events from a source based on its type.
    """
    if source.type == 'ics':
        return parse_ics_url(source.url)
    elif source.type == 'slack':
        # TODO: Implement Slack integration
        return []
    elif source.type == 'telegram':
        # Use the chat_id from source metadata
        chat_ids = [source.url] if source.url else []
        return ingest_telegram_events(chat_ids)
    elif source.type == 'forum':
        # TODO: Implement Forum scraping
        return []
    else:
        return []


def store_events(events: list, source_id: int) -> tuple:
    """
    Store events in database, skipping duplicates.
    
    Returns:
        Tuple of (ingested_count, duplicate_count)
    """
    ingested = 0
    duplicates = 0
    
    for event_data in events:
        try:
            # Normalize the event data
            normalized = normalize_event_data(event_data)
            normalized['source_id'] = source_id
            
            # Check for duplicate by fingerprint
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
    
    return ingested, duplicates


if __name__ == '__main__':
    ingest_all_sources()
