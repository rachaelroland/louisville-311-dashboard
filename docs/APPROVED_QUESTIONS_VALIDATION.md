# Approved Questions Validation & Integration

**Date:** February 12, 2026
**Status:** Testing Phase

---

## Overview

This document describes the process for testing and validating the Louisville 311 chat agent against our 53 approved questions corpus, and the plan for integrating database querying to improve response quality.

---

## Current State

### What We Have

1. **53 Approved Questions** - Loaded in Supabase database (`l311_approved_questions` table)
   - Coverage: 89.91% of 169,598 actual service requests
   - 13 categories spanning all major 311 services
   - 7 high-urgency safety-critical questions
   - Complete with validated answers, keywords, service names

2. **Chat Agent (B2C)** - Customer service chatbot in dashboard
   - Uses Claude Sonnet 4.5 via OpenRouter API
   - B2C customer service system prompt
   - Conversation memory (20 messages)
   - Rate limiting (20/session, 50/hour)
   - Feedback buttons (thumbs up/down)

### The Problem

**The chat agent currently does NOT query the approved questions database.**

- Agent generates responses using generic Claude knowledge with B2C prompt
- Does not leverage our $3,000 NLP investment (53 validated Q&A pairs)
- No guarantee responses match approved answers
- No usage tracking for approved questions (times_shown, times_helpful)

---

## Validation Process

### Step 1: Test Current State

**Script:** `test_approved_questions.py`

**What it does:**
1. Connects to Supabase and loads all 53 approved questions
2. Sends each question to the chat agent (via HTTP POST to `/chat/ask`)
3. Validates agent responses against approved answers
4. Generates validation report with pass/fail results

**Validation Criteria:**
- ✅ Contains contact information (311, louisvilleky.gov)
- ✅ Mentions relevant keywords from approved answer
- ✅ Mentions service name (if applicable)
- ✅ Includes procedural steps (for how-to questions)
- ✅ Similarity score to approved answer

