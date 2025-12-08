# Concierge Frontend

React-based frontend for the Concierge event aggregation system.

## Setup

```bash
npm install
npm start
```

The app will open at `http://localhost:3000` and proxy API requests to `http://localhost:5000`.

## Features

- Event feed with real-time updates
- Filter by tags (Required, Career, Capstone, Social, Deadline)
- Time-based filtering (Today, This Week, All Upcoming)
- Responsive design
- Source attribution for each event

## Environment Variables

Create a `.env` file:
```
REACT_APP_API_URL=http://localhost:5000/api
```

## Build for Production

```bash
npm run build
```

This creates an optimized production build in the `build/` directory.
