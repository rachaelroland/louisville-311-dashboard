-- ============================================================================
-- MULTI-CITY 311 AI ASSISTANT - DATABASE SCHEMA
-- White-Label Multi-Tenant Architecture
-- ============================================================================

-- ============================================================================
-- CITIES TABLE
-- ============================================================================

CREATE TABLE cities (
    id SERIAL PRIMARY KEY,

    -- Basic Information
    slug TEXT UNIQUE NOT NULL,              -- 'louisville', 'lexington', etc. (used in URLs)
    name TEXT NOT NULL,                     -- 'Louisville Metro Government'
    display_name TEXT,                      -- 'Louisville Metro 311' (for branding)
    state TEXT NOT NULL,                    -- 'KY'
    population INTEGER,

    -- Contact & Service Info
    phone_311 TEXT,                         -- '(502) 574-5000'
    website_311 TEXT,                       -- 'https://louisvilleky.gov/311'
    hours_of_operation TEXT,                -- 'Mon-Fri 8am-5pm EST'
    timezone TEXT DEFAULT 'America/New_York',

    -- Branding Configuration
    branding_config JSONB DEFAULT '{
        "primary_color": "#0066CC",
        "secondary_color": "#FFB81C",
        "logo_url": "",
        "favicon_url": "",
        "custom_css": "",
        "chat_greeting": "Welcome! How can we help you today?",
        "footer_text": "Powered by AI",
        "show_powered_by": true
    }'::jsonb,

    -- Subscription & Billing
    subscription_tier TEXT DEFAULT 'starter',  -- 'starter', 'professional', 'enterprise'
    monthly_price_cents INTEGER,               -- Price in cents
    monthly_question_quota INTEGER,            -- Max questions per month (NULL = unlimited)
    is_trial BOOLEAN DEFAULT false,
    trial_ends_at TIMESTAMP,

    -- Status
    is_active BOOLEAN DEFAULT true,
    onboarding_status TEXT DEFAULT 'pending', -- 'pending', 'in_progress', 'completed', 'live'

    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    activated_at TIMESTAMP,

    -- Contact Info (for account management)
    primary_contact_name TEXT,
    primary_contact_email TEXT,
    primary_contact_phone TEXT,

    -- Technical Settings
    subdomain TEXT UNIQUE,                     -- 'louisville' for louisville.311ai.com
    custom_domain TEXT,                        -- Optional: 'ask.louisvilleky.gov'
    api_key TEXT UNIQUE,                       -- For API access

    -- Feature Flags
    features JSONB DEFAULT '{
        "spanish_support": false,
        "sms_channel": false,
        "voice_ivr": false,
        "api_access": false,
        "custom_integrations": false,
        "white_label_mobile_app": false,
        "advanced_analytics": false
    }'::jsonb
);

-- Indexes
CREATE INDEX idx_cities_slug ON cities(slug);
CREATE INDEX idx_cities_subdomain ON cities(subdomain);
CREATE INDEX idx_cities_active ON cities(is_active);
CREATE INDEX idx_cities_tier ON cities(subscription_tier);

-- Auto-update updated_at timestamp
CREATE OR REPLACE FUNCTION update_cities_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER cities_updated_at_trigger
    BEFORE UPDATE ON cities
    FOR EACH ROW
    EXECUTE FUNCTION update_cities_updated_at();

-- ============================================================================
-- UPDATE EXISTING APPROVED QUESTIONS TABLE
-- ============================================================================

-- Add city_id column to existing table
ALTER TABLE l311_approved_questions
ADD COLUMN IF NOT EXISTS city_id INTEGER REFERENCES cities(id) ON DELETE CASCADE;

-- Add index for city-based queries
CREATE INDEX IF NOT EXISTS idx_approved_questions_city
ON l311_approved_questions(city_id);

-- Add composite index for common query pattern
CREATE INDEX IF NOT EXISTS idx_approved_questions_city_approved
ON l311_approved_questions(city_id, is_approved)
WHERE is_approved = true;

-- ============================================================================
-- CITY ANALYTICS TABLE
-- ============================================================================

