# DDL Conflict Analysis - Louisville 311 vs Zendesk

## Purpose
Verify that Louisville 311 database schema does NOT conflict with existing Zendesk project DDL when using the same database.

**Analysis Date:** February 9, 2026
**Zendesk Schema Location:** `/Users/rachael/Documents/projects/roar_appliedindustrials/lucifer/projects/zendesk/`
**Louisville 311 Schema Location:** `/Users/rachael/Documents/projects/rachaelroland/pipelines/pipelines/311/dashboard/migrations/`

---

## Zendesk Project DDL (Existing)

### Tables (12 total, NO PREFIX)
```sql
1.  agent_interactions
2.  annotation_consensus
3.  annotation_sessions
4.  annotation_users
5.  answer_annotations
6.  approved_questions
7.  qa_annotations
8.  qa_assignments
9.  spec_annotations
10. spec_assignments
11. spec_image_clusters
12. spec_image_embeddings
```

### Functions (4 total, NO PREFIX)
```sql
1. assign_qa_to_user(p_user_id INTEGER, p_count INTEGER DEFAULT 10)
2. calculate_consensus(p_qa_id INTEGER)
3. update_agent_interaction_timestamp()
4. update_approved_questions_updated_at()
```

### Views (8 total, some with v_ prefix)
```sql
1. agent_performance_stats
2. spec_annotation_progress
3. v_annotation_progress
4. v_annotation_quality
5. v_answer_annotation_stats
6. v_category_answer_quality
7. v_qa_pending_annotation
8. v_user_answer_annotation_progress
```

### Triggers (2 total, NO PREFIX)
```sql
1. approved_questions_updated_at (on table: approved_questions)
2. trigger_update_agent_interaction_timestamp (on table: agent_interactions)
```

---

## Louisville 311 DDL (New)

### Tables (4 total, ALL WITH l311_ PREFIX) ✅
```sql
1. l311_approved_questions
2. l311_answer_feedback
3. l311_annotation_users
4. l311_answer_annotations
```

### Functions (3 total, ALL WITH l311_ PREFIX) ✅
```sql
1. update_l311_approved_questions_updated_at()
2. update_l311_annotation_users_updated_at()
3. update_l311_answer_annotations_updated_at()
```

### Views (3 total, ALL WITH v_l311_ PREFIX) ✅
```sql
1. v_l311_question_stats
2. v_l311_category_stats
3. v_l311_user_annotation_progress
```

### Triggers (3 total, ALL WITH l311_ PREFIX) ✅
```sql
1. l311_approved_questions_updated_at (on table: l311_approved_questions)
2. l311_annotation_users_updated_at (on table: l311_annotation_users)
3. l311_answer_annotations_updated_at (on table: l311_answer_annotations)
```

---

## Conflict Analysis

### ❌ POTENTIAL CONFLICTS (Without Prefix)
If we had NOT used the `l311_` prefix, we would have conflicts:

| Object Type | Would Conflict With |
|-------------|---------------------|
| Table | `approved_questions` ← CONFLICT with Zendesk |
| Table | `annotation_users` ← CONFLICT with Zendesk |
| Table | `answer_annotations` ← CONFLICT with Zendesk |
| Function | `update_approved_questions_updated_at()` ← CONFLICT with Zendesk |
| View | `v_answer_annotation_stats` ← CONFLICT with Zendesk |
| View | `v_user_answer_annotation_progress` ← CONFLICT with Zendesk |
| Trigger | `approved_questions_updated_at` ← CONFLICT with Zendesk |

**7 conflicts would occur without prefix!**

---

### ✅ ACTUAL CONFLICTS (With l311_ Prefix)

| Louisville 311 Object | Zendesk Object | Conflict? |
|-----------------------|----------------|-----------|
| l311_approved_questions | approved_questions | ❌ NO - Different name |
| l311_answer_feedback | (none) | ✅ NO - Unique to 311 |
| l311_annotation_users | annotation_users | ❌ NO - Different name |
| l311_answer_annotations | answer_annotations | ❌ NO - Different name |
| update_l311_approved_questions_updated_at() | update_approved_questions_updated_at() | ❌ NO - Different name |
| update_l311_annotation_users_updated_at() | (none) | ✅ NO - Unique to 311 |
| update_l311_answer_annotations_updated_at() | (none) | ✅ NO - Unique to 311 |
| v_l311_question_stats | (none) | ✅ NO - Unique to 311 |
| v_l311_category_stats | (none) | ✅ NO - Unique to 311 |
| v_l311_user_annotation_progress | v_user_answer_annotation_progress | ❌ NO - Different name |
| l311_approved_questions_updated_at | approved_questions_updated_at | ❌ NO - Different name |
| l311_annotation_users_updated_at | (none) | ✅ NO - Unique to 311 |
| l311_answer_annotations_updated_at | (none) | ✅ NO - Unique to 311 |

