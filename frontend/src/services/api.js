import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const eventService = {
  // Get all events with optional filters
  getEvents: async (params = {}) => {
    const response = await api.get('/events', { params });
    return response.data;
  },

  // Get a single event by ID
  getEvent: async (eventId) => {
    const response = await api.get(`/events/${eventId}`);
    return response.data;
  },

  // Get all sources
  getSources: async () => {
    const response = await api.get('/sources');
    return response.data;
  },

  // Get user subscriptions
  getSubscriptions: async (userId) => {
    const response = await api.get(`/users/${userId}/subscriptions`);
    return response.data;
  },

  // Subscribe to a tag
  subscribe: async (userId, tag) => {
    const response = await api.post(`/users/${userId}/subscribe`, { tag });
    return response.data;
  },

  // Unsubscribe from a tag
  unsubscribe: async (userId, tag) => {
    const response = await api.post(`/users/${userId}/unsubscribe`, { tag });
    return response.data;
  },
};

export default api;
