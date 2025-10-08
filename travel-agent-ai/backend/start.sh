#!/bin/bash
set -e

# Install dependencies
echo "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Set environment variables
export PYTHONPATH=/app

# Run database migrations
echo "Running database migrations..."
alembic upgrade head

# Start the application
echo "Starting application..."
if [ "$RAILWAY_ENVIRONMENT" = "production" ]; then
    echo "Running in production mode with Gunicorn..."
    gunicorn -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:$PORT app.main:app
else
    echo "Running in development mode with Uvicorn..."
    uvicorn app.main:app --host 0.0.0.0 --port $PORT --reload
fi
