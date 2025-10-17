"""
SQLAlchemy Database Models
===========================

Comprehensive database schema for enterprise features including:
- Multi-tenant support with complete data isolation
- Campaign and asset management
- A/B testing experiments and results
- Analytics events and metrics
- Collaboration and user management
- Subscription and billing
- CDN tracking

All models include tenant_id for multi-tenant isolation (except Tenant model itself).
"""

from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, Text, ForeignKey, JSON, Index, Enum as SQLEnum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
import enum

# Base class for all models
Base = declarative_base()


# Enums for type safety
class SubscriptionTier(enum.Enum):
    """Subscription tier levels."""
    FREE = "free"
    PRO = "pro"
    ENTERPRISE = "enterprise"


class ABTestStatus(enum.Enum):
    """A/B test lifecycle states."""
    DRAFT = "draft"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class EventType(enum.Enum):
    """Analytics event types."""
    CAMPAIGN_CREATED = "campaign_created"
    CAMPAIGN_COMPLETED = "campaign_completed"
    ASSET_GENERATED = "asset_generated"
    ASSET_VIEWED = "asset_viewed"
    ASSET_CLICKED = "asset_clicked"
    AB_TEST_STARTED = "ab_test_started"
    API_CALL = "api_call"
    USER_LOGIN = "user_login"


# ============================================================================
# Multi-Tenant Models
# ============================================================================