**Expected Results (Current State):**
- **Low similarity** to approved answers (~20-40%)
- **Some failures** due to missing specific service info
- **Generally helpful** but not optimal (relies on Claude's general knowledge)

### Step 2: Run Validation

```bash
# Ensure dashboard is running
cd /Users/rachael/Documents/projects/rachaelroland/pipelines/pipelines/311/dashboard
./start_dashboard.sh

# In another terminal, run validation
cd /Users/rachael/Documents/projects/rachaelroland/pipelines/pipelines/311/dashboard
python3 test_approved_questions.py
```

**Outputs:**
- `validation_results.json` - Complete test results with all responses
- `validation_report.md` - Human-readable report with failed questions highlighted

**Estimated Time:** 3-5 minutes (53 questions × 3-5 seconds each)

### Step 3: Analyze Results

Review the validation report to understand:
- Which questions the agent handles well without database
- Which questions need approved answers (safety-critical, service-specific)
- Common gaps (missing contact info, procedures, service names)

---

## Integration Plan

### Phase 1: Add Database Connection

**File:** `dashboard_app.py`

**Changes Needed:**
1. Add psycopg2 dependency to requirements.txt
2. Add Supabase connection configuration
3. Create database connection pool

```python
import psycopg2
from psycopg2.pool import SimpleConnectionPool

# Configuration
SUPABASE_HOST = "db.cxzhgidmzosdavugggks.supabase.co"
SUPABASE_DB = "postgres"
SUPABASE_USER = "postgres"
SUPABASE_PASSWORD = os.getenv("SUPABASE_PASSWORD")

# Connection pool
db_pool = SimpleConnectionPool(
    minconn=1,
    maxconn=10,
    host=SUPABASE_HOST,
    database=SUPABASE_DB,
    user=SUPABASE_USER,
    password=SUPABASE_PASSWORD
)
```

### Phase 2: Implement Question Matching

**File:** `dashboard_app.py`

**New Function:**
```python
def find_approved_answer(user_question: str):
    """
    Search l311_approved_questions for matching Q&A
    Returns: (question_id, question_text, answer_text) or None
    """
    # Method 1: PostgreSQL full-text search (best)
    # Use tsvector search with keywords and question_text

    # Method 2: Keyword matching (fallback)
    # Find questions where any keyword appears in user query

    # Method 3: Similarity threshold (optional)
    # Use pg_trgm extension for similarity scoring
```

**Matching Strategy:**
1. Check if user question contains any keywords from approved questions
2. Use PostgreSQL `to_tsvector` and `to_tsquery` for full-text search
3. Rank results by relevance
4. Return top match if similarity > threshold (e.g., 0.7)

### Phase 3: Integrate with Chat Flow

**File:** `dashboard_app.py` - modify `/chat/ask` route

**Current Flow:**
```
User Question → OpenRouter API (Claude) → Generic Response
```

**New Flow:**
```
User Question → Search Approved Questions
  ↓
  Found Match? → Return Approved Answer (optionally enhanced by Claude)
  ↓
  No Match? → OpenRouter API (Claude) → Generic Response
```

**Implementation:**
```python
@rt('/chat/ask')
def post(message: str, request):
    # ... (existing rate limit and session code) ...

    # NEW: Search approved questions
    approved_match = find_approved_answer(message)

    if approved_match:
        # Found approved answer
        question_id, matched_question, approved_answer = approved_match

        # Track usage
        increment_question_shown(question_id)

        # Option A: Return approved answer directly
        assistant_text = approved_answer

        # Option B: Enhance with Claude (optional)
        # Use Claude to personalize/enhance approved answer
        # messages.append({
        #     "role": "system",
        #     "content": f"Use this approved answer: {approved_answer}"
        # })
        # assistant_text = call_claude(messages)
    else:
        # No approved answer found - use generic Claude
        assistant_text = call_claude(messages)

    # ... (rest of existing code) ...
```

### Phase 4: Usage Tracking

**Purpose:** Understand which approved questions are being used

**Database Updates:**
```sql
-- Track when question is shown
UPDATE l311_approved_questions
SET times_shown = times_shown + 1
WHERE id = :question_id;

-- Track helpful feedback (existing feedback buttons)
UPDATE l311_approved_questions
SET times_helpful = times_helpful + 1
WHERE id = :question_id;

-- Track not helpful feedback
UPDATE l311_approved_questions
SET times_not_helpful = times_not_helpful + 1
WHERE id = :question_id;
```

**Analytics:**
- Dashboard page showing most-used approved questions
- Helpfulness percentage per question
- Identify questions that need answer improvement

---

## Testing After Integration

### Validation Script (Updated)

**Script:** `test_approved_questions_integrated.py`

**What's Different:**
- Tests now expect HIGH similarity (>80%) to approved answers
- Validates that approved answers are being returned
- Checks that usage stats are being incremented

**Expected Results (After Integration):**
- **High similarity** to approved answers (80-95%)
- **100% pass rate** for approved questions
- **All questions tracked** in database (times_shown incremented)

---

## Success Metrics

### Before Integration (Current)
- ❌ Similarity to approved answers: ~20-40%
- ❌ Approved answers used: 0%
- ❌ Usage tracking: None
- ⚠️ Response quality: Decent but inconsistent

### After Integration (Target)
- ✅ Similarity to approved answers: 80-95%
- ✅ Approved answers used: 100% (when question matches)
- ✅ Usage tracking: All 53 questions tracked
- ✅ Response quality: Excellent and consistent

---

## Timeline

| Phase | Task | Estimated Time | Status |
|-------|------|----------------|--------|
| 1 | Run validation test (current state) | 30 min | ⏳ Ready |
| 2 | Add database connection to dashboard | 1 hour | ⏸️ Pending |
| 3 | Implement question matching function | 2 hours | ⏸️ Pending |
| 4 | Integrate with chat flow | 1 hour | ⏸️ Pending |
| 5 | Add usage tracking | 1 hour | ⏸️ Pending |
| 6 | Run validation test (integrated) | 30 min | ⏸️ Pending |
| 7 | Deploy to production | 30 min | ⏸️ Pending |

**Total:** ~6-7 hours of development work

---

## Files Created/Modified

### New Files
- ✅ `test_approved_questions.py` - Validation test script
- ⏸️ `test_approved_questions_integrated.py` - Post-integration test
- ✅ `docs/APPROVED_QUESTIONS_VALIDATION.md` - This document

### Modified Files (Planned)
- ⏸️ `dashboard_app.py` - Add database integration
- ⏸️ `requirements.txt` - Add psycopg2-binary
- ⏸️ `.env` (create) - Store SUPABASE_PASSWORD securely

---

## FAQ

### Q: Why validate before integrating?

**A:** To establish a baseline. We need to see how the current agent performs WITHOUT approved answers so we can measure improvement after integration.

### Q: What if the agent handles some questions well already?

**A:** Great! That means Claude's general knowledge is solid. But for service-specific, safety-critical, and procedural questions, we want guaranteed accuracy from validated answers.

### Q: Should we ALWAYS return approved answers?

**A:** Not necessarily. Three options:
1. **Direct return** - Return approved answer verbatim (fastest, most accurate)
2. **Enhanced return** - Use Claude to personalize approved answer based on conversation context
3. **Hybrid** - Return approved answer for safety-critical questions, enhance for others

Recommend starting with #1 (direct return), then experimenting with #2 if responses feel too robotic.

### Q: What about questions NOT in the approved corpus?

**A:** These will fall back to generic Claude responses (current behavior). Over time, we'll:
- Track which questions users ask that we don't have approved answers for
- Add new approved questions based on actual usage patterns
- Expand from 53 to 60-70 questions (months 2-3 roadmap)

### Q: How do we handle the remaining 10.09% of requests?

**A:** These are covered by:
- Generic Claude responses (chat fallback)
- Future question expansion (phases 4-5)
- SME annotation workflow for quality improvement

---

## Next Steps

1. **Run validation test** - Establish baseline performance
2. **Review results** - Identify specific gaps
3. **Decide integration approach** - Direct return vs enhanced
4. **Implement database integration** - Add psycopg2 and connection
5. **Deploy and re-test** - Validate improved performance
6. **Monitor usage** - Track which questions are most helpful

---

**Prepared by:** Claude Code
**For Demo:** Partner review and production deployment
**Status:** Ready for validation testing

🚀 **Ready to test!**