**RESULT: ZERO CONFLICTS ✅**

---

## Similar Names Analysis

While there are NO conflicts, some objects serve similar purposes:

### Approved Questions
- **Zendesk:** `approved_questions` - Product support Q&A (170 questions)
- **Louisville 311:** `l311_approved_questions` - City services Q&A (25+ questions)
- **Purpose:** Both store validated Q&A pairs, but for different domains
- **Conflict:** ❌ NO - Different table names

### Annotation Users
- **Zendesk:** `annotation_users` - SMEs for product support
- **Louisville 311:** `l311_annotation_users` - SMEs for city services
- **Purpose:** Both manage annotator accounts
- **Conflict:** ❌ NO - Different table names

### Answer Annotations
- **Zendesk:** `answer_annotations` - Quality review for product Q&A
- **Louisville 311:** `l311_answer_annotations` - Quality review for 311 Q&A
- **Purpose:** Both track SME reviews
- **Conflict:** ❌ NO - Different table names

### Views
- **Zendesk:** `v_user_answer_annotation_progress` - SME progress tracking
- **Louisville 311:** `v_l311_user_annotation_progress` - SME progress tracking
- **Purpose:** Both show annotation progress
- **Conflict:** ❌ NO - Different view names

---

## Unique to Louisville 311

These objects are ONLY in Louisville 311 (not in Zendesk):

### Tables
1. `l311_answer_feedback` - Tracks thumbs up/down from residents in chat

### Views
1. `v_l311_question_stats` - Per-question usage and helpfulness metrics
2. `v_l311_category_stats` - Category-level performance metrics

### All Functions and Triggers
All Louisville 311 functions and triggers are unique because of the `l311_` prefix.

---

## Unique to Zendesk

These objects are ONLY in Zendesk (not in Louisville 311):

### Tables (8 unique)
1. `agent_interactions` - Asana agent tracking
2. `annotation_consensus` - Multi-annotator consensus
3. `annotation_sessions` - Annotation session management
4. `qa_annotations` - Q&A pair annotations
5. `qa_assignments` - Task assignment to annotators
6. `spec_annotations` - Spec sheet image annotations
7. `spec_assignments` - Spec annotation assignments
8. `spec_image_clusters` - K-means clustered spec images
9. `spec_image_embeddings` - CLIP embeddings for spec images

### Functions (2 unique)
1. `assign_qa_to_user()` - Auto-assign questions to annotators
2. `calculate_consensus()` - Calculate multi-annotator agreement

### Views (5 unique)
1. `agent_performance_stats` - Asana agent performance
2. `spec_annotation_progress` - Spec sheet annotation progress
3. `v_annotation_progress` - Overall annotation progress
4. `v_annotation_quality` - Annotation quality metrics
5. `v_qa_pending_annotation` - Questions awaiting annotation

---

## Database Sharing Strategy

### Recommended Approach ✅
**Use the SAME database for both projects**

**Why it works:**
1. ✅ Zero naming conflicts (l311_ prefix on all objects)
2. ✅ Clear separation of concerns
3. ✅ Easier management (one database to maintain)
4. ✅ Can share common infrastructure (Supabase, backups)
5. ✅ Similar patterns (annotation workflow, Q&A validation)

**Connection string can be shared:**
```bash
# Same DATABASE_URL for both projects
export DATABASE_URL="postgresql://user:pass@host:5432/postgres"

# Zendesk migrations
psql $DATABASE_URL < zendesk/migrations/*.sql

# Louisville 311 migrations
psql $DATABASE_URL < 311/migrations/*.sql
```

### Table Organization in Database

```
database: postgres (or louisville_roar_db)
│
├── Zendesk Tables (no prefix)
│   ├── agent_interactions
│   ├── annotation_consensus
│   ├── annotation_sessions
│   ├── annotation_users
│   ├── answer_annotations
│   ├── approved_questions
│   ├── qa_annotations
│   ├── qa_assignments
│   ├── spec_annotations
│   ├── spec_assignments
│   ├── spec_image_clusters
│   └── spec_image_embeddings
│
└── Louisville 311 Tables (l311_ prefix)
    ├── l311_approved_questions
    ├── l311_answer_feedback
    ├── l311_annotation_users
    └── l311_answer_annotations
```

---

## Verification Queries

After deploying both schemas, verify no conflicts:

