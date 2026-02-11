# Louisville 311 Database Migrations

Database schema and initial data for the Louisville Metro 311 dashboard approved questions corpus.

## Overview

These migrations create a knowledge base of validated Q&A pairs for the B2C customer service chat agent. The system helps Louisville residents get accurate answers about 311 services.

## Schema Prefix

All tables use the `l311_` prefix to avoid conflicts with other projects (e.g., Zendesk uses different tables).

## Migration Files

### 1. `20260209_create_311_approved_questions.sql`
**Purpose:** Create database schema for approved questions corpus

**Tables Created:**
- `l311_approved_questions` - Core Q&A corpus with metadata
- `l311_answer_feedback` - Resident feedback (thumbs up/down from chat)
- `l311_annotation_users` - SME user management for quality review
- `l311_answer_annotations` - SME annotations for answer quality

**Views Created:**
- `v_l311_question_stats` - Usage and helpfulness metrics per question
- `v_l311_category_stats` - Performance metrics by category
- `v_l311_user_annotation_progress` - SME annotation progress tracking

**Features:**
- Full-text search on questions and answers
- Keyword array matching for question variations
- Automatic updated_at timestamps
- Usage tracking (times shown, helpful, not helpful)
- Version control for answers

### 2. `20260209_load_initial_311_questions.sql`
**Purpose:** Load initial corpus of 25+ validated Q&A pairs

**Categories:**
1. General (5 questions) - About 311, submitting, tracking, timelines
2. Waste Management (5 questions) - Trash, recycling, bulk pickup
3. Street Maintenance (4 questions) - Potholes, lights, sidewalks, signs
4. Code Enforcement (3 questions) - Violations, abandoned vehicles
5. Parks (2 questions) - Park issues, trees
6. Animal Control (2 questions) - Stray animals, noise
7. Water/Sewer (2 questions) - Water main breaks, sewer backups

**Each Question Includes:**
- Question text and answer text
- Category and subcategory
- Question type (how_to, what_is, timeline, etc.)
- Keywords for matching
- Common question variations
- Typical urgency and response time
- Link to 311 service name (when applicable)

## Running Migrations

### Option 1: PostgreSQL (Recommended for Production)

```bash
# Create database
createdb louisville_311

# Run schema migration
psql louisville_311 < migrations/20260209_create_311_approved_questions.sql

# Load initial questions
psql louisville_311 < migrations/20260209_load_initial_311_questions.sql

# Verify
psql louisville_311 -c "SELECT COUNT(*) FROM l311_approved_questions;"
psql louisville_311 -c "SELECT category, COUNT(*) FROM l311_approved_questions GROUP BY category;"
```

### Option 2: Supabase (Cloud PostgreSQL)

1. Create new Supabase project at https://supabase.com
2. Get database URL from project settings
3. Run migrations:

```bash
# Set connection string
export DATABASE_URL="postgresql://[user]:[password]@[host]:5432/postgres"

# Run schema
psql $DATABASE_URL < migrations/20260209_create_311_approved_questions.sql

# Load questions
psql $DATABASE_URL < migrations/20260209_load_initial_311_questions.sql

# Verify
psql $DATABASE_URL -c "SELECT COUNT(*) FROM l311_approved_questions;"
```

### Option 3: SQLite (Development Only)

SQLite doesn't support all PostgreSQL features (arrays, full-text search). For development only:

```bash
# Note: Some features won't work in SQLite
sqlite3 louisville_311.db < migrations/20260209_create_311_approved_questions.sql
# You'll need to modify the SQL for SQLite compatibility
```

## Verification Queries

After running migrations:

