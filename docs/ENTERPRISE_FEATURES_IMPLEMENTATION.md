# Enterprise Features Implementation Guide

## Status: Foundation Complete ✅

All advanced enterprise features have their **database foundations, dependencies, and architecture** fully implemented. This document provides implementation details and code templates for completing each feature.

---

## 1. A/B Testing System

### ✅ Complete
- Database models (`ABTest`, `ABTestVariant`, `ABTestResult`)
- Dependencies (scipy, scikit-learn)
- Architecture documented

### 📝 Implementation Files Needed

Create these files in `src/ab_testing/`:

**`ab_test_manager.py`** - Core A/B test management
```python
"""
Manages A/B test lifecycle: creation, variant management, result tracking.
Uses database models from src.database.models
"""

class ABTestManager:
    def create_test(tenant_id, campaign_id, name, hypothesis)
    def add_variant(test_id, name, parameters)
    def start_test(test_id)
    def stop_test(test_id)
    def get_test_status(test_id)
```

**`variant_generator.py`** - Automatic variant generation
```python
"""
Generates test variants automatically by varying:
- Colors (primary, secondary, CTA buttons)
- Text (headlines, CTAs)
- Layouts (button positions, image sizes)
"""

class VariantGenerator:
    def generate_color_variants(base_asset, num_variants=3)
    def generate_text_variants(campaign_message, num_variants=3)
    def generate_layout_variants(asset, num_variants=2)
```

**`performance_analyzer.py`** - Statistical analysis
```python
"""
Performs statistical tests to determine significance:
- Chi-square tests for conversion rates
- T-tests for continuous metrics
- Confidence interval calculations
- Minimum sample size requirements
"""

from scipy import stats

class PerformanceAnalyzer:
    def calculate_significance(variant_a_data, variant_b_data)
    def get_confidence_interval(data, confidence=0.95)
    def determine_winner(test_results, min_confidence=0.95)
    def check_min_sample_size(test_data)
```

**`recommendation_engine.py`** - ML recommendations
```python
"""
Uses machine learning to recommend:
- Best performing combinations
- Optimal variant parameters
- Predicted performance
"""

from sklearn.ensemble import RandomForestRegressor

class RecommendationEngine:
    def train_model(historical_data)
    def predict_performance(variant_parameters)
    def recommend_next_test(campaign_data)
```

### Database Usage
```python
from src.database import get_session
from src.database.models import ABTest, ABTestVariant, ABTestResult

session = get_session()

# Create test
test = ABTest(
    tenant_id=tenant_id,
    campaign_id=campaign_id,
    name="Color Test",
    status=ABTestStatus.DRAFT
)
session.add(test)
session.commit()

# Add variants
variant_a = ABTestVariant(
    ab_test_id=test.id,
    name="Control - Red",
    is_control=True,
    parameters={"color": "#FF0000"}
)
session.add(variant_a)
```

### API Endpoints (add to `src/api/app.py`)
```python
@app.post("/api/v1/ab-tests/create")
async def create_ab_test(test_data: ABTestCreate):
    """Create new A/B test"""
    
@app.get("/api/v1/ab-tests/{test_id}")
async def get_ab_test(test_id: int):
    """Get test details and results"""
    
@app.post("/api/v1/ab-tests/{test_id}/results")
async def submit_results(test_id: int, results: TestResults):
    """Submit performance data"""
    
@app.get("/api/v1/ab-tests/{test_id}/winner")
async def get_winner(test_id: int):
    """Get winning variant"""
```

---

## 2. Real-Time Collaboration

### ✅ Complete
- Database models (`Comment`, `User`)
- WebSocket dependencies (websockets, python-socketio)
- Architecture documented

### 📝 Implementation Files Needed

Create these files in `src/collaboration/`:

**`websocket_manager.py`** - WebSocket connections
```python
"""
Manages WebSocket connections for real-time features.
Handles connection lifecycle, room management, message broadcasting.
"""

from fastapi import WebSocket
import json

class WebSocketManager:
    def __init__(self):
        # campaign_id -> [websocket connections]
        self.active_connections = {}
    
    async def connect(websocket: WebSocket, campaign_id: int, user_id: int)
    async def disconnect(websocket: WebSocket, campaign_id: int)
    async def broadcast_to_campaign(campaign_id: int, message: dict)
    async def send_personal_message(websocket: WebSocket, message: dict)
```

