# backend/start.sh
#!/bin/bash
set -e

# Install dependencies
pip install -r requirements.txt

# Run database migrations
alembic upgrade head

# Start the application
uvicorn app.main:app --host 0.0.0.0 --port $PORT
