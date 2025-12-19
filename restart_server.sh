#!/bin/bash

echo "🔄 Restarting server with fixes..."

# Stop existing server
echo "Stopping existing server..."
pkill -f "uvicorn main:app" || echo "No server running"

# Wait a moment
sleep 2

# Start fresh server
echo "Starting server..."
bash deploy.sh

echo "✅ Server restarted!"
echo ""
echo "Test with:"
echo "  curl http://localhost:8080/health"
echo "  curl -X POST http://localhost:8080/query -H 'Content-Type: application/json' -d '{\"propertyId\":\"516812130\",\"query\":\"How many users last 7 days?\"}'"