CREATE TABLE city_analytics_daily (
    id SERIAL PRIMARY KEY,
    city_id INTEGER REFERENCES cities(id) ON DELETE CASCADE,
    date DATE NOT NULL,

    -- Usage Metrics
    total_questions INTEGER DEFAULT 0,
    approved_answers_used INTEGER DEFAULT 0,
    claude_fallback_used INTEGER DEFAULT 0,
    unique_users INTEGER DEFAULT 0,

    -- Performance Metrics
    avg_response_time_ms INTEGER,
    p95_response_time_ms INTEGER,

    -- Satisfaction Metrics
    thumbs_up INTEGER DEFAULT 0,
    thumbs_down INTEGER DEFAULT 0,
    satisfaction_rate DECIMAL(5,2), -- Calculated: thumbs_up / (thumbs_up + thumbs_down)

    -- Coverage Metrics
    total_approved_questions INTEGER,
    questions_with_usage INTEGER,
    coverage_rate DECIMAL(5,2), -- Calculated: questions_with_usage / total_approved_questions

    -- Created timestamp
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- Unique constraint (one row per city per day)
    UNIQUE(city_id, date)
);

CREATE INDEX idx_analytics_city_date ON city_analytics_daily(city_id, date DESC);

-- ============================================================================
-- CITY USERS TABLE (for SME access control)
-- ============================================================================

CREATE TABLE city_users (
    id SERIAL PRIMARY KEY,
    city_id INTEGER REFERENCES cities(id) ON DELETE CASCADE,

    -- User Info
    email TEXT NOT NULL,
    full_name TEXT,
    role TEXT DEFAULT 'viewer', -- 'admin', 'editor', 'viewer'

    -- Authentication
    hashed_password TEXT,
    password_reset_token TEXT,
    password_reset_expires_at TIMESTAMP,

    -- Status
    is_active BOOLEAN DEFAULT true,
    last_login_at TIMESTAMP,

    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- Unique email per city (user can have multiple cities)
    UNIQUE(city_id, email)
);

CREATE INDEX idx_city_users_city ON city_users(city_id);
CREATE INDEX idx_city_users_email ON city_users(email);

-- ============================================================================
-- QUESTION EDIT HISTORY (audit trail)
-- ============================================================================