```sql
-- Check total questions loaded
SELECT COUNT(*) FROM l311_approved_questions;
-- Expected: 25+

-- Questions by category
SELECT category, COUNT(*) as count
FROM l311_approved_questions
GROUP BY category
ORDER BY count DESC;

-- Sample questions
SELECT question_text, category, question_type
FROM l311_approved_questions
LIMIT 5;

-- Check question types distribution
SELECT question_type, COUNT(*) as count
FROM l311_approved_questions
GROUP BY question_type
ORDER BY count DESC;

-- Verify full-text search index
SELECT question_text
FROM l311_approved_questions
WHERE to_tsvector('english', question_text) @@ to_tsquery('english', 'pothole');
-- Should return pothole-related questions

-- Verify keyword search
SELECT question_text
FROM l311_approved_questions
WHERE 'trash' = ANY(keywords);
-- Should return waste management questions
```

## Adding New Questions

To add new approved questions:

```sql
INSERT INTO l311_approved_questions (
    question_text,
    answer_text,
    category,
    subcategory,
    question_type,
    keywords,
    common_variations,
    typical_urgency,
    service_name
) VALUES (
    'Your question here?',
    'Your detailed answer here.',
    'Category Name',
    'Subcategory',
    'how_to',  -- or what_is, timeline, tracking, eligibility
    ARRAY['keyword1', 'keyword2'],
    ARRAY['Alternative question 1?', 'Alternative question 2?'],
    'medium',
    'Service Name from 311 Data'
);
```

## Integration with Chat Agent

The chat agent can use this corpus to:

1. **Exact Match**: Find identical or very similar questions
2. **Keyword Search**: Match based on keywords array
3. **Full-Text Search**: Find questions containing specific terms
4. **Category Filtering**: Show questions by category/service type

Example integration code:

```python
import psycopg2

# Search for matching questions
def find_matching_question(user_question: str, conn):
    cur = conn.cursor()

    # Try full-text search
    cur.execute("""
        SELECT question_text, answer_text, category
        FROM l311_approved_questions
        WHERE to_tsvector('english', question_text) @@ plainto_tsquery('english', %s)
        AND is_approved = true
        ORDER BY ts_rank(to_tsvector('english', question_text), plainto_tsquery('english', %s)) DESC
        LIMIT 3
    """, (user_question, user_question))

    return cur.fetchall()
```

## Tracking Usage

The system automatically tracks:
- How many times each question is shown
- Thumbs up/down feedback from residents
- Helpfulness percentage

View stats:

```sql
-- Top performing questions
SELECT question_text, times_shown, helpfulness_pct
FROM v_l311_question_stats
WHERE times_shown > 0
ORDER BY helpfulness_pct DESC
LIMIT 10;

-- Category performance
SELECT * FROM v_l311_category_stats
ORDER BY category_helpfulness_pct DESC;
```

## SME Annotation Workflow

For quality review by subject matter experts:

1. Create annotation users:
```sql
INSERT INTO l311_annotation_users (username, full_name, email, role)
VALUES ('john.doe', 'John Doe', 'john@louisvilleky.gov', 'sme');
```

2. SMEs review and annotate answers:
```sql
INSERT INTO l311_answer_annotations (
    approved_question_id,
    user_id,
    is_accurate,
    is_helpful,
    is_complete,
    should_use,
    clarity_rating,
    usefulness_rating,
    notes
) VALUES (
    1,  -- question ID
    1,  -- user ID
    true,  -- accurate
    true,  -- helpful
    true,  -- complete
    true,  -- should use
    5,  -- clarity 1-5
    5,  -- usefulness 1-5
    'Excellent answer, very clear'
);
```

3. View annotation progress:
```sql
SELECT * FROM v_l311_user_annotation_progress;
```

## Next Steps

1. ✅ Schema created
2. ✅ Initial 25 questions loaded
3. [ ] Deploy database to production
4. [ ] Integrate with chat agent
5. [ ] Track usage and feedback
6. [ ] Build SME annotation interface
7. [ ] Expand corpus based on actual resident questions

## Notes

- All tables use `l311_` prefix to avoid conflicts
- Schema supports versioning for answer updates
- Full-text search requires PostgreSQL (not SQLite)
- Array fields require PostgreSQL
- Triggers auto-update `updated_at` timestamps
- Foreign keys ensure referential integrity

## Questions?

See main documentation in `docs/CLAUDE.md` for complete project context.
