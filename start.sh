#!/bin/bash

# TalentFlow-AI 2.0 - Start All Services (Bash)
# Usage: bash start.sh

echo "🚀 Starting TalentFlow-AI 2.0..."
echo ""

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Function to start a service
start_service() {
    local name=$1
    local command=$2
    local port=$3

    echo "📍 Starting $name on port $port..."
    eval "$command" &
    sleep 0.5
}

# Start Backend
start_service "Backend API" "cd \"$ROOT_DIR/backend\" && python -m uvicorn app:app --reload --port 8000" 8000

# Start Recruiter Dashboard
start_service "Recruiter Dashboard" "cd \"$ROOT_DIR/frontend/recruiter-dashboard\" && npm run dev" 3001

# Start Candidate Portal
start_service "Candidate Portal" "cd \"$ROOT_DIR/frontend/candidate-portal\" && npm run dev" 5173

echo ""
echo "✅ All services started!"
echo ""
echo "📊 URLs:"
echo "  Backend API:          http://localhost:8000"
echo "  API Docs:             http://localhost:8000/docs"
echo "  Recruiter Dashboard:  http://localhost:3001"
echo "  Candidate Portal:     http://localhost:5173"
echo ""
echo "💡 Tip: Press Ctrl+C to stop all services"
echo ""

# Keep the script running
wait
