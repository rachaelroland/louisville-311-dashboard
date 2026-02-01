#!/bin/bash
# Louisville Metro 311 NLP Dashboard Launcher
# Quick start script for the interactive dashboard

echo "🚀 Louisville Metro 311 NLP Analysis Dashboard"
echo "================================================"
echo ""
echo "📦 Installing dependencies..."
uv pip install -q fasthtml pandas plotly uvicorn

echo ""
echo "🔄 Starting dashboard..."
echo ""
echo "Dashboard will be available at:"
echo "  👉 http://localhost:5002"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

PORT=5002 uv run python dashboard_app.py
