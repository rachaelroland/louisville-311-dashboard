# Louisville 311 Approved Questions Corpus

## Overview

Following the Zendesk project pattern, we've created a database-backed corpus of approved Q&A pairs for the Louisville Metro 311 customer service chat agent.

**Status:** ✅ Schema created, 25+ initial questions loaded, ready for database deployment

**Purpose:** Provide validated, high-quality answers to common resident questions about Louisville Metro 311 services

**Based on:** Zendesk project `approved_questions` schema and annotation framework

---

## Database Schema

### Table Prefix: `l311_`

All tables use the `l311_` prefix to avoid conflicts with other projects (Zendesk uses different tables in the same database).

### Tables Created

#### 1. `l311_approved_questions` (Core Q&A Corpus)
Stores validated question-answer pairs that the chat agent can reference.

**Key Fields:**
- `question_text` - The question as residents ask it
- `answer_text` - The validated answer
- `category` - Main category (Waste Management, Street Maintenance, etc.)
- `subcategory` - Specific service area
- `question_type` - Type: how_to, what_is, timeline, tracking, eligibility, general
- `keywords` - Array of keywords for matching
- `common_variations` - Array of alternative ways to ask the same question
- `service_name` - Links to actual 311 service names from data
- `typical_urgency` - Expected urgency level (low, medium, high)
- `typical_response_time` - Expected time to resolution
- `times_shown` - Usage tracking
- `times_helpful` / `times_not_helpful` - Feedback from thumbs up/down

#### 2. `l311_answer_feedback` (Resident Feedback)
Tracks thumbs up/down feedback from residents in the chat interface.

**Key Fields:**
- `approved_question_id` - Links to question
- `session_id` - Chat session ID
- `message_id` - Specific message ID
- `feedback_type` - "positive" or "negative"
- `user_comment` - Optional detailed feedback
- `suggested_improvement` - How to improve the answer

#### 3. `l311_annotation_users` (SME User Management)
Manages users who can annotate and validate answers.

**Key Fields:**
- `username` - Login username
- `full_name` - Full name
- `email` - Email address
- `role` - "annotator", "admin", or "sme"
- `is_active` - Account status

#### 4. `l311_answer_annotations` (Quality Review)
SME annotations for answer quality validation.

**Key Fields:**
- `approved_question_id` - Question being reviewed
- `user_id` - Reviewer
- `is_accurate` - Factually correct?
- `is_helpful` - Helpful for residents?
- `is_complete` - Contains all needed info?
- `should_use` - Ready for production?
- `clarity_rating` - 1-5 scale
- `usefulness_rating` - 1-5 scale
- `notes` - Review notes
- `suggested_improvement` - Improvement suggestions

### Views Created

#### 1. `v_l311_question_stats`
Per-question usage and quality metrics:
- Times shown, helpful, not helpful
- Helpfulness percentage
- Average annotation ratings
- Accuracy and clarity scores

#### 2. `v_l311_category_stats`
Category-level performance:
- Questions per category
- Total usage metrics
- Average helpfulness by category

#### 3. `v_l311_user_annotation_progress`
SME annotation progress tracking:
- Annotations completed per user
- Time spent annotating
- Quality metrics
- Last annotation date

---

## Initial Question Corpus (25 Questions)

### General (5 Questions)
1. What is 311?
2. How do I submit a 311 service request?
3. What's the difference between 311 and 911?
4. How do I track the status of my 311 request?
5. How long does it take to fix my issue?

### Waste Management (5 Questions)
1. How do I request bulk trash pickup?
2. When is my regular trash pickup day?
3. My trash wasn't picked up. What should I do?
4. What can I recycle?
5. How do I dispose of yard waste?

### Street Maintenance (4 Questions)
1. How do I report a pothole?
2. How do I report a streetlight that's out?
3. How do I report damaged sidewalk?
4. How do I report a missing or damaged street sign?

### Code Enforcement (3 Questions)
1. How do I report a property code violation?
2. How do I report an abandoned vehicle?
3. How do I report overgrown grass or weeds?

### Parks (2 Questions)
1. How do I report a problem at a park?
2. How do I report a tree problem?

### Animal Control (2 Questions)
1. How do I report a stray animal?
2. How do I report a barking dog complaint?

### Water/Sewer (2 Questions)
1. How do I report a water main break?
2. How do I report a sewer backup?

---

## Question Structure

Each question includes:

```json
{
  "question_text": "How do I submit a 311 service request?",
  "answer_text": "There are three easy ways to submit a 311 request: 1) Call 311...",
  "category": "General",
  "subcategory": "Submitting Requests",
  "question_type": "how_to",
  "keywords": ["submit", "report", "request", "how"],
  "common_variations": [
    "How can I report an issue?",
    "How do I file a 311 request?",
    "How to submit a service request?"
  ],
  "typical_urgency": "low",
  "typical_response_time": "Immediate (information only)",
  "service_name": null
}
```

