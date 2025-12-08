"""
Utility functions for event deduplication and normalization.
"""
import hashlib
from datetime import datetime
from typing import Dict, Optional


def generate_fingerprint(
    title: str,
    start_time: datetime,
    location: Optional[str] = None
) -> str:
    """
    Generate a fingerprint for deduplication.
    
    Uses title + start_time + location to create a unique hash.
    This helps identify the same event from different sources.
    """
    components = [
        title.lower().strip(),
        start_time.isoformat(),
        (location or '').lower().strip()
    ]
    
    content = '|'.join(components)
    return hashlib.sha256(content.encode('utf-8')).hexdigest()


def normalize_event_data(raw_data: Dict) -> Dict:
    """
    Normalize event data from various sources into standard schema.
    
    Args:
        raw_data: Raw event data from any source
        
    Returns:
        Normalized event dictionary
    """
    normalized = {
        'title': (raw_data.get('title') or '').strip(),
        'description': (raw_data.get('description') or '').strip(),
        'start_time': raw_data.get('start_time'),
        'end_time': raw_data.get('end_time'),
        'timezone': raw_data.get('timezone', 'UTC'),
        'location': (raw_data.get('location') or '').strip() or None,
        'is_virtual': raw_data.get('is_virtual', False),
        'meeting_link': (raw_data.get('meeting_link') or '').strip() or None,
        'tag': normalize_tag(raw_data.get('tag')),
        'rsvp_link': (raw_data.get('rsvp_link') or '').strip() or None,
        'why_matters': (raw_data.get('why_matters') or '').strip() or None,
        'source_event_id': raw_data.get('source_event_id')
    }
    
    # Generate fingerprint
    if normalized['title'] and normalized['start_time']:
        normalized['fingerprint'] = generate_fingerprint(
            normalized['title'],
            normalized['start_time'],
            normalized['location']
        )
    
    return normalized


def normalize_tag(tag: Optional[str]) -> Optional[str]:
    """
    Normalize tag to one of the standard values.
    
    Standard tags: Required, Career, Capstone, Social, Deadline
    """
    if not tag:
        return None
    
    tag_lower = tag.lower().strip()
    
    tag_map = {
        'required': 'Required',
        'mandatory': 'Required',
        'career': 'Career',
        'jobs': 'Career',
        'recruiting': 'Career',
        'capstone': 'Capstone',
        'thesis': 'Capstone',
        'social': 'Social',
        'community': 'Social',
        'deadline': 'Deadline',
        'due': 'Deadline',
    }
    
    return tag_map.get(tag_lower, tag.title())


def is_duplicate(event1: Dict, event2: Dict) -> bool:
    """
    Check if two events are duplicates based on fingerprint or fields.
    """
    # Check fingerprint first
    if event1.get('fingerprint') and event2.get('fingerprint'):
        return event1['fingerprint'] == event2['fingerprint']
    
    # Fallback to field comparison
    same_title = event1.get('title', '').lower() == \
        event2.get('title', '').lower()
    same_time = event1.get('start_time') == event2.get('start_time')
    same_location = event1.get('location', '').lower() == \
        event2.get('location', '').lower()
    
    return same_title and same_time and same_location
