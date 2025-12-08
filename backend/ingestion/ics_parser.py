"""
ICS (iCalendar) feed ingestion.
"""
from icalendar import Calendar
from datetime import datetime
import requests
import pytz
from typing import List, Dict


def parse_ics_url(url: str) -> List[Dict]:
    """
    Fetch and parse an ICS calendar feed.
    
    Args:
        url: URL to the ICS file
        
    Returns:
        List of event dictionaries
    """
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        return parse_ics_content(response.content)
    except Exception as e:
        print(f"Error fetching ICS from {url}: {e}")
        return []


def parse_ics_from_file(file_path: str) -> List[Dict]:
    """
    Parse an ICS calendar file from disk.
    
    Args:
        file_path: Path to the ICS file
        
    Returns:
        List of event dictionaries
    """
    try:
        with open(file_path, 'rb') as f:
            content = f.read()
        return parse_ics_content(content)
    except Exception as e:
        print(f"Error reading ICS file {file_path}: {e}")
        return []


def parse_ics_content(content: bytes) -> List[Dict]:
    """
    Parse ICS calendar content.
    
    Args:
        content: Raw ICS file content
        
    Returns:
        List of event dictionaries
    """
    events = []
    
    try:
        calendar = Calendar.from_ical(content)
        
        for component in calendar.walk():
            if component.name == "VEVENT":
                event = parse_vevent(component)
                if event:
                    events.append(event)
                    
    except Exception as e:
        print(f"Error parsing ICS content: {e}")
    
    return events


def parse_vevent(vevent) -> Dict:
    """
    Parse a VEVENT component into event dictionary.
    
    Args:
        vevent: iCalendar VEVENT component
        
    Returns:
        Event dictionary or None if event should be skipped
    """
    try:
        # Extract basic fields
        title = str(vevent.get('SUMMARY', ''))
        description = str(vevent.get('DESCRIPTION', ''))
        location = str(vevent.get('LOCATION', ''))
        
        # Skip class events (CS###, NS###, SS###, AH###, HC###, etc.)
        import re
        if re.match(r'^[A-Z]{2}\d{3}\s', title):
            return None
        
        # Parse start and end times
        dtstart = vevent.get('DTSTART')
        dtend = vevent.get('DTEND')
        
        if not dtstart:
            return None
        
        start_time = ensure_datetime(dtstart.dt)
        end_time = ensure_datetime(dtend.dt) if dtend else None
        
        # Extract timezone
        tz = 'UTC'
        if hasattr(dtstart.dt, 'tzinfo') and dtstart.dt.tzinfo:
            tz = str(dtstart.dt.tzinfo)
        
        # Check if virtual (look for Zoom, Meet, Teams links)
        is_virtual = False
        meeting_link = None
        
        if description:
            for keyword in ['zoom.us', 'meet.google.com', 'teams.microsoft']:
                if keyword in description.lower():
                    is_virtual = True
                    # Try to extract link (simple regex)
                    import re
                    match = re.search(r'https?://[^\s]+', description)
                    if match:
                        meeting_link = match.group()
                    break
        
        # Get UID for deduplication
        uid = str(vevent.get('UID', ''))
        
        return {
            'title': title,
            'description': description,
            'start_time': start_time,
            'end_time': end_time,
            'timezone': tz,
            'location': location if location else None,
            'is_virtual': is_virtual,
            'meeting_link': meeting_link,
            'source_event_id': uid,
            'tag': infer_tag_from_event(title, description),
        }
        
    except Exception as e:
        print(f"Error parsing VEVENT: {e}")
        return None


def ensure_datetime(dt) -> datetime:
    """Convert date or datetime to datetime object"""
    if isinstance(dt, datetime):
        return dt
    else:
        # It's a date, convert to datetime at midnight
        return datetime.combine(dt, datetime.min.time())


def infer_tag_from_event(title: str, description: str) -> str:
    """
    Infer event tag from title and description.
    
    Uses keyword matching to guess the appropriate tag.
    """
    text = (title + ' ' + description).lower()
    
    # Required/Mandatory
    if any(word in text for word in [
        'required', 'mandatory', 'attendance',
        'must attend', 'compulsory'
    ]):
        return 'Required'
    
    # Career
    if any(word in text for word in [
        'career', 'job', 'recruiting', 'interview',
        'resume', 'networking', 'employer'
    ]):
        return 'Career'
    
    # Capstone
    if any(word in text for word in [
        'capstone', 'thesis', 'research', 'advisor',
        'committee', 'defense'
    ]):
        return 'Capstone'
    
    # Deadline
    if any(word in text for word in [
        'deadline', 'due', 'submission', 'final date'
    ]):
        return 'Deadline'
    
    # Social (parties, gatherings, etc.)
    if any(word in text for word in [
        'social', 'party', 'gathering', 'hangout',
        'celebration', 'mixer'
    ]):
        return 'Social'
    
    # General (default for classes and other events)
    return 'General'