---

## Question Types Taxonomy

1. **how_to** - How to do something (submit, report, track)
2. **what_is** - What something is or what's available
3. **timeline** - How long something takes
4. **tracking** - Checking status or following up
5. **eligibility** - Who qualifies or what's allowed
6. **general** - General information

---

## Migration Files

### 1. `migrations/20260209_create_311_approved_questions.sql`
- Creates 4 tables with full schema
- Creates 3 views for statistics
- Creates triggers for auto-updating timestamps
- Creates indexes for performance (full-text search, keywords, categories)
- Total: ~350 lines of SQL

### 2. `migrations/20260209_load_initial_311_questions.sql`
- Loads 25 initial Q&A pairs
- Organized by category
- Includes all metadata (keywords, variations, response times)
- Verification queries at end
- Total: ~380 lines of SQL

### 3. `migrations/README.md`
- Complete migration guide
- Instructions for PostgreSQL, Supabase, SQLite
- Verification queries
- Integration examples
- Usage tracking examples
- Total: ~300 lines of documentation

---

## Deployment Options

### Option 1: Supabase (Recommended for Production)
- Cloud PostgreSQL database
- Free tier available
- Built-in auth and API
- Dashboard for querying

```bash
# Get connection string from Supabase project settings
export DATABASE_URL="postgresql://[user]:[password]@[host]:5432/postgres"

# Run migrations
psql $DATABASE_URL < migrations/20260209_create_311_approved_questions.sql
psql $DATABASE_URL < migrations/20260209_load_initial_311_questions.sql
```

### Option 2: Local PostgreSQL
- Full control
- No cloud dependencies
- Good for development

```bash
createdb louisville_311
psql louisville_311 < migrations/20260209_create_311_approved_questions.sql
psql louisville_311 < migrations/20260209_load_initial_311_questions.sql
```

### Option 3: Render PostgreSQL
- Hosted PostgreSQL
- Integrates with Render deployment
- Pay-as-you-go pricing

---

## Integration with Chat Agent

### Current State
The chat agent currently uses OpenRouter/Claude with a system prompt. No database integration yet.

### Proposed Integration

#### Phase 1: Question Matching
```python
def find_matching_questions(user_question: str, conn):
    """Find approved questions matching user input"""
    cur = conn.cursor()

    # Full-text search
    cur.execute("""
        SELECT id, question_text, answer_text, category
        FROM l311_approved_questions
        WHERE to_tsvector('english', question_text)
              @@ plainto_tsquery('english', %s)
        AND is_approved = true
        ORDER BY ts_rank(
            to_tsvector('english', question_text),
            plainto_tsquery('english', %s)
        ) DESC
        LIMIT 3
    """, (user_question, user_question))

    return cur.fetchall()
```

#### Phase 2: Answer Injection
Inject matched answers into the system prompt or use them to augment Claude's response.

#### Phase 3: Feedback Collection
Track when questions are shown and collect thumbs up/down feedback:

```python
def track_question_usage(question_id: int, conn):
    """Increment times_shown counter"""
    cur = conn.cursor()
    cur.execute("""
        UPDATE l311_approved_questions
        SET times_shown = times_shown + 1
        WHERE id = %s
    """, (question_id,))
    conn.commit()

def record_feedback(question_id: int, session_id: str,
                   feedback_type: str, conn):
    """Record thumbs up/down feedback"""
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO l311_answer_feedback
        (approved_question_id, session_id, feedback_type)
        VALUES (%s, %s, %s)
    """, (question_id, session_id, feedback_type))

    # Update helpfulness counters
    if feedback_type == 'positive':
        cur.execute("""
            UPDATE l311_approved_questions
            SET times_helpful = times_helpful + 1
            WHERE id = %s
        """, (question_id,))
    else:
        cur.execute("""
            UPDATE l311_approved_questions
            SET times_not_helpful = times_not_helpful + 1
            WHERE id = %s
        """, (question_id,))

    conn.commit()
```

#### Phase 4: Stats Dashboard
Add a new tab to the dashboard showing:
- Most helpful questions
- Questions needing improvement (low helpfulness %)
- Category performance
- Recent feedback

---

## Usage Statistics

### Tracking Metrics

Per Question:
- Times shown to residents
- Times marked helpful (👍)
- Times marked not helpful (👎)
- Helpfulness percentage
- Category and service type

Per Category:
- Total questions
- Total usage
- Average helpfulness
- Questions needing review

### Sample Queries