CREATE TABLE question_edit_history (
    id SERIAL PRIMARY KEY,
    question_id INTEGER REFERENCES l311_approved_questions(id) ON DELETE CASCADE,
    city_id INTEGER REFERENCES cities(id) ON DELETE CASCADE,
    edited_by INTEGER REFERENCES city_users(id),

    -- What changed
    field_name TEXT NOT NULL, -- 'question_text', 'answer_text', 'keywords', etc.
    old_value TEXT,
    new_value TEXT,

    -- When
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_edit_history_question ON question_edit_history(question_id);
CREATE INDEX idx_edit_history_city ON question_edit_history(city_id);

-- ============================================================================
-- USAGE EVENTS (detailed event tracking)
-- ============================================================================

CREATE TABLE usage_events (
    id SERIAL PRIMARY KEY,
    city_id INTEGER REFERENCES cities(id) ON DELETE CASCADE,

    -- Event Details
    event_type TEXT NOT NULL, -- 'question_asked', 'answer_shown', 'feedback_given', 'fallback_used'
    user_question TEXT,
    matched_question_id INTEGER REFERENCES l311_approved_questions(id) ON DELETE SET NULL,

    -- Context
    session_id TEXT,
    user_ip TEXT,
    user_agent TEXT,

    -- Performance
    response_time_ms INTEGER,
    search_method TEXT, -- 'standard', 'enhanced', 'fallback'

    -- Feedback
    feedback TEXT, -- 'positive', 'negative', NULL

    -- Timestamp
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_usage_events_city ON usage_events(city_id);
CREATE INDEX idx_usage_events_created ON usage_events(created_at DESC);
CREATE INDEX idx_usage_events_city_date ON usage_events(city_id, created_at DESC);

-- Partition by month for performance (optional, for high-volume)
-- CREATE TABLE usage_events_2026_02 PARTITION OF usage_events
--     FOR VALUES FROM ('2026-02-01') TO ('2026-03-01');

-- ============================================================================
-- ONBOARDING CHECKLIST TABLE
-- ============================================================================

CREATE TABLE city_onboarding_tasks (
    id SERIAL PRIMARY KEY,
    city_id INTEGER REFERENCES cities(id) ON DELETE CASCADE,

    -- Task Info
    task_name TEXT NOT NULL,
    task_description TEXT,
    task_order INTEGER,

    -- Status
    is_completed BOOLEAN DEFAULT false,
    completed_at TIMESTAMP,
    completed_by INTEGER REFERENCES city_users(id),

    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_onboarding_city ON city_onboarding_tasks(city_id);

-- ============================================================================
-- BILLING EVENTS TABLE
-- ============================================================================

CREATE TABLE billing_events (
    id SERIAL PRIMARY KEY,
    city_id INTEGER REFERENCES cities(id) ON DELETE CASCADE,

    -- Event Details
    event_type TEXT NOT NULL, -- 'invoice_created', 'payment_received', 'payment_failed', 'subscription_changed'
    amount_cents INTEGER,
    currency TEXT DEFAULT 'USD',

    -- Stripe/Payment Integration
    stripe_invoice_id TEXT,
    stripe_payment_intent_id TEXT,
    stripe_subscription_id TEXT,

    -- Status
    status TEXT, -- 'pending', 'paid', 'failed', 'refunded'

    -- Metadata
    metadata JSONB,

    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_billing_city ON billing_events(city_id);
CREATE INDEX idx_billing_created ON billing_events(created_at DESC);

-- ============================================================================
-- INITIAL DATA - LOUISVILLE AS FIRST CITY
-- ============================================================================

INSERT INTO cities (
    slug,
    name,
    display_name,
    state,
    population,
    phone_311,
    website_311,
    hours_of_operation,
    timezone,
    branding_config,
    subscription_tier,
    monthly_price_cents,
    is_active,
    onboarding_status,
    activated_at,
    subdomain
) VALUES (
    'louisville',
    'Louisville Metro Government',
    'Louisville Metro 311',
    'KY',
    617000,
    '(502) 574-5000',
    'https://louisvilleky.gov/311',
    'Monday-Friday 8:00 AM - 5:00 PM EST',
    'America/New_York',
    '{
        "primary_color": "#00539B",
        "secondary_color": "#FFB81C",
        "logo_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/86/Seal_of_Louisville%2C_Kentucky.svg/240px-Seal_of_Louisville%2C_Kentucky.svg.png",
        "chat_greeting": "Welcome to Louisville Metro 311! How can I help you today?",
        "footer_text": "Louisville Metro Government",
        "show_powered_by": false
    }',
    'professional',
    500000, -- $5,000/month
    true,
    'live',
    CURRENT_TIMESTAMP,
    'louisville'
);

-- Link existing questions to Louisville
UPDATE l311_approved_questions
SET city_id = (SELECT id FROM cities WHERE slug = 'louisville')
WHERE city_id IS NULL;

-- ============================================================================
-- HELPER FUNCTIONS
-- ============================================================================

-- Function to calculate daily analytics
CREATE OR REPLACE FUNCTION calculate_daily_analytics(target_city_id INTEGER, target_date DATE)
RETURNS void AS $$
DECLARE
    total_qs INTEGER;
    approved_qs INTEGER;
    fallback_qs INTEGER;
    unique_users_count INTEGER;
    thumbs_up_count INTEGER;
    thumbs_down_count INTEGER;
    satisfaction DECIMAL(5,2);
BEGIN
    -- Count questions
    SELECT COUNT(*) INTO total_qs
    FROM usage_events
    WHERE city_id = target_city_id
    AND DATE(created_at) = target_date
    AND event_type = 'question_asked';

    -- Count approved answers used
    SELECT COUNT(*) INTO approved_qs
    FROM usage_events
    WHERE city_id = target_city_id
    AND DATE(created_at) = target_date
    AND event_type = 'answer_shown'
    AND matched_question_id IS NOT NULL;

    -- Count fallbacks
    SELECT COUNT(*) INTO fallback_qs
    FROM usage_events
    WHERE city_id = target_city_id
    AND DATE(created_at) = target_date
    AND event_type = 'fallback_used';

    -- Count unique users (by session_id)
    SELECT COUNT(DISTINCT session_id) INTO unique_users_count
    FROM usage_events
    WHERE city_id = target_city_id
    AND DATE(created_at) = target_date;

    -- Count feedback
    SELECT
        SUM(CASE WHEN feedback = 'positive' THEN 1 ELSE 0 END),
        SUM(CASE WHEN feedback = 'negative' THEN 1 ELSE 0 END)
    INTO thumbs_up_count, thumbs_down_count
    FROM usage_events
    WHERE city_id = target_city_id
    AND DATE(created_at) = target_date
    AND feedback IS NOT NULL;

    -- Calculate satisfaction rate
    IF (thumbs_up_count + thumbs_down_count) > 0 THEN
        satisfaction := (thumbs_up_count::DECIMAL / (thumbs_up_count + thumbs_down_count)) * 100;
    ELSE
        satisfaction := NULL;
    END IF;

    -- Insert or update analytics record
    INSERT INTO city_analytics_daily (
        city_id,
        date,
        total_questions,
        approved_answers_used,
        claude_fallback_used,
        unique_users,
        thumbs_up,
        thumbs_down,
        satisfaction_rate
    ) VALUES (
        target_city_id,
        target_date,
        total_qs,
        approved_qs,
        fallback_qs,
        unique_users_count,
        thumbs_up_count,
        thumbs_down_count,
        satisfaction
    )
    ON CONFLICT (city_id, date)
    DO UPDATE SET
        total_questions = EXCLUDED.total_questions,
        approved_answers_used = EXCLUDED.approved_answers_used,
        claude_fallback_used = EXCLUDED.claude_fallback_used,
        unique_users = EXCLUDED.unique_users,
        thumbs_up = EXCLUDED.thumbs_up,
        thumbs_down = EXCLUDED.thumbs_down,
        satisfaction_rate = EXCLUDED.satisfaction_rate;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- VIEWS FOR COMMON QUERIES
-- ============================================================================

-- Active cities overview
CREATE OR REPLACE VIEW v_active_cities AS
SELECT
    c.id,
    c.slug,
    c.name,
    c.state,
    c.subscription_tier,
    c.monthly_price_cents / 100.0 AS monthly_price_dollars,
    c.is_active,
    c.activated_at,
    COUNT(DISTINCT q.id) AS total_questions,
    COUNT(DISTINCT u.id) AS total_users
FROM cities c
LEFT JOIN l311_approved_questions q ON q.city_id = c.id AND q.is_approved = true
LEFT JOIN city_users u ON u.city_id = c.id AND u.is_active = true
WHERE c.is_active = true
GROUP BY c.id
ORDER BY c.created_at DESC;

-- Monthly revenue view
CREATE OR REPLACE VIEW v_monthly_revenue AS
SELECT
    DATE_TRUNC('month', created_at) AS month,
    COUNT(*) AS active_cities,
    SUM(monthly_price_cents) / 100.0 AS mrr_dollars,
    SUM(monthly_price_cents) * 12 / 100.0 AS arr_dollars
FROM cities
WHERE is_active = true
GROUP BY DATE_TRUNC('month', created_at)
ORDER BY month DESC;

-- City health scorecard
CREATE OR REPLACE VIEW v_city_health AS
SELECT
    c.slug,
    c.name,
    a.date,
    a.total_questions,
    a.approved_answers_used,
    a.satisfaction_rate,
    CASE
        WHEN a.satisfaction_rate >= 80 AND a.approved_answers_used::DECIMAL / NULLIF(a.total_questions, 0) >= 0.8 THEN 'healthy'
        WHEN a.satisfaction_rate >= 70 AND a.approved_answers_used::DECIMAL / NULLIF(a.total_questions, 0) >= 0.6 THEN 'warning'
        ELSE 'critical'
    END AS health_status
FROM cities c
LEFT JOIN city_analytics_daily a ON a.city_id = c.id
WHERE c.is_active = true
ORDER BY a.date DESC, c.name;

-- ============================================================================
-- SAMPLE QUERIES
-- ============================================================================

-- Get all cities with their question counts
-- SELECT * FROM v_active_cities;

-- Calculate analytics for yesterday
-- SELECT calculate_daily_analytics(
--     (SELECT id FROM cities WHERE slug = 'louisville'),
--     CURRENT_DATE - INTERVAL '1 day'
-- );

-- Get monthly revenue
-- SELECT * FROM v_monthly_revenue;

-- Check city health
-- SELECT * FROM v_city_health WHERE date >= CURRENT_DATE - INTERVAL '7 days';

-- ============================================================================
-- MIGRATION COMPLETE
-- ============================================================================

-- Summary of changes:
-- ✅ Created cities table for multi-tenant support
-- ✅ Added city_id to l311_approved_questions
-- ✅ Created analytics tracking tables
-- ✅ Created user management tables
-- ✅ Created audit trail tables
-- ✅ Created helper functions
-- ✅ Created useful views
-- ✅ Migrated Louisville as first city

-- Next steps:
-- 1. Update dashboard_app.py to support city routing
-- 2. Build admin interface for city management
-- 3. Implement usage event tracking
-- 4. Set up automated analytics calculation (cron job)
