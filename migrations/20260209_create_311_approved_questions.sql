-- Migration: Create Louisville 311 Approved Questions Corpus
-- Date: 2026-02-09
-- Purpose: Store validated Q&A pairs for Louisville Metro 311 customer service chat
-- Scope: B2C customer service - helping residents use 311 services
-- Schema: l311_ prefix to avoid conflicts with other projects

-- ============================================================================
-- APPROVED QUESTIONS TABLE
-- ============================================================================
CREATE TABLE IF NOT EXISTS l311_approved_questions (
    id SERIAL PRIMARY KEY,

    -- Question and answer text
    question_text TEXT NOT NULL,
    answer_text TEXT NOT NULL,

    -- Category taxonomy (aligned with 311 service types)
    category VARCHAR(100) NOT NULL,  -- Examples: "Waste Management", "Street Maintenance", "Code Enforcement"
    subcategory VARCHAR(100),        -- Examples: "Bulk Pickup", "Pothole Repair", "Property Violations"

    -- Service request metadata
    service_name VARCHAR(200),       -- Links to actual 311 service names from data
    typical_urgency VARCHAR(20),     -- low, medium, high (typical for this question type)
    typical_response_time VARCHAR(100), -- Example: "3-7 days", "24-48 hours"

    -- Question characteristics
    question_type VARCHAR(50) NOT NULL,  -- "how_to", "what_is", "timeline", "tracking", "eligibility", "general"
    keywords TEXT[],                     -- Search keywords for matching user questions
    common_variations TEXT[],            -- Alternative ways to ask this question

    -- Answer characteristics
    answer_level VARCHAR(50) DEFAULT 'general', -- "general", "detailed", "expert"
    includes_external_link BOOLEAN DEFAULT false,
    external_links TEXT[],               -- URLs to Louisville Metro resources

    -- Validation and approval
    is_approved BOOLEAN DEFAULT true,
    approved_by VARCHAR(100) DEFAULT 'System Admin',
    approved_at TIMESTAMP DEFAULT NOW(),
    validation_notes TEXT,

    -- Usage tracking
    times_shown INTEGER DEFAULT 0,
    times_helpful INTEGER DEFAULT 0,     -- From thumbs up
    times_not_helpful INTEGER DEFAULT 0, -- From thumbs down

    -- Metadata
    version INTEGER DEFAULT 1,
    source VARCHAR(100) DEFAULT 'Initial_Corpus', -- "Initial_Corpus", "Resident_Feedback", "SME_Review"
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),

    -- Ensure question uniqueness
    CONSTRAINT l311_unique_question UNIQUE(question_text)
);

-- ============================================================================
-- INDEXES
-- ============================================================================
CREATE INDEX IF NOT EXISTS idx_l311_approved_category
ON l311_approved_questions(category);

CREATE INDEX IF NOT EXISTS idx_l311_approved_service_name
ON l311_approved_questions(service_name);

CREATE INDEX IF NOT EXISTS idx_l311_approved_question_type
ON l311_approved_questions(question_type);

CREATE INDEX IF NOT EXISTS idx_l311_approved_is_approved
ON l311_approved_questions(is_approved)
WHERE is_approved = true;

-- Full-text search on questions
CREATE INDEX IF NOT EXISTS idx_l311_approved_question_fts
ON l311_approved_questions USING gin(to_tsvector('english', question_text));

-- Full-text search on answers
CREATE INDEX IF NOT EXISTS idx_l311_approved_answer_fts
ON l311_approved_questions USING gin(to_tsvector('english', answer_text));

-- GIN index for keyword arrays
CREATE INDEX IF NOT EXISTS idx_l311_approved_keywords
ON l311_approved_questions USING gin(keywords);