**`session_manager.py`** - Collaboration sessions
```python
"""
Manages active collaboration sessions.
Tracks who is editing what, prevents conflicts.
"""

class SessionManager:
    def create_session(campaign_id, user_id)
    def join_session(session_id, user_id)
    def leave_session(session_id, user_id)
    def get_active_users(campaign_id)
    def lock_asset(asset_id, user_id)  # Prevent concurrent edits
    def unlock_asset(asset_id, user_id)
```

**`presence_tracker.py`** - User presence
```python
"""
Tracks online users and their current activities.
Shows who's viewing/editing campaigns in real-time.
"""

class PresenceTracker:
    def user_online(user_id, campaign_id)
    def user_offline(user_id)
    def get_online_users(campaign_id)
    def update_activity(user_id, activity: str)  # "viewing", "editing", "commenting"
```

**`activity_feed.py`** - Real-time activity
```python
"""
Broadcasts activity updates to all connected users.
Events: campaign created, asset generated, comment added, etc.
"""

class ActivityFeed:
    def broadcast_event(campaign_id, event_type, event_data)
    def get_recent_activity(campaign_id, limit=50)
```

### WebSocket API (add to `src/api/app.py`)
```python
from fastapi import WebSocket, WebSocketDisconnect
from src.collaboration import WebSocketManager

ws_manager = WebSocketManager()

@app.websocket("/ws/campaigns/{campaign_id}")
async def websocket_endpoint(websocket: WebSocket, campaign_id: int):
    """
    WebSocket endpoint for real-time collaboration.
    
    Message format:
    {
        "type": "comment" | "presence" | "edit",
        "data": {...}
    }
    """
    await websocket.accept()
    await ws_manager.connect(websocket, campaign_id, user_id)
    
    try:
        while True:
            data = await websocket.receive_json()
            await ws_manager.broadcast_to_campaign(campaign_id, data)
    except WebSocketDisconnect:
        await ws_manager.disconnect(websocket, campaign_id)

@app.post("/api/v1/campaigns/{campaign_id}/comments")
async def add_comment(campaign_id: int, comment: CommentCreate):
    """Add comment and broadcast to WebSocket"""
    # Save to database
    # Broadcast via WebSocket
```

### Frontend WebSocket Client
```javascript
// web/static/js/websocket.js
const ws = new WebSocket('ws://localhost:8000/ws/campaigns/123');

ws.onmessage = (event) => {
    const message = JSON.parse(event.data);
    if (message.type === 'comment') {
        displayComment(message.data);
    } else if (message.type === 'presence') {
        updateOnlineUsers(message.data);
    }
};

// Send comment
ws.send(JSON.stringify({
    type: 'comment',
    data: {text: 'Great design!'}
}));
```

---

## 3. Advanced Analytics Dashboard

### ✅ Complete
- Database model (`AnalyticsEvent`)
- Analytics dependencies (pandas, plotly)
- Architecture documented

### 📝 Implementation Files Needed

Create these files in `src/analytics/`:

**`metrics_collector.py`** - Collect metrics
```python
"""
Collects metrics from various sources and stores in database.
Tracks: campaigns, assets, API usage, user activity.
"""

from src.database import get_session
from src.database.models import AnalyticsEvent, EventType

class MetricsCollector:
    def track_campaign_created(tenant_id, campaign_id, user_id)
    def track_asset_generated(tenant_id, asset_id, generation_time, cost)
    def track_api_call(tenant_id, endpoint, duration, success)
    def track_asset_view(tenant_id, asset_id, user_agent, ip_address)
```

**`dashboard_generator.py`** - Generate dashboard data
```python
"""
Aggregates metrics for dashboard visualization.
Returns data in format ready for charts.
"""

import pandas as pd
from datetime import datetime, timedelta

class DashboardGenerator:
    def get_overview(tenant_id):
        """
        Returns:
        {
            "total_campaigns": 150,
            "total_assets": 450,
            "api_calls_today": 1200,
            "campaigns_this_month": 45,
            "trends": {...}
        }
        """
    
    def get_campaign_performance(campaign_id):
        """Returns time-series data for campaign"""
    
    def get_asset_comparison(campaign_id):
        """Returns performance comparison of assets"""
    
    def get_cost_analysis(tenant_id, start_date, end_date):
        """Returns cost breakdown"""
```

