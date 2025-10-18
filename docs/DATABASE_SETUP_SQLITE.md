# SQLite Database Setup Guide

## Overview

The system uses **SQLite** as its database, which provides:
- ✅ **No server required** - Database is a single file
- ✅ **Zero configuration** - Works out of the box
- ✅ **Portable** - Easy to backup and move
- ✅ **Fast** - Excellent performance for most use cases
- ✅ **Reliable** - Production-ready, used by millions of applications

## Quick Start

### 1. Automatic Initialization

The database is automatically created when you first run the application:

```bash
# Initialize database (creates creative_automation.db)
python -c "from src.database import init_database; init_database()"
```

This creates `creative_automation.db` in your project root.

### 2. Verify Installation

```python
# Test connection
python -c "from src.database import check_database_connection; print('✓ Connected' if check_database_connection() else '✗ Failed')"
```

## Database File Location

**Default:** `./creative_automation.db` (project root)

**Custom location** via environment variable:
```bash
# In .env file
DATABASE_URL=sqlite:///./data/my_database.db
```

## Database Schema

The system automatically creates 15+ tables:

### Core Tables
- `tenants` - Multi-tenant organizations
- `subscriptions` - Billing and subscription tiers
- `users` - User accounts scoped to tenants
- `campaigns` - Marketing campaigns
- `assets` - Generated creative assets

### Feature Tables
- `ab_tests`, `ab_test_variants`, `ab_test_results` - A/B testing
- `analytics_events` - Event tracking
- `comments` - Collaboration
- `cdn_deliveries` - CDN tracking

## Backup and Restore

### Backup (Simple File Copy)
```bash
# Stop the application first
cp creative_automation.db creative_automation_backup_$(date +%Y%m%d).db
```

### Restore
```bash
# Stop the application first
cp creative_automation_backup_20240101.db creative_automation.db
```

### Automated Backup Script
```bash
#!/bin/bash
# backup_database.sh
DATE=$(date +%Y%m%d_%H%M%S)
cp creative_automation.db backups/creative_automation_$DATE.db
echo "Backup created: backups/creative_automation_$DATE.db"
```

## Database Migrations

Use Alembic for schema changes:

```bash
# Create migration
alembic revision --autogenerate -m "Description of changes"

# Apply migrations
alembic upgrade head

# Rollback last migration
alembic downgrade -1
```

## Performance Optimization

SQLite is already optimized with:

### Enabled Optimizations
- ✅ **WAL Mode** (Write-Ahead Logging) - Better concurrency
- ✅ **Foreign Keys** - Data integrity enforced
- ✅ **64MB Cache** - Faster queries
- ✅ **Memory Temp Store** - Faster temporary operations

### Monitor Database Size
```python
import os
size_mb = os.path.getsize('creative_automation.db') / (1024 * 1024)
print(f"Database size: {size_mb:.2f} MB")
```

### Vacuum Database (Reclaim Space)
```bash
sqlite3 creative_automation.db "VACUUM;"
```

## Concurrent Access

SQLite supports multiple concurrent readers and one writer:
- ✅ **Multiple reads** simultaneously
- ✅ **Queued writes** (30 second timeout)
- ✅ **Thread-safe** with `check_same_thread=False`

## Limitations & When to Upgrade

SQLite is excellent for most use cases, but consider PostgreSQL if:
- ❌ Very high concurrent writes (>100/second sustained)
- ❌ Database size >100GB
- ❌ Need distributed/replicated setup
- ❌ Multiple application servers accessing same database

**For most applications, SQLite is perfect!**

## Database Tools

### Command Line Interface
```bash
# Open database in SQLite CLI
sqlite3 creative_automation.db

# Common commands:
.tables              # List all tables
.schema tenants      # Show table schema
SELECT * FROM tenants;  # Query data
.quit                # Exit
```

### GUI Tools
- **DB Browser for SQLite** (Free) - https://sqlitebrowser.org/
- **TablePlus** (Free/Paid) - https://tableplus.com/
- **DBeaver** (Free) - https://dbeaver.io/

### Python Inspection
```python
from src.database import get_engine
from sqlalchemy import inspect

engine = get_engine()
inspector = inspect(engine)

# List all tables
print("Tables:", inspector.get_table_names())

# Get table columns
for column in inspector.get_columns('tenants'):
    print(f"- {column['name']}: {column['type']}")
```

## Troubleshooting

### Database Locked Error
```
sqlite3.OperationalError: database is locked
```

**Solution:**
- Check if another process is accessing the database
- Increase timeout in `DATABASE_URL`:
  ```python
  sqlite:///./creative_automation.db?timeout=30000
  ```

### Foreign Key Constraint Failed
```
IntegrityError: FOREIGN KEY constraint failed
```

**Solution:**
- Ensure parent records exist before creating child records
- Check the order of operations in your code

### Database File Permissions
```bash
# Ensure the database file is writable
chmod 644 creative_automation.db
```

## Production Deployment

### Docker
SQLite works great in Docker containers:

```dockerfile
# In Dockerfile
VOLUME ["/app/data"]

# Mount database directory
# docker run -v ./data:/app/data myapp
```

### Multiple Instances
For multiple application instances, use a shared file system:
- NFS mount
- AWS EFS
- Azure Files

Or migrate to PostgreSQL for better multi-instance support.

## Migration from SQLite to PostgreSQL (Future)

If you need to migrate later:

```bash
# Install pgloader
sudo apt-get install pgloader

# Convert database
pgloader creative_automation.db postgresql://user:pass@localhost/dbname
```

Or use Alembic migrations to recreate schema in PostgreSQL.

## Best Practices

✅ **DO:**
- Backup regularly (automated script)
- Use WAL mode (already enabled)
- Close connections properly
- Use transactions for related writes

❌ **DON'T:**
- Put database file in shared network drive (use local SSD)
- Run VACUUM during high traffic
- Use NFS for multi-server setups
- Store large blobs (>10MB) - use file storage instead

## Example: Query the Database

```python
from src.database import get_session
from src.database.models import Tenant, Campaign

# Get all tenants
with get_session() as session:
    tenants = session.query(Tenant).all()
    for tenant in tenants:
        print(f"Tenant: {tenant.name}")
        
        # Get tenant campaigns
        campaigns = session.query(Campaign).filter(
            Campaign.tenant_id == tenant.id
        ).all()
        print(f"  Campaigns: {len(campaigns)}")
```

## Summary

SQLite provides an excellent database solution for the Creative Automation Platform:
- 🚀 **Zero setup** - No database server to install
- 💾 **Single file** - Easy backup and portability  
- ⚡ **Fast** - Optimized for read-heavy workloads
- 🔒 **Reliable** - ACID compliant, battle-tested
- 📈 **Scalable** - Handles millions of rows easily

Perfect for development, testing, and production deployments with <100 concurrent users!

