"""
Database Session Management
============================

SQLAlchemy session management and database initialization.
Provides session factory and engine configuration for SQLite.

SQLite Benefits:
    - No separate database server required
    - Single file storage (portable)
    - Perfect for development and small-medium deployments
    - All SQL features needed for enterprise features
    - Easy backup (just copy the .db file)

Environment Variables (Optional):
    DATABASE_URL - Custom SQLite database path
    Default: sqlite:///./creative_automation.db
    
Usage:
    from src.database import init_database, get_session
    
    # Initialize database (creates tables)
    init_database()
    
    # Get session for queries
    with get_session() as session:
        tenants = session.query(Tenant).all()
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.pool import StaticPool
from contextlib import contextmanager
from pathlib import Path
from dotenv import load_dotenv

from .models import Base

# Load environment variables
load_dotenv()

# Database configuration
# SQLite database file will be created in the project root
DATABASE_URL = os.getenv(
    'DATABASE_URL',
    'sqlite:///./creative_automation.db'
)

# Ensure the database directory exists
if DATABASE_URL.startswith('sqlite:///'):
    db_path = DATABASE_URL.replace('sqlite:///', '')
    if '/' in db_path:
        db_dir = Path(db_path).parent
        db_dir.mkdir(parents=True, exist_ok=True)

# Create engine with SQLite-specific settings
# SQLite configuration optimized for concurrent access
engine = create_engine(
    DATABASE_URL,
    # Use StaticPool for SQLite to avoid connection issues
    # This keeps connections open for reuse
    poolclass=StaticPool,
    
    # Enable foreign key constraints (disabled by default in SQLite)
    connect_args={
        'check_same_thread': False,  # Allow multi-threaded access
        'timeout': 30  # Wait up to 30 seconds for lock to be released
    },
    
    # Set to True for SQL query logging (development only)
    echo=False
)

# Enable foreign keys for SQLite (must be done per connection)
from sqlalchemy import event
@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_conn, connection_record):
    """Enable foreign key support and other SQLite optimizations."""
    cursor = dbapi_conn.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.execute("PRAGMA journal_mode=WAL")  # Write-Ahead Logging for better concurrency
    cursor.execute("PRAGMA synchronous=NORMAL")  # Good balance of safety and speed
    cursor.execute("PRAGMA cache_size=-64000")  # 64MB cache
    cursor.execute("PRAGMA temp_store=MEMORY")  # Store temp tables in memory
    cursor.close()

# Session factory
SessionFactory = sessionmaker(bind=engine)

# Thread-safe session
Session = scoped_session(SessionFactory)


def get_engine():
    """
    Get the SQLAlchemy engine instance.
    
    Returns:
        Engine: SQLAlchemy engine
        
    Example:
        engine = get_engine()
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
    """
    return engine


def init_database():
    """
    Initialize database by creating all tables.
    
    This function creates all tables defined in models.py if they don't exist.
    Safe to call multiple times - won't recreate existing tables.
    
    For production, use Alembic migrations instead of calling this directly.
    
    Example:
        # In application startup
        init_database()
        
    Note:
        This does NOT handle schema migrations. Use Alembic for production:
            alembic revision --autogenerate -m "Initial migration"
            alembic upgrade head
    """
    try:
        # Create all tables
        Base.metadata.create_all(engine)
        print("✓ Database tables created successfully")
    except Exception as e:
        print(f"✗ Error creating database tables: {e}")
        raise


def drop_all_tables():
    """
    Drop all tables from the database.
    
    ⚠️ DANGEROUS: This will delete all data!
    Only use for testing or development.
    
    Example:
        # For testing cleanup
        drop_all_tables()
        init_database()  # Recreate fresh tables
    """
    try:
        Base.metadata.drop_all(engine)
        print("✓ All tables dropped")
    except Exception as e:
        print(f"✗ Error dropping tables: {e}")
        raise


def get_session():
    """
    Get a new database session.
    
    Returns a SQLAlchemy session that should be closed after use.
    Recommended to use with context manager for automatic cleanup.
    
    Returns:
        Session: SQLAlchemy session
        
    Example:
        # Manual session management
        session = get_session()
        try:
            tenants = session.query(Tenant).all()
        finally:
            session.close()
            
        # Better: Use context manager
        with get_session() as session:
            tenants = session.query(Tenant).all()
            # Session automatically closed on exit
    """
    return Session()


@contextmanager
def session_scope():
    """
    Provide a transactional scope for database operations.
    
    Context manager that handles commit/rollback automatically.
    Commits on success, rolls back on exception.
    
    Yields:
        Session: SQLAlchemy session
        
    Example:
        with session_scope() as session:
            new_tenant = Tenant(id=str(uuid.uuid4()), name="Acme Corp")
            session.add(new_tenant)
            # Automatically committed on exit
            # Automatically rolled back if exception occurs
    """
    session = Session()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def close_session():
    """
    Close the current thread-local session.
    
    Should be called at the end of request in web applications.
    
    Example:
        # In FastAPI
        @app.middleware("http")
        async def db_session_middleware(request, call_next):
            response = await call_next(request)
            close_session()
            return response
    """
    Session.remove()


# Database health check
def check_database_connection():
    """
    Check if database connection is working.
    
    Returns:
        bool: True if connection successful, False otherwise
        
    Example:
        if check_database_connection():
            print("Database is accessible")
        else:
            print("Cannot connect to database")
    """
    try:
        with engine.connect() as conn:
            conn.execute("SELECT 1")
        return True
    except Exception as e:
        print(f"Database connection failed: {e}")
        return False

