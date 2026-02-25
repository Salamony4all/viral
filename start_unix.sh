#!/bin/bash

# Start the entire Viral Engine stack on macOS/Linux

echo ""
echo "╔════════════════════════════════════════╗"
echo "║   VIRAL ENGINE - STARTUP SEQUENCE      ║"
echo "╚════════════════════════════════════════╝"
echo ""

# Check if Ollama is running
echo "[1/3] Checking Ollama..."
if ! curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    echo "⚠️  Ollama is not running!"
    echo "Run this in a separate terminal:"
    echo "  ollama serve"
    echo ""
    read -p "Press Enter to continue..."
fi

# Start the backend API
echo "[2/3] Starting Backend API..."
python api.py &
BACKEND_PID=$!
echo "✅ Backend started on http://localhost:8000"
echo ""

# Start the frontend
echo "[3/3] Starting Frontend..."
cd frontend
if [ ! -d "node_modules" ]; then
    echo "Installing dependencies..."
    npm install
fi

echo "✅ Frontend starting on http://localhost:3000"
npm run dev &
FRONTEND_PID=$!

sleep 2

echo ""
echo "╔════════════════════════════════════════╗"
echo "║       🚀 VIRAL ENGINE IS LIVE! 🚀      ║"
echo "║   Open: http://localhost:3000          ║"
echo "║                                        ║"
echo "║ Press Ctrl+C to stop all services     ║"
echo "╚════════════════════════════════════════╝"
echo ""

# Wait for both processes
wait $BACKEND_PID $FRONTEND_PID

echo "Shutdown complete"
