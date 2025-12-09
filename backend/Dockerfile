FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt gunicorn

# Copy application
COPY . .

# Ensure instance directory exists with database
RUN mkdir -p instance

# Expose port
EXPOSE 5000

# Run application with Railway's PORT variable
CMD gunicorn -w 4 -b 0.0.0.0:${PORT:-5000} --timeout 120 app:app
