"""
Minimal Flask application for Concierge - static events only.
"""
from flask import Flask, jsonify
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)

EVENTS = [
    {
        'id': 1, 'title': 'AI Night in Candlelight w/ Pizza & Grape Juice',
        'description': 'ASM + AIC event about AI at Minerva. Room 4105',
        'start_time': '2025-12-09T20:00:00', 'end_time': None,
        'location': 'Room 4105', 'tag': 'Social', 'is_virtual': False,
        'timezone': 'America/Argentina/Buenos_Aires',
        'source': {'id': 1, 'name': 'Telegram', 'type': 'telegram'}
    },
    {
        'id': 2, 'title': 'Tokyo Spring 2026 - Pre-Departure Orientation',
        'description': 'PDO for incoming Tokyo students via Zoom.',
        'start_time': '2025-12-08T21:00:00', 'end_time': None,
        'location': 'Zoom', 'tag': 'Required', 'is_virtual': True,
        'timezone': 'America/Argentina/Buenos_Aires',
        'source': {'id': 1, 'name': 'Email', 'type': 'email'}
    },
    {
        'id': 3, 'title': 'Neurodivergency Discussion & Awareness',
        'description': 'Discussion about neurodivergency. Quiet Room 708.',
        'start_time': '2025-12-11T20:00:00', 'end_time': None,
        'location': 'Quiet Room 708', 'tag': 'Social', 'is_virtual': False,
        'timezone': 'America/Argentina/Buenos_Aires',
        'source': {'id': 1, 'name': 'Telegram', 'type': 'telegram'}
    },
    {
        'id': 4, 'title': 'Unit Condition Report - Check Out',
        'description': 'SLT will send calendar invitations for check-out.',
        'start_time': '2025-12-11T12:00:00', 'end_time': None,
        'location': None, 'tag': 'Required', 'is_virtual': False,
        'timezone': 'America/Argentina/Buenos_Aires',
        'source': {'id': 1, 'name': 'Email', 'type': 'email'}
    },
    {
        'id': 5, 'title': 'Spring26 Room Assignments Info',
        'description': 'Info about room assignments and luggage storing.',
        'start_time': '2025-12-11T12:00:00', 'end_time': None,
        'location': None, 'tag': 'Required', 'is_virtual': False,
        'timezone': 'America/Argentina/Buenos_Aires',
        'source': {'id': 1, 'name': 'Email', 'type': 'email'}
    },
    {
        'id': 6, 'title': 'Making (Academic) Major Choices - Majors Fair',
        'description': 'Created by Professor Terrana.',
        'start_time': '2025-12-12T09:00:00', 'end_time': '2025-12-12T11:00:00',
        'location': None, 'tag': 'Career', 'is_virtual': False,
        'timezone': 'America/Argentina/Buenos_Aires',
        'source': {'id': 1, 'name': 'Community Portal', 'type': 'portal'}
    },
    {
        'id': 7, 'title': 'Indian Visa Pickup Deadline',
        'description': 'Last day to pick up Indian visa.',
        'start_time': '2025-12-13T17:00:00', 'end_time': None,
        'location': None, 'tag': 'Deadline', 'is_virtual': False,
        'timezone': 'America/Argentina/Buenos_Aires',
        'source': {'id': 1, 'name': 'Manual', 'type': 'manual'}
    },
    {
        'id': 8, 'title': 'Last Day of Fall Classes',
        'description': 'Final day of Fall 2025 semester classes.',
        'start_time': '2025-12-13T23:59:00', 'end_time': None,
        'location': None, 'tag': 'Required', 'is_virtual': False,
        'timezone': 'America/Argentina/Buenos_Aires',
        'source': {'id': 1, 'name': 'Academic Calendar', 'type': 'calendar'}
    },
    {
        'id': 9, 'title': 'CTD 10-Week Challenge - Weekly Deadline',
        'description': 'Complete the weekly task by Saturday 11:59 PM.',
        'start_time': '2025-12-13T23:59:00', 'end_time': None,
        'location': None, 'tag': 'Deadline', 'is_virtual': False,
        'meeting_link': 'https://minarashad.github.io/CTD-leaderboard/',
        'timezone': 'America/Argentina/Buenos_Aires',
        'source': {'id': 1, 'name': 'Telegram', 'type': 'telegram'}
    },
    {
        'id': 10, 'title': 'December Dash for B.R.E.A.K.',
        'description': 'Running/walking/biking event Dec 5-19.',
        'start_time': '2025-12-19T23:59:00', 'end_time': None,
        'location': None, 'tag': 'Social', 'is_virtual': False,
        'timezone': 'America/Argentina/Buenos_Aires',
        'source': {'id': 1, 'name': 'Community Portal', 'type': 'portal'}
    }
]


@app.route('/')
def index():
    return jsonify({
        'name': 'Concierge API',
        'version': '1.0.0',
        'status': 'running'
    })


@app.route('/api/health')
def health():
    return jsonify({'status': 'healthy'})


@app.route('/api/events')
def get_events():
    return jsonify({
        'events': EVENTS,
        'count': len(EVENTS)
    })


@app.route('/api/tags')
def get_tags():
    tags = list(set(e['tag'] for e in EVENTS))
    return jsonify({'tags': tags})


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