```sql
-- Top 10 most helpful questions
SELECT question_text, times_shown, helpfulness_pct
FROM v_l311_question_stats
WHERE times_shown > 10
ORDER BY helpfulness_pct DESC
LIMIT 10;

-- Questions needing improvement (< 60% helpful)
SELECT question_text, times_shown, helpfulness_pct
FROM v_l311_question_stats
WHERE times_shown > 10 AND helpfulness_pct < 60
ORDER BY times_shown DESC;

-- Category performance
SELECT * FROM v_l311_category_stats
ORDER BY category_helpfulness_pct DESC;

-- Recent negative feedback
SELECT aq.question_text, af.user_comment, af.created_at
FROM l311_answer_feedback af
JOIN l311_approved_questions aq ON af.approved_question_id = aq.id
WHERE af.feedback_type = 'negative'
AND af.created_at > NOW() - INTERVAL '7 days'
ORDER BY af.created_at DESC;
```

---

## SME Annotation Workflow

### Purpose
Subject matter experts (Louisville Metro 311 staff) can review and validate answer quality.

### Process

1. **Create SME User**
```sql
INSERT INTO l311_annotation_users (username, full_name, email, role)
VALUES ('jane.smith', 'Jane Smith', 'jane@louisvilleky.gov', 'sme');
```

2. **SME Reviews Question**
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
    1, 1,  -- question 1, user 1
    true, true, true, true,  -- all yes
    5, 5,  -- high ratings
    'Perfect answer, very clear and complete'
);
```

3. **View Progress**
```sql
SELECT * FROM v_l311_user_annotation_progress;
```

### Future: Annotation UI
Build a web interface where SMEs can:
- View unannotated questions
- Rate answer quality
- Suggest improvements
- Track their progress
- See aggregate stats

---

## Expansion Strategy

### Sources for New Questions

1. **Actual Chat Usage** - Track questions residents actually ask
2. **311 Call Data** - Common questions from call center
3. **Website FAQ** - Louisville Metro website common questions
4. **Social Media** - Questions from Facebook/Twitter
5. **SME Input** - Questions staff know are common

### Adding New Questions

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
    'New question here?',
    'Detailed answer here.',
    'Category',
    'Subcategory',
    'how_to',
    ARRAY['keyword1', 'keyword2'],
    ARRAY['Variation 1?', 'Variation 2?'],
    'medium',
    'Service Name'
);
```

### Version Control

When updating an answer:
```sql
-- Create new version
UPDATE l311_approved_questions
SET
    answer_text = 'Updated answer here',
    version = version + 1,
    source = 'SME_Revision',
    updated_at = NOW()
WHERE id = 1;
```

---

## Comparison with Zendesk Project

### Similarities
- Same table structure concept (approved Q&A corpus)
- Same annotation workflow (SME validation)
- Same stats tracking (usage, helpfulness)
- Same view pattern (stats, progress, quality)

### Differences
- **Prefix:** `l311_` vs Zendesk (no prefix or different tables)
- **Focus:** B2C resident help vs B2B product support
- **Categories:** 311 services vs product categories
- **Integration:** Chat agent vs product documentation
- **Scale:** 25 questions (expanding) vs 170+ questions

### Why Separate Tables
- Avoid conflicts in shared database
- Different business domains (city services vs manufacturing)
- Independent versioning and management
- Clear ownership and responsibility

---

## Next Steps

### Immediate (Week 1)
- [ ] Choose database (Supabase recommended)
- [ ] Run migrations
- [ ] Verify all questions loaded
- [ ] Test queries

### Short Term (Month 1)
- [ ] Integrate with chat agent (Phase 1: matching)
- [ ] Add feedback collection (thumbs up/down)
- [ ] Track usage statistics
- [ ] Review initial helpfulness data

### Medium Term (Month 2-3)
- [ ] Expand corpus to 50+ questions based on usage
- [ ] Build SME annotation interface
- [ ] Add stats dashboard tab
- [ ] A/B test answer variations

### Long Term (Month 4+)
- [ ] 100+ questions covering all major 311 services
- [ ] Continuous improvement based on feedback
- [ ] Integration with 311 tracking system (if API available)
- [ ] Multi-language support (Spanish)

---

## Files Created

1. **migrations/20260209_create_311_approved_questions.sql** (9.5 KB)
   - Database schema, tables, views, triggers, indexes

2. **migrations/20260209_load_initial_311_questions.sql** (13 KB)
   - Initial 25 Q&A pairs across 7 categories

3. **migrations/README.md** (7 KB)
   - Migration guide, deployment options, examples

4. **docs/APPROVED_QUESTIONS_CORPUS.md** (This file, 14 KB)
   - Overview, integration guide, expansion strategy

5. **docs/CLAUDE.md** (Updated)
   - Added "Approved Questions Corpus" section

---

## Summary

✅ **Created:** Database schema for approved questions corpus
✅ **Loaded:** 25 initial Q&A pairs across 7 categories
✅ **Documented:** Complete migration and integration guide
✅ **Committed:** All files to GitHub (commit `04c8262`)

**Status:** Ready for database deployment and chat agent integration

**Based on:** Zendesk project pattern for validated Q&A knowledge base

**Location:** `/Users/rachael/Documents/projects/rachaelroland/pipelines/pipelines/311/dashboard/migrations/`
