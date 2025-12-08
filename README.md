# Concierge - Event Aggregation System

A single, dependable event hub that consolidates campus events and delivers them at predictable times.

## Problem

Course touchpoints, advising, capstone meetings, community events, and activities are scattered across email, Forum posts, myMinerva, Slack, Telegram, and calendar invites. This leads to missed mandatory sessions, lost opportunities, and weaker community ties.

## Solution

A trustworthy event aggregation system that provides:
- **Completeness**: All relevant events from tracked sources
- **Structural Assurance**: Predictable delivery times (08:00 digest + optional 15:00 reminder)
- **Source Transparency**: Every event shows its source
- **Personalization**: Filter by tags (Required/Career/Capstone/Social/Deadline)

## Architecture

```
Backend (Flask + SQLite)
├── Event ingestion (ICS, Slack, Telegram, Forum)
├── Normalization & deduplication
├── REST API
└── Scheduled digest delivery

Frontend (React)
├── Event feed with filters
├── Tag-based subscriptions
└── Export to ICS
```

## Quick Start

### Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python init_db.py
python app.py
```

### Frontend Setup
```bash
cd frontend
npm install
npm start
```

### Run Scheduler
```bash
cd backend
source venv/bin/activate
python scheduler.py
```

## Project Structure

```
concierge/
├── backend/
│   ├── app.py              # Flask application
│   ├── models.py           # Database models
│   ├── ingestion/          # Event source connectors
│   ├── scheduler.py        # Daily digest scheduler
│   └── utils/              # Helpers (dedup, normalization)
├── frontend/
│   ├── src/
│   │   ├── components/     # React components
│   │   ├── services/       # API client
│   │   └── App.js
│   └── public/
└── database/
    └── schema.sql          # Database schema
```

## Core Features (MVP)

- [x] ICS calendar ingestion
- [x] Event normalization schema
- [x] Web feed with source labels
- [x] Tag-based filtering
- [x] Daily 08:00 digest
- [x] Optional 15:00 same-day reminder
- [x] SQLite database
- [x] REST API

## Stretch Goals

- [ ] Event submission form
- [ ] Per-tag email subscriptions
- [ ] Slack/Telegram bot integration
- [ ] Analytics dashboard
- [ ] Mobile app

## Tech Stack

- **Backend**: Python 3.11+, Flask, SQLAlchemy, APScheduler
- **Database**: SQLite (production can use PostgreSQL)
- **Frontend**: React, Axios
- **Deployment**: Docker, Gunicorn

## License

MIT
