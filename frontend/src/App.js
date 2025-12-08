import React, { useState, useEffect } from 'react';
import { eventService } from './services/api';
import EventCard from './components/EventCard';
import FilterBar from './components/FilterBar';
import './App.css';

function App() {
  const [events, setEvents] = useState([]);
  const [filteredEvents, setFilteredEvents] = useState([]);
  const [selectedTags, setSelectedTags] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [timeFilter, setTimeFilter] = useState('upcoming'); // upcoming, today, week

  useEffect(() => {
    fetchEvents();
  }, [timeFilter]);

  useEffect(() => {
    applyFilters();
  }, [events, selectedTags]);

  const fetchEvents = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const params = {};
      if (timeFilter === 'today') {
        params.days = 1;
      } else if (timeFilter === 'week') {
        params.days = 7;
      }
      
      const data = await eventService.getEvents(params);
      setEvents(data.events || []);
    } catch (err) {
      setError('Failed to load events. Please try again later.');
      console.error('Error fetching events:', err);
    } finally {
      setLoading(false);
    }
  };

  const applyFilters = () => {
    if (selectedTags.length === 0) {
      setFilteredEvents(events);
    } else {
      setFilteredEvents(
        events.filter((event) => selectedTags.includes(event.tag))
      );
    }
  };

  const handleTagToggle = (tag) => {
    setSelectedTags((prev) =>
      prev.includes(tag)
        ? prev.filter((t) => t !== tag)
        : [...prev, tag]
    );
  };

  const handleClearFilters = () => {
    setSelectedTags([]);
  };

  return (
    <div className="app">
      <header className="app-header">
        <div className="header-content">
          <h1>Concierge</h1>
          <p className="tagline">Your event hub</p>
        </div>
      </header>

      <main className="app-main">
        <div className="container">
          <div className="time-filter">
            <button
              className={timeFilter === 'today' ? 'active' : ''}
              onClick={() => setTimeFilter('today')}
            >
              Today
            </button>
            <button
              className={timeFilter === 'week' ? 'active' : ''}
              onClick={() => setTimeFilter('week')}
            >
              This Week
            </button>
            <button
              className={timeFilter === 'upcoming' ? 'active' : ''}
              onClick={() => setTimeFilter('upcoming')}
            >
              All Upcoming
            </button>
          </div>

          <FilterBar
            selectedTags={selectedTags}
            onTagToggle={handleTagToggle}
            onClearFilters={handleClearFilters}
          />

          {loading && (
            <div className="loading">
              <div className="spinner"></div>
              <p>Loading events...</p>
            </div>
          )}

          {error && (
            <div className="error">
              <p>{error}</p>
              <button onClick={fetchEvents}>Retry</button>
            </div>
          )}

          {!loading && !error && filteredEvents.length === 0 && (
            <div className="empty-state">
              <h3>No events found</h3>
              <p>
                {selectedTags.length > 0
                  ? 'Try adjusting your filters'
                  : 'No upcoming events at this time'}
              </p>
            </div>
          )}

          {!loading && !error && filteredEvents.length > 0 && (
            <div className="events-list">
              <div className="events-count">
                {filteredEvents.length} event{filteredEvents.length !== 1 ? 's' : ''}
              </div>
              {filteredEvents.map((event) => (
                <EventCard key={event.id} event={event} />
              ))}
            </div>
          )}
        </div>
      </main>

      <footer className="app-footer">
        <p>
          For this version (V1.0.0), events are sourced from Calendar, Email, and Telegram general chat. Patience is advised.
        </p>
      </footer>
    </div>
  );
}

export default App;