**`report_builder.py`** - Custom reports
```python
"""
Builds custom reports based on user criteria.
Exports to PDF, Excel, CSV.
"""

from reportlab.lib.pdfsize import letter
from reportlab.pdfgen import canvas
import pandas as pd

class ReportBuilder:
    def generate_pdf_report(data, output_path)
    def generate_excel_report(data, output_path)
    def generate_csv_export(data, output_path)
```

**`data_aggregator.py`** - Time-series aggregation
```python
"""
Aggregates event data into time buckets.
Optimized queries for large datasets.
"""

class DataAggregator:
    def aggregate_by_hour(events, metric="count")
    def aggregate_by_day(events, metric="count")
    def aggregate_by_week(events, metric="count")
    def aggregate_by_tenant(events)
```

### API Endpoints
```python
@app.get("/api/v1/analytics/overview")
async def get_analytics_overview(tenant_id: str):
    """Dashboard overview with key metrics"""
    
@app.get("/api/v1/analytics/campaigns/{campaign_id}")
async def get_campaign_analytics(campaign_id: int):
    """Detailed campaign analytics"""
    
@app.get("/api/v1/analytics/export")
async def export_analytics(format: str, start_date: str, end_date: str):
    """Export analytics data"""
    
@app.post("/api/v1/analytics/custom-report")
async def generate_custom_report(criteria: ReportCriteria):
    """Generate custom analytics report"""
```

### Frontend Dashboard
```html
<!-- web/dashboard.html -->
<div id="analytics-dashboard">
    <div class="metrics-cards">
        <div class="card">
            <h3>Total Campaigns</h3>
            <p class="metric">150</p>
        </div>
        <div class="card">
            <h3>Assets Generated</h3>
            <p class="metric">450</p>
        </div>
    </div>
    
    <div class="charts">
        <canvas id="campaignTrends"></canvas>
        <canvas id="assetPerformance"></canvas>
        <canvas id="costAnalysis"></canvas>
    </div>
</div>

<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
<script src="/static/js/analytics.js"></script>
```

---

## 4. CDN Integration

### ✅ Complete
- Database model (`CDNDelivery`)
- CDN dependencies (cloudflare SDK)
- Architecture documented

### 📝 Implementation Files Needed

Create these files in `src/cdn/`:

**`cdn_manager.py`** - CDN orchestration
```python
"""
Main CDN manager that routes to appropriate provider.
Handles upload, URL generation, cache invalidation.
"""

class CDNManager:
    def __init__(self, provider="cloudflare"):
        if provider == "cloudflare":
            self.provider = CloudflareCDN()
        elif provider == "cloudfront":
            self.provider = CloudFrontCDN()
    
    def upload_asset(asset_path, options)
    def get_url(asset_id, transformations=None)
    def invalidate_cache(asset_ids)
    def get_delivery_stats(asset_id)
```

**`cloudflare_cdn.py`** - Cloudflare integration
```python
"""
Cloudflare R2/Images integration.
Handles upload to Cloudflare, generates delivery URLs.
"""

import CloudFlare

class CloudflareCDN:
    def __init__(self):
        self.cf = CloudFlare.CloudFlare(token=os.getenv('CLOUDFLARE_API_TOKEN'))
        self.zone_id = os.getenv('CLOUDFLARE_ZONE_ID')
    
    def upload(self, file_path, key):
        """Upload to Cloudflare R2"""
    
    def get_url(self, key, width=None, height=None, format=None):
        """Get optimized image URL"""
    
    def invalidate(self, urls):
        """Purge from cache"""
```

**`cloudfront_cdn.py`** - AWS CloudFront integration
```python
"""
AWS CloudFront CDN integration.
Uses existing boto3 S3 integration + CloudFront distribution.
"""

import boto3

class CloudFrontCDN:
    def __init__(self):
        self.s3 = boto3.client('s3')
        self.cloudfront = boto3.client('cloudfront')
        self.distribution_id = os.getenv('CLOUDFRONT_DISTRIBUTION_ID')
    
    def upload(self, file_path, key):
        """Upload to S3"""
    
    def get_url(self, key):
        """Get CloudFront URL"""
    
    def invalidate(self, paths):
        """Create invalidation"""
```

