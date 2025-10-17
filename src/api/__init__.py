"""
FastAPI Web Interface Module
=============================

REST API interface for the Creative Automation Pipeline.
Provides HTTP endpoints for campaign creation, status tracking, and asset management.

Features:
    - Campaign creation and management
    - Batch campaign processing
    - Real-time status tracking
    - Asset download and management
    - API key authentication
    - Rate limiting

Usage:
    # Start the API server
    uvicorn src.api.app:app --host 0.0.0.0 --port 8000
    
    # Or use the convenience script
    python -m src.api.app
"""

from .app import app

__all__ = ['app']