class Tenant(Base):
    """
    Tenant (Organization) Model
    
    Represents a single organization/customer in the multi-tenant system.
    Each tenant has complete data isolation from other tenants.
    
    Attributes:
        id (str): Unique tenant identifier (UUID)
        name (str): Organization name
        subdomain (str): Unique subdomain for tenant (e.g., 'acme' -> acme.platform.com)
        subscription_tier (SubscriptionTier): Current subscription level
        is_active (bool): Whether tenant account is active
        created_at (datetime): When tenant was created
        updated_at (datetime): Last update timestamp
        settings (JSON): Tenant-specific configuration
        branding (JSON): Custom branding (logo, colors, etc.)
        
        # Resource usage tracking
        campaigns_count (int): Number of campaigns created
        storage_used_gb (float): Storage consumed in GB
        api_calls_this_month (int): API calls made this billing cycle
        
        # Relationships
        users (List[User]): Users belonging to this tenant
        campaigns (List[Campaign]): Campaigns owned by tenant
        ab_tests (List[ABTest]): A/B tests for tenant
        analytics_events (List[AnalyticsEvent]): Analytics data
    
    Indexes:
        - subdomain (unique) for fast tenant resolution
        - subscription_tier for billing queries
    """
    __tablename__ = 'tenants'
    
    # Primary identification
    id = Column(String(36), primary_key=True)  # UUID
    name = Column(String(255), nullable=False)
    subdomain = Column(String(63), unique=True, nullable=False, index=True)
    
    # Subscription and status
    subscription_tier = Column(SQLEnum(SubscriptionTier), default=SubscriptionTier.FREE, nullable=False, index=True)
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    
    # Configuration (stored as JSON)
    settings = Column(JSON, default={})
    branding = Column(JSON, default={})  # {logo_url, primary_color, secondary_color}
    
    # Resource usage tracking
    campaigns_count = Column(Integer, default=0)
    storage_used_gb = Column(Float, default=0.0)
    api_calls_this_month = Column(Integer, default=0)
    
    # Relationships
    users = relationship("User", back_populates="tenant", cascade="all, delete-orphan")
    campaigns = relationship("Campaign", back_populates="tenant", cascade="all, delete-orphan")
    ab_tests = relationship("ABTest", back_populates="tenant", cascade="all, delete-orphan")
    analytics_events = relationship("AnalyticsEvent", back_populates="tenant", cascade="all, delete-orphan")
    subscriptions = relationship("Subscription", back_populates="tenant", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Tenant(id={self.id}, name={self.name}, tier={self.subscription_tier.value})>"


class Subscription(Base):
    """
    Subscription and Billing Model
    
    Tracks subscription details, billing history, and resource quotas for each tenant.
    
    Attributes:
        id (int): Unique subscription ID
        tenant_id (str): Foreign key to tenant
        tier (SubscriptionTier): Subscription tier
        status (str): Active, cancelled, past_due, etc.
        billing_cycle (str): monthly, annual
        price_per_month (float): Subscription price
        started_at (datetime): Subscription start date
        expires_at (datetime): Subscription expiry (None for active)
        auto_renew (bool): Whether to auto-renew
        
        # Resource quotas based on tier
        max_campaigns (int): Maximum campaigns allowed (-1 = unlimited)
        max_storage_gb (int): Maximum storage in GB
        max_api_calls_per_month (int): Monthly API call limit
        
        # Stripe integration (optional)
        stripe_customer_id (str): Stripe customer ID
        stripe_subscription_id (str): Stripe subscription ID
    """
    __tablename__ = 'subscriptions'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    tenant_id = Column(String(36), ForeignKey('tenants.id'), nullable=False, index=True)
    
    # Subscription details
    tier = Column(SQLEnum(SubscriptionTier), nullable=False)
    status = Column(String(50), default='active')  # active, cancelled, past_due, trialing
    billing_cycle = Column(String(20), default='monthly')  # monthly, annual
    price_per_month = Column(Float, default=0.0)
    
    # Dates
    started_at = Column(DateTime, default=func.now())
    expires_at = Column(DateTime, nullable=True)
    cancelled_at = Column(DateTime, nullable=True)
    auto_renew = Column(Boolean, default=True)
    
    # Resource quotas (set based on tier)
    max_campaigns = Column(Integer, default=10)  # -1 = unlimited
    max_storage_gb = Column(Integer, default=5)
    max_api_calls_per_month = Column(Integer, default=1000)
    
    # Payment integration
    stripe_customer_id = Column(String(255), nullable=True)
    stripe_subscription_id = Column(String(255), nullable=True)
    
    # Relationships
    tenant = relationship("Tenant", back_populates="subscriptions")
    
    __table_args__ = (
        Index('idx_subscription_tenant_status', 'tenant_id', 'status'),
    )


# ============================================================================
# User and Authentication Models
# ============================================================================

class User(Base):
    """
    User Model
    
    Represents individual users within a tenant. Users are scoped to tenants
    and can have different roles and permissions.
    
    Attributes:
        id (int): Unique user ID
        tenant_id (str): Foreign key to tenant
        email (str): User email (unique within tenant)
        full_name (str): User's full name
        password_hash (str): Bcrypt password hash
        role (str): User role (admin, editor, viewer)
        is_active (bool): Whether account is active
        created_at (datetime): Account creation date
        last_login (datetime): Last successful login
        settings (JSON): User preferences
    """
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    tenant_id = Column(String(36), ForeignKey('tenants.id'), nullable=False, index=True)
    
    # Authentication
    email = Column(String(255), nullable=False)
    password_hash = Column(String(255), nullable=False)
    
    # Profile
    full_name = Column(String(255), nullable=False)
    role = Column(String(50), default='viewer')  # admin, editor, viewer
    is_active = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    last_login = Column(DateTime, nullable=True)
    
    # User preferences
    settings = Column(JSON, default={})
    
    # Relationships
    tenant = relationship("Tenant", back_populates="users")
    comments = relationship("Comment", back_populates="user", cascade="all, delete-orphan")
    
    __table_args__ = (
        Index('idx_user_tenant_email', 'tenant_id', 'email', unique=True),
    )


# ============================================================================
# Campaign Models
# ============================================================================

class Campaign(Base):
    """
    Campaign Model
    
    Represents a marketing campaign with generated assets. Links to tenant
    for multi-tenant isolation and tracks campaign lifecycle.
    
    Attributes:
        id (int): Unique campaign ID
        tenant_id (str): Foreign key to tenant
        name (str): Campaign name
        status (str): draft, in_progress, completed, failed
        brief_data (JSON): Original campaign brief
        output_path (str): Path to generated assets
        language (str): Target language code
        created_at (datetime): Creation timestamp
        completed_at (datetime): Completion timestamp
        metrics (JSON): Performance metrics
        
    Relationships:
        assets (List[Asset]): Generated assets
        ab_tests (List[ABTest]): Associated A/B tests
    """
    __tablename__ = 'campaigns'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    tenant_id = Column(String(36), ForeignKey('tenants.id'), nullable=False, index=True)
    
    # Campaign details
    name = Column(String(255), nullable=False)
    status = Column(String(50), default='draft', index=True)
    brief_data = Column(JSON, nullable=False)  # Original campaign brief
    output_path = Column(String(500), nullable=True)
    language = Column(String(10), default='en')
    
    # Timestamps
    created_at = Column(DateTime, default=func.now(), nullable=False, index=True)
    completed_at = Column(DateTime, nullable=True)
    
    # Performance metrics
    metrics = Column(JSON, default={})  # {views, clicks, conversions, cost}
    
    # Relationships
    tenant = relationship("Tenant", back_populates="campaigns")
    assets = relationship("Asset", back_populates="campaign", cascade="all, delete-orphan")
    ab_tests = relationship("ABTest", back_populates="campaign", cascade="all, delete-orphan")
    comments = relationship("Comment", back_populates="campaign", cascade="all, delete-orphan")
    
    __table_args__ = (
        Index('idx_campaign_tenant_status', 'tenant_id', 'status'),
        Index('idx_campaign_created', 'created_at'),
    )


class Asset(Base):
    """
    Asset Model
    
    Individual generated assets (images, videos) within a campaign.
    Tracks CDN URLs, performance metrics, and metadata.
    
    Attributes:
        id (int): Unique asset ID
        campaign_id (int): Foreign key to campaign
        tenant_id (str): Foreign key to tenant (for isolation)
        product_name (str): Product this asset represents
        aspect_ratio (str): 1:1, 9:16, 16:9
        file_type (str): image, video
        local_path (str): Local storage path
        cdn_url (str): CDN delivery URL
        file_size_bytes (int): File size
        metadata (JSON): Asset metadata
        metrics (JSON): Performance metrics
    """
    __tablename__ = 'assets'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    campaign_id = Column(Integer, ForeignKey('campaigns.id'), nullable=False, index=True)
    tenant_id = Column(String(36), ForeignKey('tenants.id'), nullable=False, index=True)
    
    # Asset details
    product_name = Column(String(255), nullable=False)
    aspect_ratio = Column(String(10), nullable=False)  # 1:1, 9:16, 16:9
    file_type = Column(String(20), default='image')  # image, video
    local_path = Column(String(500), nullable=False)
    cdn_url = Column(String(500), nullable=True)
    file_size_bytes = Column(Integer, nullable=True)
    
    # Metadata
    metadata = Column(JSON, default={})  # {width, height, format, etc.}
    created_at = Column(DateTime, default=func.now())
    
    # Performance tracking
    metrics = Column(JSON, default={})  # {views, clicks, conversions}
    
    # Relationships
    campaign = relationship("Campaign", back_populates="assets")
    
    __table_args__ = (
        Index('idx_asset_campaign', 'campaign_id'),
        Index('idx_asset_tenant', 'tenant_id'),
    )


# ============================================================================
# A/B Testing Models
# ============================================================================

class ABTest(Base):
    """
    A/B Test Model
    
    Represents an A/B testing experiment with multiple variants.
    Tracks performance of each variant to determine winner.
    
    Attributes:
        id (int): Unique test ID
        tenant_id (str): Foreign key to tenant
        campaign_id (int): Foreign key to campaign
        name (str): Test name
        status (ABTestStatus): Current test status
        hypothesis (str): What we're testing
        created_at (datetime): Test creation date
        started_at (datetime): When test went live
        ended_at (datetime): When test completed
        winner_variant_id (int): ID of winning variant
        confidence_level (float): Statistical confidence (0-1)
        
    Relationships:
        variants (List[ABTestVariant]): Test variants
        results (List[ABTestResult]): Performance results
    """
    __tablename__ = 'ab_tests'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    tenant_id = Column(String(36), ForeignKey('tenants.id'), nullable=False, index=True)
    campaign_id = Column(Integer, ForeignKey('campaigns.id'), nullable=True, index=True)
    
    # Test details
    name = Column(String(255), nullable=False)
    status = Column(SQLEnum(ABTestStatus), default=ABTestStatus.DRAFT, nullable=False, index=True)
    hypothesis = Column(Text, nullable=True)
    description = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    started_at = Column(DateTime, nullable=True)
    ended_at = Column(DateTime, nullable=True)
    
    # Results
    winner_variant_id = Column(Integer, nullable=True)
    confidence_level = Column(Float, default=0.0)  # 0.0 to 1.0
    
    # Test configuration
    config = Column(JSON, default={})  # {traffic_split, min_sample_size, etc.}
    
    # Relationships
    tenant = relationship("Tenant", back_populates="ab_tests")
    campaign = relationship("Campaign", back_populates="ab_tests")
    variants = relationship("ABTestVariant", back_populates="ab_test", cascade="all, delete-orphan")
    results = relationship("ABTestResult", back_populates="ab_test", cascade="all, delete-orphan")
    
    __table_args__ = (
        Index('idx_abtest_tenant_status', 'tenant_id', 'status'),
    )


class ABTestVariant(Base):
    """
    A/B Test Variant Model
    
    Individual variant within an A/B test. Each variant represents
    a different version of the creative (different text, colors, layout, etc.)
    
    Attributes:
        id (int): Unique variant ID
        ab_test_id (int): Foreign key to AB test
        name (str): Variant name (A, B, C, etc.)
        description (str): What makes this variant different
        asset_id (int): Foreign key to asset (if applicable)
        parameters (JSON): Variant parameters
        is_control (bool): Whether this is the control variant
    """
    __tablename__ = 'ab_test_variants'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    ab_test_id = Column(Integer, ForeignKey('ab_tests.id'), nullable=False, index=True)
    
    # Variant details
    name = Column(String(50), nullable=False)  # A, B, C, etc.
    description = Column(Text, nullable=True)
    asset_id = Column(Integer, ForeignKey('assets.id'), nullable=True)
    is_control = Column(Boolean, default=False)
    
    # Variant configuration
    parameters = Column(JSON, default={})  # {color, text, layout, etc.}
    
    # Relationships
    ab_test = relationship("ABTest", back_populates="variants")
    results = relationship("ABTestResult", back_populates="variant", cascade="all, delete-orphan")


class ABTestResult(Base):
    """
    A/B Test Result Model
    
    Stores performance data for each variant during the test.
    Used for statistical analysis to determine winner.
    
    Attributes:
        id (int): Unique result ID
        ab_test_id (int): Foreign key to AB test
        variant_id (int): Foreign key to variant
        impressions (int): Number of times shown
        clicks (int): Number of clicks
        conversions (int): Number of conversions
        revenue (float): Revenue generated
        recorded_at (datetime): When this data was recorded
    """
    __tablename__ = 'ab_test_results'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    ab_test_id = Column(Integer, ForeignKey('ab_tests.id'), nullable=False, index=True)
    variant_id = Column(Integer, ForeignKey('ab_test_variants.id'), nullable=False, index=True)
    
    # Performance metrics
    impressions = Column(Integer, default=0)
    clicks = Column(Integer, default=0)
    conversions = Column(Integer, default=0)
    revenue = Column(Float, default=0.0)
    
    # Timestamp
    recorded_at = Column(DateTime, default=func.now(), index=True)
    
    # Relationships
    ab_test = relationship("ABTest", back_populates="results")
    variant = relationship("ABTestVariant", back_populates="results")
    
    __table_args__ = (
        Index('idx_result_test_variant', 'ab_test_id', 'variant_id'),
    )


# ============================================================================
# Analytics Models
# ============================================================================

class AnalyticsEvent(Base):
    """
    Analytics Event Model
    
    Stores all analytics events for tracking user behavior, system performance,
    and business metrics. Events are aggregated for dashboard visualization.
    
    Attributes:
        id (int): Unique event ID
        tenant_id (str): Foreign key to tenant
        event_type (EventType): Type of event
        event_data (JSON): Event-specific data
        user_id (int): User who triggered event (nullable)
        session_id (str): Session identifier
        ip_address (str): Client IP (hashed for privacy)
        user_agent (str): Browser user agent
        created_at (datetime): Event timestamp
    """
    __tablename__ = 'analytics_events'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    tenant_id = Column(String(36), ForeignKey('tenants.id'), nullable=False, index=True)
    
    # Event details
    event_type = Column(SQLEnum(EventType), nullable=False, index=True)
    event_data = Column(JSON, default={})  # Flexible event data
    
    # User tracking
    user_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    session_id = Column(String(255), nullable=True, index=True)
    
    # Request metadata
    ip_address = Column(String(45), nullable=True)  # IPv6 compatible
    user_agent = Column(String(500), nullable=True)
    
    # Timestamp
    created_at = Column(DateTime, default=func.now(), nullable=False, index=True)
    
    # Relationships
    tenant = relationship("Tenant", back_populates="analytics_events")
    
    __table_args__ = (
        Index('idx_analytics_tenant_type_time', 'tenant_id', 'event_type', 'created_at'),
    )


# ============================================================================
# Collaboration Models
# ============================================================================

class Comment(Base):
    """
    Comment Model
    
    User comments on campaigns and assets for collaboration.
    Supports threaded conversations and mentions.
    
    Attributes:
        id (int): Unique comment ID
        tenant_id (str): Foreign key to tenant
        campaign_id (int): Foreign key to campaign
        user_id (int): User who posted comment
        parent_id (int): Parent comment for threading
        content (Text): Comment text
        mentions (JSON): List of mentioned user IDs
        created_at (datetime): Comment timestamp
        updated_at (datetime): Last edit timestamp
        is_resolved (bool): Whether comment thread is resolved
    """
    __tablename__ = 'comments'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    tenant_id = Column(String(36), ForeignKey('tenants.id'), nullable=False, index=True)
    campaign_id = Column(Integer, ForeignKey('campaigns.id'), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    
    # Comment threading
    parent_id = Column(Integer, ForeignKey('comments.id'), nullable=True)
    
    # Content
    content = Column(Text, nullable=False)
    mentions = Column(JSON, default=[])  # List of user IDs mentioned
    
    # Status
    is_resolved = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="comments")
    campaign = relationship("Campaign", back_populates="comments")
    replies = relationship("Comment", remote_side=[parent_id])
    
    __table_args__ = (
        Index('idx_comment_campaign_created', 'campaign_id', 'created_at'),
    )


# ============================================================================
# CDN Tracking Models
# ============================================================================

class CDNDelivery(Base):
    """
    CDN Delivery Tracking Model
    
    Tracks CDN uploads, cache status, and delivery metrics for assets.
    Used for CDN performance monitoring and cost optimization.
    
    Attributes:
        id (int): Unique delivery ID
        asset_id (int): Foreign key to asset
        cdn_provider (str): CDN provider name
        cdn_url (str): Full CDN URL
        upload_status (str): pending, uploaded, failed
        cache_status (str): cached, invalidated
        last_accessed (datetime): Last access time
        access_count (int): Number of times accessed
        bandwidth_bytes (int): Total bandwidth consumed
    """
    __tablename__ = 'cdn_deliveries'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    asset_id = Column(Integer, ForeignKey('assets.id'), nullable=False, index=True)
    
    # CDN details
    cdn_provider = Column(String(50), nullable=False)  # cloudflare, cloudfront, etc.
    cdn_url = Column(String(500), nullable=False)
    cdn_key = Column(String(500), nullable=True)  # CDN-specific key/path
    
    # Status tracking
    upload_status = Column(String(20), default='pending')  # pending, uploaded, failed
    cache_status = Column(String(20), default='cached')  # cached, invalidated
    
    # Performance metrics
    last_accessed = Column(DateTime, nullable=True)
    access_count = Column(Integer, default=0)
    bandwidth_bytes = Column(Integer, default=0)
    
    # Timestamps
    uploaded_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=func.now())
    
    __table_args__ = (
        Index('idx_cdn_asset', 'asset_id'),
        Index('idx_cdn_provider_status', 'cdn_provider', 'upload_status'),
    )