```sql
-- List all tables (should see both projects)
SELECT table_name, table_schema
FROM information_schema.tables
WHERE table_schema = 'public'
ORDER BY table_name;

-- Check for name conflicts (should return 0 rows)
SELECT t1.table_name
FROM information_schema.tables t1
JOIN information_schema.tables t2
  ON t1.table_name = t2.table_name
WHERE t1.table_schema = 'public'
  AND t2.table_schema = 'public'
  AND t1.table_catalog != t2.table_catalog;

-- List all functions
SELECT routine_name, routine_type
FROM information_schema.routines
WHERE routine_schema = 'public'
ORDER BY routine_name;

-- List all views
SELECT table_name
FROM information_schema.views
WHERE table_schema = 'public'
ORDER BY table_name;

-- Count Zendesk tables (should be 12)
SELECT COUNT(*)
FROM information_schema.tables
WHERE table_schema = 'public'
  AND table_name NOT LIKE 'l311_%';

-- Count Louisville 311 tables (should be 4)
SELECT COUNT(*)
FROM information_schema.tables
WHERE table_schema = 'public'
  AND table_name LIKE 'l311_%';
```

---

## Migration Order

When deploying to a fresh database:

```bash
# 1. Create database
createdb louisville_roar_db

# 2. Deploy Zendesk schema first (existing project)
cd /Users/rachael/Documents/projects/roar_appliedindustrials/lucifer/projects/zendesk
psql louisville_roar_db < migrations/20260104_create_approved_questions.sql
psql louisville_roar_db < migrations/20260104_create_answer_annotations.sql
# ... other Zendesk migrations

# 3. Deploy Louisville 311 schema second (new project)
cd /Users/rachael/Documents/projects/rachaelroland/pipelines/pipelines/311/dashboard
psql louisville_roar_db < migrations/20260209_create_311_approved_questions.sql
psql louisville_roar_db < migrations/20260209_load_initial_311_questions.sql

# 4. Verify both schemas loaded
psql louisville_roar_db -c "\dt"  # List all tables
psql louisville_roar_db -c "SELECT COUNT(*) FROM approved_questions;"  # Zendesk
psql louisville_roar_db -c "SELECT COUNT(*) FROM l311_approved_questions;"  # 311
```

---

## Foreign Key Safety

Louisville 311 tables do NOT reference Zendesk tables:

✅ `l311_approved_questions` - Self-contained, no FK to Zendesk
✅ `l311_answer_feedback` - FKs only to l311_approved_questions
✅ `l311_annotation_users` - Self-contained, no FK to Zendesk
✅ `l311_answer_annotations` - FKs only to l311_ tables

**Result:** Complete isolation between projects at the database constraint level.

---

## Rollback Safety

If Louisville 311 schema needs to be removed:

```sql
-- Drop all Louisville 311 objects (safe - won't affect Zendesk)
DROP VIEW IF EXISTS v_l311_user_annotation_progress CASCADE;
DROP VIEW IF EXISTS v_l311_category_stats CASCADE;
DROP VIEW IF EXISTS v_l311_question_stats CASCADE;

DROP TABLE IF EXISTS l311_answer_annotations CASCADE;
DROP TABLE IF EXISTS l311_answer_feedback CASCADE;
DROP TABLE IF EXISTS l311_annotation_users CASCADE;
DROP TABLE IF EXISTS l311_approved_questions CASCADE;

DROP FUNCTION IF EXISTS update_l311_answer_annotations_updated_at() CASCADE;
DROP FUNCTION IF EXISTS update_l311_annotation_users_updated_at() CASCADE;
DROP FUNCTION IF EXISTS update_l311_approved_questions_updated_at() CASCADE;

-- Verify Zendesk objects still exist
SELECT COUNT(*) FROM approved_questions;  -- Should still work
SELECT COUNT(*) FROM annotation_users;    -- Should still work
```

---

## Summary

### ✅ SAFE TO DEPLOY - ZERO CONFLICTS

**Conflict Analysis:**
- ❌ **0** table name conflicts
- ❌ **0** function name conflicts
- ❌ **0** view name conflicts
- ❌ **0** trigger name conflicts
- ❌ **0** foreign key conflicts

**Strategy:**
- ✅ Use `l311_` prefix on ALL Louisville 311 objects
- ✅ Share same database with Zendesk project
- ✅ Complete isolation through naming convention
- ✅ Safe to deploy and rollback independently

**Recommendation:** **APPROVED - Proceed with deployment** 🚀

The `l311_` prefix successfully prevents all DDL conflicts with the existing Zendesk schema. Both projects can safely coexist in the same PostgreSQL database.

---

## Next Steps

1. ✅ Conflict analysis complete
2. ⏭️ Choose database (Supabase recommended)
3. ⏭️ Deploy Zendesk schema (if not already done)
4. ⏭️ Deploy Louisville 311 schema
5. ⏭️ Verify both schemas with test queries
6. ⏭️ Update application connection strings

**Location:** `/Users/rachael/Documents/projects/rachaelroland/pipelines/pipelines/311/dashboard/migrations/DDL_CONFLICT_ANALYSIS.md`
