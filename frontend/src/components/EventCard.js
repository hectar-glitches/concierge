import React from 'react';
import { format, parseISO } from 'date-fns';
import './EventCard.css';

const TAG_COLORS = {
  Required: '#dc2626',
  Career: '#2563eb',
  Capstone: '#7c3aed',
  Social: '#059669',
  Deadline: '#ea580c',
};

const EventCard = ({ event }) => {
  const eventDate = parseISO(event.start_time);
  const endDate = event.end_time ? parseISO(event.end_time) : null;

  return (
    <div className="event-card">
      <div className="event-header">
        <div className="event-date-time">
          <div className="event-date">
            {format(eventDate, 'MMM d, yyyy')}
          </div>
          <div className="event-time">
            {format(eventDate, 'h:mm a')}
            {endDate && ` - ${format(endDate, 'h:mm a')}`}
          </div>
        </div>
        {event.tag && (
          <span
            className="event-tag"
            style={{ backgroundColor: TAG_COLORS[event.tag] || '#6b7280' }}
          >
            {event.tag}
          </span>
        )}
      </div>

      <h3 className="event-title">{event.title}</h3>

      {event.description && (
        <p className="event-description">{event.description}</p>
      )}

      <div className="event-footer">
        <div className="event-location">
          {event.location_type === 'virtual' && event.virtual_url ? (
            <a
              href={event.virtual_url}
              target="_blank"
              rel="noopener noreferrer"
              className="event-link"
            >
              📹 Join Online
            </a>
          ) : event.location ? (
            <span>📍 {event.location}</span>
          ) : null}
        </div>

        <div className="event-source">
          <span className="source-badge">
            {event.source_name || 'Unknown Source'}
          </span>
        </div>
      </div>

      {event.rsvp_url && (
        <div className="event-actions">
          <a
            href={event.rsvp_url}
            target="_blank"
            rel="noopener noreferrer"
            className="rsvp-button"
          >
            RSVP
          </a>
        </div>
      )}
    </div>
  );
};

export default EventCard;
