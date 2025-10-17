# Database Setup Guide

## PostgreSQL Installation and Configuration

### 1. Install PostgreSQL

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install postgresql postgresql-contrib
```

**macOS:**
```bash
brew install postgresql@15
brew services start postgresql@15
```

**Windows:**
Download and install from https://www.postgresql.org/download/windows/

### 2. Create Database

```bash
# Access PostgreSQL
sudo -u postgres psql

# Create database
CREATE DATABASE creative_automation;

# Create user (optional)
CREATE USER creative_user WITH PASSWORD 'your_secure_password';

# Grant privileges
GRANT ALL PRIVILEGES ON DATABASE creative_automation TO creative_user;

# Exit
\q
```

### 3. Configure Environment

Edit `.env` file:
```bash
DATABASE_URL=postgresql://creative_user:your_secure_password@localhost:5432/creative_automation
```

Or for default postgres user:
```bash
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/creative_automation
```

### 4. Initialize Database

**Method A: Direct initialization (Development)**
```python
python -c "from src.database import init_database; init_database()"
```

**Method B: Alembic migrations (Production - Recommended)**
```bash
# Initialize Alembic (first time only)
alembic init alembic

# Create initial migration
alembic revision --autogenerate -m "Initial schema"

# Apply migrations
alembic upgrade head
```

### 5. Verify Installation

```python
# Test connection
python -c "from src.database import check_database_connection; print('✓ Connected' if check_database_connection() else '✗ Failed')"
```

## Database Schema

The system uses 15+ tables organized into logical domains:

### Core Tables
- `tenants` - Multi-tenant organizations
- `subscriptions` - Billing and subscription tiers
- `users` - User accounts scoped to tenants
- `campaigns` - Marketing campaigns
- `assets` - Generated creative assets

### A/B Testing
- `ab_tests` - Experiment definitions
- `ab_test_variants` - Test variations
- `ab_test_results` - Performance metrics

### Analytics
- `analytics_events` - Event tracking
- `comments` - Collaboration comments

### CDN
- `cdn_deliveries` - CDN upload tracking

## Migration Commands

```bash
# Create new migration
alembic revision --autogenerate -m "Description of changes"

# Apply migrations
alembic upgrade head

# Rollback last migration
alembic downgrade -1

# Show current version
alembic current

# Show migration history
alembic history
```

## Backup and Restore

### Backup
```bash
pg_dump -U postgres creative_automation > backup.sql
```

### Restore
```bash
psql -U postgres creative_automation < backup.sql
```

## Production Considerations

### Connection Pooling
The application uses SQLAlchemy's connection pooling:
- Pool size: 10 connections
- Max overflow: 20 additional connections
- Pre-ping enabled for connection validation

### Performance Optimization
1. **Indexes**: All foreign keys and frequently queried columns have indexes
2. **Composite Indexes**: Multi-column indexes for common query patterns
3. **JSONB**: Use JSONB columns for flexible metadata storage

### Security
1. **Use strong passwords** for database users
2. **Limit network access** to PostgreSQL port (5432)
3. **Enable SSL** for production connections
4. **Regular backups** with point-in-time recovery
5. **Monitor connection usage** to prevent exhaustion

### Monitoring
```sql
-- Check active connections
SELECT count(*) FROM pg_stat_activity;

-- Check database size
SELECT pg_size_pretty(pg_database_size('creative_automation'));

-- Check table sizes
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
```

## Troubleshooting

### Connection Refused
```bash
# Check if PostgreSQL is running
sudo systemctl status postgresql

# Start PostgreSQL
sudo systemctl start postgresql
```

### Authentication Failed
```bash
# Edit pg_hba.conf to allow password authentication
sudo nano /etc/postgresql/15/main/pg_hba.conf

# Change METHOD from 'peer' to 'md5' for local connections
# Restart PostgreSQL
sudo systemctl restart postgresql
```

### Permission Denied
```sql
-- Grant necessary permissions
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO creative_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO creative_user;
```

## Docker PostgreSQL (Alternative)

For development, use Docker:

```bash
# Run PostgreSQL in Docker
docker run --name creative-postgres \
    -e POSTGRES_PASSWORD=postgres \
    -e POSTGRES_DB=creative_automation \
    -p 5432:5432 \
    -d postgres:15

# Initialize database
python -c "from src.database import init_database; init_database()"
```

Add to `docker-compose.yml`:
```yaml
services:
  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: creative_automation
      POSTGRES_PASSWORD: postgres
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

