#!/bin/bash
# Production run script for Flask application

echo "Starting Flask application in production mode..."
echo "- Debug mode: OFF"
echo "- Host: 0.0.0.0"
echo "- Port: 5000"
echo ""

# Set environment variables for production
export FLASK_ENV=production
export FLASK_DEBUG=0

# Run the application
python -m app