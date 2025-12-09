FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir flask flask-cors gunicorn

# Copy application
COPY app_simple.py ./app.py

# Expose port
EXPOSE 5000

# Run application
CMD gunicorn -w 2 -b 0.0.0.0:${PORT:-5000} app:app