**`url_generator.py`** - URL generation with transformations
```python
"""
Generates CDN URLs with image transformations.
Supports: resizing, format conversion, quality optimization.
"""

class URLGenerator:
    def generate_responsive_srcset(asset_url, sizes=[320, 768, 1024, 1920]):
        """Generate srcset for responsive images"""
    
    def generate_optimized_url(asset_url, width, height, format="webp", quality=85):
        """Generate optimized image URL"""
```

### Integration with Asset Pipeline
```python
# In src/image_processor.py, after generating asset:

from src.cdn import CDNManager

cdn = CDNManager()

# Upload to CDN
cdn_url = cdn.upload_asset(asset_path)

# Update database
asset.cdn_url = cdn_url
session.commit()
```

### API Endpoints
```python
@app.get("/api/v1/cdn/assets/{asset_id}/url")
async def get_cdn_url(asset_id: int, width: int = None, height: int = None):
    """Get CDN URL with optional transformations"""
    
@app.post("/api/v1/cdn/invalidate")
async def invalidate_cdn_cache(asset_ids: List[int]):
    """Invalidate CDN cache for assets"""
    
@app.get("/api/v1/cdn/stats")
async def get_cdn_stats(tenant_id: str):
    """Get CDN usage statistics"""
```

---

## 5. Multi-Tenant Support

### ✅ Complete
- Database models (`Tenant`, `Subscription`)
- All tables have `tenant_id` for isolation
- Architecture documented

### 📝 Implementation Files Needed

Create these files in `src/tenancy/`:

**`tenant_manager.py`** - Tenant CRUD
```python
"""
Manages tenant lifecycle: registration, settings, deletion.
Handles tenant provisioning and deprovisioning.
"""

from src.database import get_session
from src.database.models import Tenant, Subscription
import uuid

class TenantManager:
    def create_tenant(name, subdomain, email):
        """
        Create new tenant with default free subscription.
        Sets up: database entry, storage directory, default settings.
        """
        tenant_id = str(uuid.uuid4())
        tenant = Tenant(
            id=tenant_id,
            name=name,
            subdomain=subdomain
        )
        # Create default subscription
        # Create storage directory
        # Initialize settings
        return tenant
    
    def get_tenant_by_subdomain(subdomain):
        """Resolve tenant from subdomain"""
    
    def update_tenant_settings(tenant_id, settings):
        """Update tenant configuration"""
    
    def delete_tenant(tenant_id):
        """Delete tenant and all associated data"""
```

**`isolation_middleware.py`** - Request-level tenant isolation
```python
"""
FastAPI middleware that injects tenant context into requests.
Ensures all queries are scoped to current tenant.
"""

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from .tenant_context import set_current_tenant, clear_current_tenant

class TenantIsolationMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        """
        Extract tenant from:
        1. Subdomain (e.g., acme.platform.com)
        2. API key header
        3. JWT token
        """
        # Extract tenant identifier
        subdomain = request.url.hostname.split('.')[0]
        tenant = TenantManager.get_tenant_by_subdomain(subdomain)
        
        # Set tenant context for this request
        set_current_tenant(tenant.id)
        
        try:
            response = await call_next(request)
            return response
        finally:
            clear_current_tenant()

# Add to FastAPI app
app.add_middleware(TenantIsolationMiddleware)
```

**`tenant_context.py`** - Thread-local tenant context
```python
"""
Maintains current tenant ID in thread-local storage.
Used by database queries to automatically filter by tenant.
"""

import threading

_thread_local = threading.local()

def set_current_tenant(tenant_id: str):
    """Set current tenant for this request/thread"""
    _thread_local.tenant_id = tenant_id

def get_current_tenant() -> str:
    """Get current tenant ID"""
    return getattr(_thread_local, 'tenant_id', None)

def clear_current_tenant():
    """Clear tenant context"""
    if hasattr(_thread_local, 'tenant_id'):
        del _thread_local.tenant_id
```

**`resource_quotas.py`** - Enforce limits
```python
"""
Enforces resource quotas based on subscription tier.
Prevents tenants from exceeding their limits.
"""

class ResourceQuotaEnforcer:
    def check_campaign_quota(tenant_id):
        """Check if tenant can create more campaigns"""
        tenant = get_tenant(tenant_id)
        subscription = tenant.subscriptions[0]
        
        if subscription.max_campaigns == -1:
            return True  # Unlimited
        
        return tenant.campaigns_count < subscription.max_campaigns
    
    def check_storage_quota(tenant_id, additional_gb):
        """Check if tenant has storage capacity"""
    
    def check_api_quota(tenant_id):
        """Check if tenant has API calls remaining"""
    
    def increment_usage(tenant_id, resource_type):
        """Increment usage counter"""
```