-- ============================================================================
-- ANSWER FEEDBACK TABLE
-- ============================================================================
CREATE TABLE IF NOT EXISTS l311_answer_feedback (
    feedback_id SERIAL PRIMARY KEY,

    -- Link to approved question
    approved_question_id INTEGER NOT NULL REFERENCES l311_approved_questions(id) ON DELETE CASCADE,

    -- Chat session info
    session_id VARCHAR(100),
    message_id VARCHAR(100),

    -- Feedback type
    feedback_type VARCHAR(20) NOT NULL, -- "positive", "negative"

    -- Optional detailed feedback
    user_comment TEXT,
    suggested_improvement TEXT,

    -- Metadata
    ip_address VARCHAR(45),  -- For tracking (IPv4/IPv6)
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Indexes for feedback
CREATE INDEX IF NOT EXISTS idx_l311_feedback_question
ON l311_answer_feedback(approved_question_id);

CREATE INDEX IF NOT EXISTS idx_l311_feedback_session
ON l311_answer_feedback(session_id);

CREATE INDEX IF NOT EXISTS idx_l311_feedback_type
ON l311_answer_feedback(feedback_type);

CREATE INDEX IF NOT EXISTS idx_l311_feedback_created
ON l311_answer_feedback(created_at);

-- ============================================================================
-- ANNOTATION USERS TABLE
-- ============================================================================
CREATE TABLE IF NOT EXISTS l311_annotation_users (
    user_id SERIAL PRIMARY KEY,

    -- User identity
    username VARCHAR(100) NOT NULL UNIQUE,
    full_name VARCHAR(200),
    email VARCHAR(200),

    -- Role
    role VARCHAR(50) DEFAULT 'annotator', -- "annotator", "admin", "sme"

    -- Access
    is_active BOOLEAN DEFAULT true,
    last_login TIMESTAMP,

    -- Metadata
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- ============================================================================
-- ANSWER ANNOTATIONS TABLE (for SME review)
-- ============================================================================
CREATE TABLE IF NOT EXISTS l311_answer_annotations (
    annotation_id SERIAL PRIMARY KEY,

    -- Links
    approved_question_id INTEGER NOT NULL REFERENCES l311_approved_questions(id) ON DELETE CASCADE,
    user_id INTEGER NOT NULL REFERENCES l311_annotation_users(user_id),

    -- Quality assessment
    is_accurate BOOLEAN NOT NULL,         -- Factually correct?
    is_helpful BOOLEAN NOT NULL,          -- Helpful for residents?
    is_complete BOOLEAN NOT NULL,         -- Contains all needed info?
    should_use BOOLEAN NOT NULL,          -- Ready for production?

    -- Answer quality rating
    clarity_rating INTEGER CHECK (clarity_rating BETWEEN 1 AND 5),   -- 1-5 scale
    usefulness_rating INTEGER CHECK (usefulness_rating BETWEEN 1 AND 5), -- 1-5 scale

    -- Optional feedback
    notes TEXT,
    suggested_improvement TEXT,
    suggested_answer_rewrite TEXT,

    -- Metadata
    annotation_status VARCHAR(50) DEFAULT 'submitted',  -- submitted, reviewed, approved
    time_spent_seconds INTEGER,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),

    -- One annotation per user per question
    CONSTRAINT l311_unique_user_annotation UNIQUE(approved_question_id, user_id)
);

-- Indexes for annotations
CREATE INDEX IF NOT EXISTS idx_l311_annotations_question
ON l311_answer_annotations(approved_question_id);

CREATE INDEX IF NOT EXISTS idx_l311_annotations_user
ON l311_answer_annotations(user_id);

CREATE INDEX IF NOT EXISTS idx_l311_annotations_status
ON l311_answer_annotations(annotation_status);

-- ============================================================================
-- UPDATED_AT TRIGGERS
-- ============================================================================

-- Trigger for approved_questions
CREATE OR REPLACE FUNCTION update_l311_approved_questions_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER l311_approved_questions_updated_at
    BEFORE UPDATE ON l311_approved_questions
    FOR EACH ROW
    EXECUTE FUNCTION update_l311_approved_questions_updated_at();

-- Trigger for annotation_users
CREATE OR REPLACE FUNCTION update_l311_annotation_users_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER l311_annotation_users_updated_at
    BEFORE UPDATE ON l311_annotation_users
    FOR EACH ROW
    EXECUTE FUNCTION update_l311_annotation_users_updated_at();

-- Trigger for answer_annotations
CREATE OR REPLACE FUNCTION update_l311_answer_annotations_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER l311_answer_annotations_updated_at
    BEFORE UPDATE ON l311_answer_annotations
    FOR EACH ROW
    EXECUTE FUNCTION update_l311_answer_annotations_updated_at();

-- ============================================================================
-- STATS VIEWS
-- ============================================================================

-- Question usage stats
CREATE OR REPLACE VIEW v_l311_question_stats AS
SELECT
    aq.id,
    aq.question_text,
    aq.category,
    aq.subcategory,
    aq.question_type,

    -- Usage metrics
    aq.times_shown,
    aq.times_helpful,
    aq.times_not_helpful,

    -- Calculate helpfulness rate
    CASE
        WHEN (aq.times_helpful + aq.times_not_helpful) > 0
        THEN ROUND(100.0 * aq.times_helpful / (aq.times_helpful + aq.times_not_helpful), 1)
        ELSE NULL
    END as helpfulness_pct,

    -- Annotation stats
    COUNT(DISTINCT aa.annotation_id) as annotation_count,
    AVG(CASE WHEN aa.is_accurate = true THEN 100.0 ELSE 0.0 END) as avg_accuracy,
    AVG(CASE WHEN aa.is_helpful = true THEN 100.0 ELSE 0.0 END) as avg_helpfulness,
    AVG(aa.clarity_rating) as avg_clarity_rating,
    AVG(aa.usefulness_rating) as avg_usefulness_rating

FROM l311_approved_questions aq
LEFT JOIN l311_answer_annotations aa ON aq.id = aa.approved_question_id
WHERE aq.is_approved = true
GROUP BY aq.id, aq.question_text, aq.category, aq.subcategory, aq.question_type,
         aq.times_shown, aq.times_helpful, aq.times_not_helpful;

-- Category quality stats
CREATE OR REPLACE VIEW v_l311_category_stats AS
SELECT
    category,
    COUNT(*) as total_questions,
    COUNT(CASE WHEN is_approved = true THEN 1 END) as approved_questions,
    SUM(times_shown) as total_shown,
    SUM(times_helpful) as total_helpful,
    SUM(times_not_helpful) as total_not_helpful,

    -- Average helpfulness per category
    CASE
        WHEN SUM(times_helpful + times_not_helpful) > 0
        THEN ROUND(100.0 * SUM(times_helpful) / SUM(times_helpful + times_not_helpful), 1)
        ELSE NULL
    END as category_helpfulness_pct

FROM l311_approved_questions
GROUP BY category
ORDER BY category_helpfulness_pct DESC NULLS LAST;

-- User annotation progress
CREATE OR REPLACE VIEW v_l311_user_annotation_progress AS
SELECT
    u.user_id,
    u.username,
    u.full_name,
    u.role,

    COUNT(DISTINCT aa.annotation_id) as total_annotations,
    SUM(aa.time_spent_seconds) as total_time_seconds,

    -- Quality metrics
    COUNT(CASE WHEN aa.is_accurate = true THEN 1 END) as marked_accurate,
    COUNT(CASE WHEN aa.is_helpful = true THEN 1 END) as marked_helpful,
    COUNT(CASE WHEN aa.should_use = true THEN 1 END) as marked_should_use,

    -- Average ratings
    ROUND(AVG(aa.clarity_rating), 1) as avg_clarity_rating,
    ROUND(AVG(aa.usefulness_rating), 1) as avg_usefulness_rating,

    MAX(aa.updated_at) as last_annotation_date

FROM l311_annotation_users u
LEFT JOIN l311_answer_annotations aa ON u.user_id = aa.user_id
GROUP BY u.user_id, u.username, u.full_name, u.role;

-- ============================================================================
-- INITIAL DATA VERIFICATION
-- ============================================================================
DO $$
DECLARE
    question_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO question_count FROM l311_approved_questions WHERE is_approved = true;
    RAISE NOTICE 'Total approved questions in Louisville 311 corpus: %', question_count;
END $$;

-- ============================================================================
-- SAMPLE QUERIES (for reference)
-- ============================================================================
-- Query: Find questions by category
-- SELECT question_text, answer_text FROM l311_approved_questions WHERE category = 'Waste Management' AND is_approved = true;

-- Query: Search questions by keywords
-- SELECT question_text, answer_text FROM l311_approved_questions WHERE 'pothole' = ANY(keywords) AND is_approved = true;

-- Query: Get question stats
-- SELECT * FROM v_l311_question_stats ORDER BY helpfulness_pct DESC LIMIT 10;

-- Query: Category performance
-- SELECT * FROM v_l311_category_stats;

-- Query: Recent feedback
-- SELECT aq.question_text, af.feedback_type, af.user_comment
-- FROM l311_answer_feedback af
-- JOIN l311_approved_questions aq ON af.approved_question_id = aq.id
-- ORDER BY af.created_at DESC LIMIT 20;
