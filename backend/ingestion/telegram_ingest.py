"""
Telegram message ingestion for events.
Monitors Telegram groups/channels for event announcements.
"""
import os
import re
from datetime import datetime, timedelta
from typing import List, Optional
import requests
from dateutil import parser as date_parser


class TelegramIngester:
    """Ingest events from Telegram messages"""
    
    def __init__(self, bot_token: str):
        self.bot_token = bot_token
        self.base_url = f"https://api.telegram.org/bot{bot_token}"
    
    def get_chat_messages(self, chat_id: str, limit: int = 100) -> List[dict]:
        """Get recent messages from a chat"""
        url = f"{self.base_url}/getUpdates"
        params = {"limit": limit}
        
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if not data.get('ok'):
                print(f"Telegram API error: {data.get('description')}")
                return []
            
            # Filter messages from specific chat
            messages = []
            for update in data.get('result', []):
                msg = update.get('message', {})
                if str(msg.get('chat', {}).get('id')) == str(chat_id):
                    messages.append(msg)
            
            return messages
        except Exception as e:
            print(f"Error fetching Telegram messages: {e}")
            return []
    
    def parse_event_from_message(self, message: dict) -> Optional[dict]:
        """
        Parse event details from a Telegram message.
        Looks for patterns like:
        - Date/time mentions
        - Event title (first line or bolded text)
        - Location (lines with 📍 or "Location:")
        - Links
        """
        text = message.get('text', '')
        if not text or len(text) < 10:
            return None
        
        lines = text.split('\n')
        
        # Try to extract event details
        event = {
            'title': None,
            'description': text,
            'start_time': None,
            'location': None,
            'virtual_url': None,
            'tag': None
        }
        
        # First non-empty line is usually the title
        for line in lines:
            if line.strip():
                event['title'] = line.strip()[:200]
                break
        
        # Look for date/time
        event['start_time'] = self._extract_datetime(text)
        
        # Look for location
        location_match = re.search(r'(?:📍|Location:|Venue:)\s*(.+)', text, re.IGNORECASE)
        if location_match:
            event['location'] = location_match.group(1).strip()[:200]
        
        # Look for URLs
        url_match = re.search(r'https?://[^\s]+', text)
        if url_match:
            event['virtual_url'] = url_match.group(0)
        
        # Determine tag based on keywords
        text_lower = text.lower()
        if any(word in text_lower for word in ['required', 'mandatory', 'attendance']):
            event['tag'] = 'Required'
        elif any(word in text_lower for word in ['career', 'job', 'internship', 'recruiting']):
            event['tag'] = 'Career'
        elif any(word in text_lower for word in ['capstone', 'thesis', 'project']):
            event['tag'] = 'Capstone'
        elif any(word in text_lower for word in ['social', 'party', 'gathering', 'meetup']):
            event['tag'] = 'Social'
        elif any(word in text_lower for word in ['deadline', 'due', 'submission']):
            event['tag'] = 'Deadline'
        
        # Only return if we have at least title and time
        if event['title'] and event['start_time']:
            return event
        
        return None
    
    def _extract_datetime(self, text: str) -> Optional[datetime]:
        """Extract datetime from text using various patterns"""
        
        # Common date patterns
        patterns = [
            r'(\d{1,2}/\d{1,2}/\d{2,4})\s+(?:at\s+)?(\d{1,2}:\d{2}\s*(?:AM|PM)?)',
            r'((?:Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)[,\s]+\w+\s+\d{1,2})\s+at\s+(\d{1,2}:\d{2}\s*(?:AM|PM)?)',
            r'(\w+\s+\d{1,2}(?:st|nd|rd|th)?[,\s]+\d{4})\s+at\s+(\d{1,2}:\d{2}\s*(?:AM|PM)?)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    date_str = f"{match.group(1)} {match.group(2)}"
                    return date_parser.parse(date_str, fuzzy=True)
                except:
                    continue
        
        # Try dateutil parser as fallback
        try:
            return date_parser.parse(text, fuzzy=True)
        except:
            return None
    
    def ingest_from_chat(self, chat_id: str) -> List[dict]:
        """Ingest events from a Telegram chat"""
        messages = self.get_chat_messages(chat_id)
        events = []
        
        for msg in messages:
            event = self.parse_event_from_message(msg)
            if event:
                # Add source metadata
                event['source_type'] = 'telegram'
                event['source_chat_id'] = chat_id
                event['message_id'] = msg.get('message_id')
                events.append(event)
        
        return events


def ingest_telegram_events(chat_ids: List[str]) -> List[dict]:
    """Main function to ingest events from Telegram"""
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    
    if not bot_token:
        print("TELEGRAM_BOT_TOKEN not set in environment")
        return []
    
    ingester = TelegramIngester(bot_token)
    all_events = []
    
    for chat_id in chat_ids:
        print(f"Ingesting from Telegram chat: {chat_id}")
        events = ingester.ingest_from_chat(chat_id)
        all_events.extend(events)
        print(f"  Found {len(events)} events")
    
    return all_events