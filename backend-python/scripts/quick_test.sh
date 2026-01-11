#!/bin/bash
# Quick Test Script for MVP

set -e

echo "🧪 Quick MVP Test"
echo "================="
echo ""

# Check if server is running
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ Server is running"
    
    # Test health endpoint
    echo ""
    echo "Testing health endpoint..."
    curl -s http://localhost:8000/health | python3 -m json.tool
    
    # Test root endpoint
    echo ""
    echo "Testing root endpoint..."
    curl -s http://localhost:8000/ | python3 -m json.tool
    
    # Test concepts endpoint
    echo ""
    echo "Testing concepts endpoint..."
    curl -s http://localhost:8000/api/v1/concepts | python3 -m json.tool
    
    echo ""
    echo "✅ Basic API tests complete"
else
    echo "⚠️  Server not running"
    echo "Start server with: uvicorn app.main:app --reload"
    exit 1
fi