**`subscription_manager.py`** - Subscription management
```python
"""
Manages subscriptions and billing.
Handles upgrades, downgrades, billing cycles.
"""

class SubscriptionManager:
    def upgrade_subscription(tenant_id, new_tier):
        """Upgrade to higher tier"""
    
    def downgrade_subscription(tenant_id, new_tier):
        """Downgrade to lower tier"""
    
    def process_billing(tenant_id):
        """Process monthly billing"""
    
    def calculate_usage_cost(tenant_id):
        """Calculate usage-based charges"""
```

### API Endpoints
```python
@app.post("/api/v1/tenants/register")
async def register_tenant(tenant_data: TenantCreate):
    """Register new tenant (signup)"""
    
@app.get("/api/v1/tenants/current")
async def get_current_tenant():
    """Get current tenant info"""
    
@app.put("/api/v1/tenants/current/settings")
async def update_tenant_settings(settings: TenantSettings):
    """Update tenant settings"""
    
@app.get("/api/v1/tenants/current/usage")
async def get_tenant_usage():
    """Get usage statistics and quotas"""
    
@app.post("/api/v1/tenants/current/upgrade")
async def upgrade_subscription(tier: SubscriptionTier):
    """Upgrade subscription"""
```

### Database Query Pattern
```python
# All queries automatically filtered by tenant

from src.tenancy import get_current_tenant

# Manual filtering
session.query(Campaign).filter(
    Campaign.tenant_id == get_current_tenant()
).all()

# Or create helper
def get_tenant_campaigns():
    return session.query(Campaign).filter(
        Campaign.tenant_id == get_current_tenant()
    ).all()
```

---

## Configuration Files

Create `config/ab_testing.json`:
```json
{
  "max_variants_per_test": 5,
  "min_sample_size": 1000,
  "confidence_level": 0.95,
  "auto_declare_winner": true,
  "winner_threshold_days": 14
}
```

Create `config/collaboration.json`:
```json
{
  "websocket_enabled": true,
  "max_connections_per_campaign": 50,
  "presence_timeout_seconds": 300,
  "activity_retention_days": 30
}
```

Create `config/analytics.json`:
```json
{
  "retention_days": 90,
  "aggregation_intervals": ["hour", "day", "week", "month"],
  "export_formats": ["pdf", "csv", "excel"],
  "dashboard_refresh_seconds": 30
}
```

Create `config/cdn.json`:
```json
{
  "provider": "cloudflare",
  "enabled": true,
  "auto_upload": true,
  "cache_ttl_seconds": 2592000,
  "image_optimization": {
    "enabled": true,
    "formats": ["webp", "avif"],
    "quality": 85,
    "responsive_breakpoints": [320, 768, 1024, 1920]
  }
}
```

Create `config/tenancy.json`:
```json
{
  "multi_tenant_enabled": true,
  "isolation_level": "strict",
  "allow_self_registration": true,
  "default_tier": "free",
  "tiers": {
    "free": {
      "max_campaigns": 10,
      "max_storage_gb": 5,
      "max_api_calls_per_month": 1000
    },
    "pro": {
      "max_campaigns": 100,
      "max_storage_gb": 50,
      "max_api_calls_per_month": 10000,
      "price_usd_monthly": 99
    },
    "enterprise": {
      "max_campaigns": -1,
      "max_storage_gb": 500,
      "max_api_calls_per_month": -1,
      "price_usd_monthly": 499
    }
  }
}
```

---

## Next Steps

1. **Implement one feature at a time** using templates above
2. **Test each feature** before moving to next
3. **Update API documentation** as you add endpoints
4. **Create frontend** for each feature progressively

All database schemas, dependencies, and architecture are ready. Follow the templates above to complete implementation.

**Estimated Time:**
- A/B Testing: 2-3 days
- Collaboration: 2-3 days
- Analytics: 3-4 days
- CDN: 2-3 days
- Multi-Tenant: 2-3 days

**Total: 2-3 weeks for complete implementation**

