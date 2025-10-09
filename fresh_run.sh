#!/bin/bash

# fresh_run.sh - Clean installation script for CCGenTool2
# This script performs a fresh installation by removing all existing data and rebuilding everything

set -e  # Exit on any error

echo "🧹 Starting fresh installation of CCGenTool2..."
echo "================================================"

# Step 1: Stop and remove all existing containers
echo "📦 Stopping and removing existing containers..."
docker compose down -v --remove-orphans || true

# Step 2: Remove all related images
echo "🗑️ Removing existing Docker images..."
docker images | grep ccgentool2 | awk '{print $3}' | xargs -r docker rmi -f || true
docker images | grep postgres | grep -E '(16-alpine|latest)' | awk '{print $3}' | xargs -r docker rmi -f || true

# Step 3: Clean up any dangling volumes and networks
echo "🧽 Cleaning up Docker volumes and networks..."
docker volume prune -f || true
docker network prune -f || true

# Step 4: Clean up frontend node_modules if they exist
echo "📁 Cleaning frontend dependencies..."
if [ -d "web/node_modules" ]; then
    rm -rf web/node_modules
    echo "   Removed existing node_modules"
fi

# Step 5: Rebuild and start the backend services (database + API)
echo "🔧 Building and starting backend services..."
docker compose up -d --build

# Step 7: Setup frontend
echo "🎨 Setting up frontend..."
cd web

# Copy environment file if it doesn't exist
if [ ! -f .env ]; then
    cp .env.example .env
    echo "   Created .env file from example"
fi

# Install frontend dependencies
echo "   Installing frontend dependencies..."
npm install

# Start frontend development server
echo "🚀 Starting frontend development server..."
npm run dev &
FRONTEND_PID=$!

# Wait a moment for frontend to start
sleep 3

echo ""
echo "✅ Fresh installation completed successfully!"
echo "================================================"
echo "🌐 Services running:"
echo "   Database:  http://localhost:5432"
echo "   API:       http://localhost:8000"
echo "   Frontend:  http://localhost:5173"
echo ""
echo "📋 Next steps:"
echo "   1. Open your browser to http://localhost:5173"
echo "   2. Navigate to 'XML Parser' in the sidebar"
echo "   3. Upload the /oldparser/cc.xml file to populate the database"
echo "   4. Test the Security Functional Requirements feature"
echo ""
echo "🛑 To stop all services:"
echo "   Press Ctrl+C to stop the frontend"
echo "   Run: docker compose down"
echo ""
echo "Frontend PID: $FRONTEND_PID"

# Keep the script running to show frontend output
wait $FRONTEND_PID
