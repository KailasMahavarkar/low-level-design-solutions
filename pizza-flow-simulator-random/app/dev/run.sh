#!/bin/sh

# Execute the migrations
alembic upgrade head

# Run the application
fastapi dev --port 8080 --host 0.0.0.0 main.py