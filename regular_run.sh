#!/bin/bash

# regular_run.sh - Regular startup script for CCGenTool2
# This script starts the existing services without rebuilding or cleaning

set -e  # Exit on any error

echo "🚀 Starting CCGenTool2 services..."
echo "=================================="

# Step 1: Start backend services (database + API)
echo "📦 Starting backend services..."
docker compose up -d

# Step 2: Wait for services to be ready
echo "⏳ Waiting for services to be ready..."
echo "   Checking database health..."
timeout=30
counter=0
while ! docker compose exec -T db pg_isready -U postgres -d appdb >/dev/null 2>&1; do
    if [ $counter -eq $timeout ]; then
        echo "❌ Database failed to start within $timeout seconds"
        echo "💡 Try running fresh_run.sh instead"
        exit 1
    fi
    echo "   Database not ready yet... waiting ($counter/$timeout)"
    sleep 1
    ((counter++))
done

echo "   Checking API health..."
counter=0
while ! curl -s http://localhost:8000/health >/dev/null 2>&1; do
    if [ $counter -eq $timeout ]; then
        echo "❌ API failed to start within $timeout seconds"
        echo "💡 Try running fresh_run.sh instead"
        exit 1
    fi
    echo "   API not ready yet... waiting ($counter/$timeout)"
    sleep 1
    ((counter++))
done

# Step 3: Setup frontend if needed
echo "🎨 Setting up frontend..."
cd web

# Copy environment file if it doesn't exist
if [ ! -f .env ]; then
    cp .env.example .env
    echo "   Created .env file from example"
fi

# Install dependencies if node_modules doesn't exist
if [ ! -d node_modules ]; then
    echo "   Installing frontend dependencies..."
    npm install
else
    echo "   Frontend dependencies already installed"
fi

# Start frontend development server
echo "🚀 Starting frontend development server..."
npm run dev &
FRONTEND_PID=$!

# Wait a moment for frontend to start
sleep 3

echo ""
echo "✅ All services started successfully!"
echo "=================================="
echo "🌐 Services running:"
echo "   Database:  http://localhost:5432"
echo "   API:       http://localhost:8000"
echo "   Frontend:  http://localhost:5173"
echo ""
echo "📋 Quick start:"
echo "   1. Open your browser to http://localhost:5173"
echo "   2. Use the sidebar to navigate between features"
echo "   3. Database status is shown in the top-right corner"
echo ""
echo "🛑 To stop all services:"
echo "   Press Ctrl+C to stop the frontend"
echo "   Run: docker compose down"
echo ""
echo "Frontend PID: $FRONTEND_PID"

# Keep the script running to show frontend output
wait $FRONTEND_PID