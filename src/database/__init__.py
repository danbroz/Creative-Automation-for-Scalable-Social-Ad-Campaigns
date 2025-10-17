"""
Database Module
===============

PostgreSQL database layer using SQLAlchemy ORM for enterprise features.
Provides models, session management, and database utilities for:
- Multi-tenant data isolation
- Analytics data storage
- A/B testing results
- Collaboration metadata
- CDN tracking

Usage:
    from src.database import get_session, init_database
    
    # Initialize database
    init_database()
    
    # Get database session
    session = get_session()
    try:
        # Use session for queries
        results = session.query(Campaign).all()
    finally:
        session.close()
"""

from .models import Base, Tenant, Campaign, ABTest, AnalyticsEvent, User
from .session import get_session, init_database, get_engine

__all__ = [
    'Base',
    'Tenant',
    'Campaign',
    'ABTest',
    'AnalyticsEvent',
    'User',
    'get_session',
    'init_database',
    'get_engine'
]

