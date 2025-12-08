"""
Scheduler for daily digests and event ingestion.

Runs:
- Event ingestion every 6 hours
- 08:00 digest daily
- 15:00 same-day reminder daily
"""
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime, timedelta
import pytz
import os
from dotenv import load_dotenv

from app import create_app
from models import db, User, Event, DigestLog
from ingestion.ingest import ingest_all_sources
from utils.digest import send_digest_to_user

# Load environment
load_dotenv()

# Timezone
TZ = pytz.timezone(os.getenv('TIMEZONE', 'America/Los_Angeles'))


def job_ingest_events():
    """Job: Ingest events from all sources"""
    print(f"\n[{datetime.now()}] Running event ingestion...")
    try:
        ingest_all_sources()
        print("✓ Event ingestion completed")
    except Exception as e:
        print(f"✗ Event ingestion failed: {e}")


def job_send_morning_digest():
    """Job: Send 08:00 morning digest to all users"""
    print(f"\n[{datetime.now()}] Sending 08:00 morning digest...")
    app = create_app()
    
    with app.app_context():
        users = User.query.filter_by(digest_08_enabled=True).all()
        
        for user in users:
            try:
                # Get events for the next 24 hours
                events = get_user_events(user, hours=24)
                
                success = send_digest_to_user(
                    user,
                    events,
                    digest_type='08:00'
                )
                
                # Log the digest
                log = DigestLog(
                    digest_type='08:00',
                    user_id=user.id,
                    event_count=len(events),
                    success=success
                )
                db.session.add(log)
                db.session.commit()
                
                if success:
                    print(f"  ✓ Sent to {user.email} ({len(events)} events)")
                else:
                    print(f"  ✗ Failed to send to {user.email}")
                    
            except Exception as e:
                print(f"  ✗ Error for {user.email}: {e}")
                continue


def job_send_afternoon_reminder():
    """Job: Send 15:00 same-day reminder"""
    print(f"\n[{datetime.now()}] Sending 15:00 same-day reminder...")
    app = create_app()
    
    with app.app_context():
        users = User.query.filter_by(digest_15_enabled=True).all()
        
        for user in users:
            try:
                # Get events for the rest of today only
                events = get_user_events(user, hours=9)  # ~9 hours left
                
                # Only send if there are upcoming events
                if not events:
                    continue
                
                success = send_digest_to_user(
                    user,
                    events,
                    digest_type='15:00'
                )
                
                # Log the digest
                log = DigestLog(
                    digest_type='15:00',
                    user_id=user.id,
                    event_count=len(events),
                    success=success
                )
                db.session.add(log)
                db.session.commit()
                
                if success:
                    print(f"  ✓ Sent to {user.email} ({len(events)} events)")
                    
            except Exception as e:
                print(f"  ✗ Error for {user.email}: {e}")
                continue


def get_user_events(user: User, hours: int = 24):
    """
    Get upcoming events for a user based on subscriptions.
    
    Args:
        user: User object
        hours: How many hours ahead to look
        
    Returns:
        List of Event objects
    """
    now = datetime.utcnow()
    end_time = now + timedelta(hours=hours)
    
    # Get user's subscribed tags
    subscribed_tags = [sub.tag for sub in user.subscriptions]
    
    # If no subscriptions, get all events
    if not subscribed_tags:
        events = Event.query.filter(
            Event.start_time >= now,
            Event.start_time <= end_time
        ).order_by(Event.start_time.asc()).all()
    else:
        events = Event.query.filter(
            Event.start_time >= now,
            Event.start_time <= end_time,
            Event.tag.in_(subscribed_tags)
        ).order_by(Event.start_time.asc()).all()
    
    return events


def main():
    """Start the scheduler"""
    scheduler = BlockingScheduler(timezone=TZ)
    
    # Event ingestion every 6 hours
    scheduler.add_job(
        job_ingest_events,
        CronTrigger(hour='*/6'),
        id='ingest_events',
        name='Ingest events from all sources'
    )
    
    # Morning digest at 08:00
    scheduler.add_job(
        job_send_morning_digest,
        CronTrigger(hour=8, minute=0),
        id='morning_digest',
        name='Send 08:00 morning digest'
    )
    
    # Afternoon reminder at 15:00
    scheduler.add_job(
        job_send_afternoon_reminder,
        CronTrigger(hour=15, minute=0),
        id='afternoon_reminder',
        name='Send 15:00 same-day reminder'
    )
    
    print(f"{'='*60}")
    print("Concierge Scheduler Started")
    print(f"Timezone: {TZ}")
    print(f"{'='*60}")
    print("\nScheduled jobs:")
    print("  - Event ingestion: Every 6 hours")
    print("  - Morning digest: Daily at 08:00")
    print("  - Afternoon reminder: Daily at 15:00")
    print(f"\n{'='*60}\n")
    
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        print("\nShutting down scheduler...")
        scheduler.shutdown()


if __name__ == '__main__':
    main()
