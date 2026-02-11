# CLAUDE.md - Louisville Metro 311 NLP Analysis Project

## 🔄 Latest Session State (Feb 9, 2026)

**READ THIS FIRST:** This is the complete context for the Louisville Metro 311 NLP analysis project.

**Status:** Analysis complete ✅ | Reports delivered ✅ | Dashboard deployed ✅ | B2C transformation complete ✅

**IMPORTANT - PROJECT LOCATION:**
```
/Users/rachael/Documents/projects/rachaelroland/pipelines/pipelines/311/dashboard/
```
⚠️ **Always use this local directory path - files have been moved from Downloads**

**Quick Summary:**
- Dataset: 169,598 Louisville Metro 311 service requests (2024)
- Processing: 13.5 hours, 848,042 API calls, $998 cost
- Analysis: Sentiment, urgency, NER, topics, ABSA (aspect-based sentiment)
- Deliverables: Technical report, business opportunities report, interactive dashboard
- Key Finding: Call center can save $125K/year by automating 56.3% of requests
- Dashboard: Deployed at https://louisville-311-dashboard.onrender.com
- Chat Agent: Transformed to B2C customer service for Louisville residents

---

## Project Overview

**Goal:** Analyze Louisville Metro 311 service requests using advanced NLP to identify patterns, bottlenecks, and business opportunities.

**Dataset:**
- Source: Louisville Metro 311 system
- Period: January 1 - December 31, 2024
- Records: 169,598 service requests
- Raw data: `/Users/rachael/Documents/projects/rachaelroland/pipelines/pipelines/311/data/raw/louisville_311_2024.csv`
- Processed: `/Users/rachael/Documents/projects/rachaelroland/pipelines/pipelines/311/data/processed/311_processed_with_nlp.csv` (168MB)

**NLP Pipeline:**
- Model: Claude Sonnet 4.5 via OpenRouter API
- Processing: Parallel async with checkpoint/resume support (20 concurrent requests)
- Techniques: Sentiment analysis, urgency classification (0-10 scale), NER, topic extraction, ABSA
- Topic Modeling: LDA + NMF (15 topics each)

---

## Current Status (Updated Feb 1, 2026 - 10:00 AM MT)

### ✅ INTERACTIVE DASHBOARD DEPLOYED (Feb 9, 2026)
**Status:** FastHTML web application deployed and transformed to B2C customer service
**Location:** `/Users/rachael/Documents/projects/rachaelroland/pipelines/pipelines/311/dashboard/`
**Live URL:** https://louisville-311-dashboard.onrender.com

**Features:**
- ✅ **7 Interactive Tabs** - Overview, Call Center, Topics, Sentiment, Urgency, Business Opportunities, Chat
- ✅ **B2C Chat Agent** - Customer service for Louisville residents (not analytics)
- ✅ **Chat Enhancements** - Memory, rate limiting, feedback, export, follow-up questions
- ✅ **Interactive Plotly charts** - Hover, zoom, download
- ✅ **Bootstrap 5 styling** - Professional gradient design
- ✅ **OpenRouter API** - Claude Sonnet 4.5 integration
- ✅ **Comprehensive tests** - 43 passing tests with pytest

**Tech Stack:**
- FastHTML (Python web framework)
- Plotly for interactive visualizations
- Pandas for data processing
- Bootstrap 5 for responsive UI
- Claude Sonnet 4.5 via OpenRouter for chat

**Quick Start:**
```bash
cd /Users/rachael/Documents/projects/rachaelroland/pipelines/pipelines/311/dashboard
./start_dashboard.sh
# Visit http://localhost:5002
```

**Pages:**
1. `/` - Overview with key metrics and charts
2. `/call-center` - Bottleneck analysis and automation opportunities
3. `/topics` - Topic modeling insights
4. `/sentiment` - Sentiment analysis deep dive
5. `/urgency` - Urgency patterns and distribution
6. `/business` - ROI analysis and strategic recommendations
7. `/chat` - **B2C Customer service chat** for Louisville residents

### ✅ B2C CUSTOMER SERVICE TRANSFORMATION (Feb 9, 2026)
**Status:** Chat agent transformed from analytics to customer service
**Commit:** `66f218c` + `471897b`
**Documentation:** `docs/B2C_TRANSFORMATION.md`

**What Changed:**
- **Before:** Analytics assistant for city officials analyzing 311 data
- **After:** Customer service rep helping Louisville residents use 311 services

**Key Changes:**
- System prompt rewritten for customer service role
- Quick questions now resident-focused ("How do I submit a request?")
- UI text addresses residents directly
- Follow-up questions suggest actionable next steps
- Warm, friendly, empathetic tone (not analytical)

**Example Questions:**
- "How do I submit a 311 service request?"
- "What types of issues can I report to 311?"
- "How long does it take to fix a pothole?"
- "Can I track the status of my request?"
- "What's the difference between 311 and 911?"

**Safety Features Maintained:**
- Rate limiting (20 questions/session, 50/hour)
- Conversation memory (20 messages)
- Respect for all community members
- Refuses inappropriate questions warmly
- Export transcripts, feedback buttons

### ✅ APPROVED QUESTIONS CORPUS (Feb 9, 2026)
**Status:** Database schema created, initial 25+ questions loaded
**Purpose:** Known Q&A pairs to improve chat agent responses
**Documentation:** `migrations/20260209_create_311_approved_questions.sql`

**Database Schema:**
```sql
-- Tables (l311_ prefix to avoid conflicts)
- l311_approved_questions       -- Core Q&A corpus
- l311_answer_feedback          -- Resident feedback (thumbs up/down)
- l311_annotation_users         -- SME user management
- l311_answer_annotations       -- SME quality review
```

**Question Categories (Initial Corpus: 25 Questions):**
1. **General (5)** - What is 311, how to submit, tracking, timelines, 311 vs 911
2. **Waste Management (5)** - Bulk pickup, schedules, missed pickup, recycling, yard waste
3. **Street Maintenance (4)** - Potholes, streetlights, sidewalks, street signs
4. **Code Enforcement (3)** - Property violations, abandoned vehicles, tall grass
5. **Parks (2)** - Park maintenance, tree issues
6. **Animal Control (2)** - Stray animals, barking dogs
7. **Water/Sewer (2)** - Water main breaks, sewer backups

**Question Structure:**
```sql
{
    question_text: "How do I submit a 311 service request?",
    answer_text: "There are three easy ways...",
    category: "General",
    subcategory: "Submitting Requests",
    question_type: "how_to",  -- how_to, what_is, timeline, tracking, eligibility
    keywords: ['submit', 'report', 'request'],
    common_variations: ['How can I report...', 'How do I file...'],
    typical_urgency: "low",
    typical_response_time: "Immediate (information only)",
    service_name: NULL  -- Links to 311 service types from data
}
```

**Usage Stats Tracked:**
- `times_shown` - How many times shown to residents
- `times_helpful` - Thumbs up count
- `times_not_helpful` - Thumbs down count
- Calculated helpfulness percentage

**Future Expansion:**
- Add questions from actual chat usage patterns
- SME validation of answer quality (annotations table ready)
- Integration with chat agent for suggested responses
- Answer versioning and A/B testing

**Migration Files:**
1. `20260209_create_311_approved_questions.sql` - Schema (4 tables, 3 views, triggers)
2. `20260209_load_initial_311_questions.sql` - Initial 25 Q&A pairs

**Sample Queries:**
```sql
-- Find questions by category
SELECT question_text, answer_text
FROM l311_approved_questions
WHERE category = 'Waste Management' AND is_approved = true;

-- Search by keywords
SELECT question_text, answer_text
FROM l311_approved_questions
WHERE 'pothole' = ANY(keywords);

-- View question stats
SELECT * FROM v_l311_question_stats
ORDER BY helpfulness_pct DESC LIMIT 10;

-- Category performance
SELECT * FROM v_l311_category_stats;
```

**Integration Plan:**
- [ ] Phase 1: Load database on production (Supabase or local PostgreSQL)
- [ ] Phase 2: Update chat agent to reference approved questions
- [ ] Phase 3: Track usage and feedback via dashboard
- [ ] Phase 4: SME annotation interface for answer quality review

### ✅ FILE ORGANIZATION (Feb 9, 2026)
**Status:** Project organized properly, Downloads folder archived

**Old Location (REMOVED):**
- ❌ `/Users/rachael/Downloads/311_nlp_analysis_report/`

**New Location (USE THIS):**
- ✅ `/Users/rachael/Documents/projects/rachaelroland/pipelines/pipelines/311/dashboard/`

**Directory Structure:**
```
dashboard/
├── dashboard_app.py           # Main application (81 KB, B2C transformed)
├── sample_311_data.csv        # Sample dataset (8.6 MB, 9,337 requests)
├── 311_nlp_results.json       # NLP analysis results
├── requirements.txt           # Python dependencies
├── render.yaml                # Render.com deployment config
├── start_dashboard.sh         # Local startup script
├── test_dashboard.py          # Test suite (43 tests)
├── README.md                  # Comprehensive documentation
├── docs/                      # All documentation
│   ├── B2C_TRANSFORMATION.md # B2C transformation guide
│   ├── CHAT_*.md             # Chat feature docs
│   ├── DEPLOY.md             # Deployment guide
│   ├── CLAUDE.md             # This file
│   └── *.md                  # Other docs
├── .git/                      # Git repository (full history)
└── .venv/                     # Virtual environment
```

### ✅ BUSINESS OPPORTUNITIES ANALYSIS COMPLETE (Feb 1, 2026)
**Status:** Call center bottleneck analysis with ROI projections
**Documentation:** `docs/BUSINESS_OPPORTUNITIES.md`

**Key Findings:**

**Call Center Volume:**
- 106,631 calls/year (62.9% of all 311 requests)
- $222,150 annual cost in agent time
- 48.4% are simple information requests (NSR)
- 87.6% are low/medium urgency

**Opportunity:**
- Reduce call volume by 56.3% (60,035 calls)
- Save $125,075/year in agent time
- 24/7 self-service for routine requests
- Focus agents on 11,765 truly urgent calls (11%)

**Top Bottlenecks:**
1. **NSR Metro Agencies** - 34,981 calls/year (32.8%)
   - Info requests, referrals, policy questions
   - Solution: FAQ + Chatbot + IVR

2. **Waste Management** - 15,880 calls/year (14.9%)
   - Cart requests, missed pickups, appointments
   - Solution: Online cart ordering + schedule lookup

3. **Status Checks** - 52,646 calls/year (49.4%)
   - Empty/minimal descriptions = "Where's my request?"
   - Solution: Self-service status tracking + SMS alerts

4. **NSR Social Services** - 6,075 calls/year (5.7%)
   - Resource lookups, social service referrals
   - Solution: Searchable directory + live chat

**3-Phase Implementation:**
- Phase 1 (0-3 months): FAQ + IVR → 15,467 calls saved (14.5%)
- Phase 2 (3-6 months): Self-service portal → 36,446 calls saved (34.2%)
- Phase 3 (6-12 months): Proactive alerts → 8,122 calls saved (7.6%)

**Files Created:**
- `BUSINESS_OPPORTUNITIES.md` (7.6KB) - Executive summary
- `BUSINESS_OPPORTUNITIES.docx` (16KB) - Word format for presentations
- `BOTTLENECK_ANALYSIS_REPORT.md` (14KB) - Complete technical deep-dive
- `call_center_bottleneck_analysis.py` (15KB) - Analysis script
- `nsr_deep_dive.py` (4.9KB) - NSR category analysis
- `generate_summary_stats.py` (5.8KB) - Statistics generator

### ✅ COMPREHENSIVE REPORTS DELIVERED (Feb 1, 2026)
**Status:** Technical analysis and executive summary complete
**Location:** `/Users/rachael/Downloads/311_nlp_analysis_report/`

**Technical Report:**
- `Louisville_311_NLP_Analysis_Report.md` (39KB)
- `Louisville_311_NLP_Analysis_Report.docx` (32KB)
- 13 main sections + appendices
- Complete methodology, findings, recommendations

**Key Findings:**
- **Sentiment:** 55% Neutral (90,163), 45% Negative (74,616), <1% Positive (261)
- **Top Issues:**
  1. Illegal Dumping Crisis (16.6% topic weight) - IMMEDIATE ACTION
  2. Missed Service Collections (15.3% topic weight) - SERVICE RELIABILITY
  3. Street Lighting Failures (18.9% topic weight) - INFRASTRUCTURE DECAY
  4. Waste Management (30-35% of all requests) - LARGEST CATEGORY
  5. Parking Violations (10-15% of requests)

**Processing Stats:**
- Runtime: 13 hours 33 minutes
- API Calls: 848,042 total
- Cost: $998 ($0.0059 per record)
- Success Rate: 99.7% urgency, 97.3% sentiment, 99.6% NER, 77.2% ABSA

**Recommendations:**
1. Launch anti-dumping task force in identified hot spot alleys
2. Implement GPS tracking for waste collection vehicles
3. Priority street lighting repairs in dark zones
4. Deploy geographic heat maps for resource allocation
5. Create predictive models for high-volume periods
6. Build self-service portal for routine requests **NEW**
7. Implement chatbot for FAQ and information lookups **NEW**
8. Deploy proactive SMS/email notifications **NEW**

---

## Data Schema

**Processed CSV Columns (311_processed_with_nlp.csv):**
```
service_request_id      - Unique ID (e.g., SR-PRKG-24-000001)
requested_datetime      - Request timestamp
status_description      - OPEN/CLOSED/IN PROGRESS
service_name           - Service type (e.g., "Illegal Dumping")
description            - Request text description
agency_responsible     - Metro agency (e.g., "Solid Waste", "LMPD")
address                - Location address
zip_code               - Postal code
council_district       - District number (1-26)
latitude/longitude     - GPS coordinates
sentiment              - positive/negative/neutral
urgency_level          - low/medium/high
urgency_score          - 0-10 urgency score
ner_json               - Named entities (locations, dates, people)
topics_json            - Extracted topics with keywords
absa_json              - Aspect-based sentiment (granular sentiments)
```

**Topic Modeling Results (311_nlp_results.json):**
```json
{
  "metadata": {
    "processing_date": "2025-XX-XX",
    "total_requests": 169598,
    "parallel_processing": true,
    "concurrency": 20
  },
  "topic_modeling": {
    "lda": {
      "n_topics": 15,
      "topics": [...],
      "coherence_score": 0.XX
    },
    "nmf": {
      "n_topics": 15,
      "topics": [...],
      "coherence_score": 0.XX
    }
  }
}
```

---

## Key Files and Locations

### Report Package
**Location:** `/Users/rachael/Downloads/311_nlp_analysis_report/`

**Contents:**
```
Technical Analysis:
├── Louisville_311_NLP_Analysis_Report.docx (32KB)
├── Louisville_311_NLP_Analysis_Report.md (39KB)
└── 311_nlp_results.json (19KB)

Business Opportunities:
├── BUSINESS_OPPORTUNITIES.docx (16KB)
├── BUSINESS_OPPORTUNITIES.md (7.6KB)
└── BOTTLENECK_ANALYSIS_REPORT.md (14KB)

Analysis Scripts:
├── call_center_bottleneck_analysis.py (15KB)
├── nsr_deep_dive.py (4.9KB)
└── generate_summary_stats.py (5.8KB)

Interactive Dashboard:
├── dashboard_app.py (24KB) ⭐ FastHTML web app
├── start_dashboard.sh (541B) - One-click launcher
├── requirements.txt (84B) - Python dependencies
└── README_DASHBOARD.md (6.6KB) - Setup guide

Documentation:
├── README.txt (5.5KB) - Package contents
└── CLAUDE.md (this file) - Session context
```

### Data Files
```
Raw Data:
/Users/rachael/Documents/projects/rachaelroland/pipelines/pipelines/311/data/raw/louisville_311_2024.csv

Processed Data:
/Users/rachael/Documents/projects/rachaelroland/pipelines/pipelines/311/data/processed/311_processed_with_nlp.csv (168MB)

Pipeline Output:
/Users/rachael/Documents/projects/rachaelroland/pipelines/pipelines/311/output/311_nlp_results.json

Analysis Scripts:
/Users/rachael/Documents/projects/rachaelroland/pipelines/pipelines/311/analysis/
├── EXECUTIVE_SUMMARY.md
├── BOTTLENECK_ANALYSIS_REPORT.md
├── README.md
├── call_center_bottleneck_analysis.py
├── nsr_deep_dive.py
└── generate_summary_stats.py
```

### Processing Pipeline
```
Pipeline Location:
/Users/rachael/Documents/projects/rachaelroland/pipelines/pipelines/311/

Key Scripts:
├── process_311_parallel_checkpoint.py - Main processing script
├── config.py - Configuration (API keys, paths)
└── nlp311/ - NLP pipeline modules
    ├── data/models.py - ServiceRequest data model
    ├── modeling/topic_modeling.py - LDA/NMF topic modeling
    └── nlp/prompts.py - Prompt templates for Claude
```

---

## Quick Commands

### Dashboard
```bash
# Launch interactive dashboard
cd /Users/rachael/Downloads/311_nlp_analysis_report
./start_dashboard.sh
# Visit http://localhost:5002

# Or manually
uv pip install fasthtml pandas plotly uvicorn
PORT=5002 uv run python dashboard_app.py
```

### Analysis Scripts
```bash
# Run call center bottleneck analysis
cd /Users/rachael/Documents/projects/rachaelroland/pipelines/pipelines/311/analysis
uv run python call_center_bottleneck_analysis.py

# Deep dive into NSR categories
uv run python nsr_deep_dive.py

# Generate summary statistics
uv run python generate_summary_stats.py
```

### Data Exploration
```bash
# Count records by sentiment
cd /Users/rachael/Documents/projects/rachaelroland/pipelines/pipelines/311/data/processed
head -1 311_processed_with_nlp.csv && tail -n +2 311_processed_with_nlp.csv | cut -d',' -f12 | sort | uniq -c

# Count by urgency level
tail -n +2 311_processed_with_nlp.csv | cut -d',' -f13 | sort | uniq -c

# Top 10 service types
tail -n +2 311_processed_with_nlp.csv | cut -d',' -f4 | sort | uniq -c | sort -rn | head -10

# Top agencies
tail -n +2 311_processed_with_nlp.csv | cut -d',' -f6 | sort | uniq -c | sort -rn | head -10
```

### Document Conversion
```bash
# Convert markdown to DOCX (pandoc required)
cd /Users/rachael/Downloads/311_nlp_analysis_report
pandoc BUSINESS_OPPORTUNITIES.md -o BUSINESS_OPPORTUNITIES.docx
pandoc Louisville_311_NLP_Analysis_Report.md -o Louisville_311_NLP_Analysis_Report.docx
```

---

## Session Context Questions Asked

### User Questions & Answers

**Q1: "Give me a full report"**
- Created comprehensive 311 NLP analysis report with executive summary
- Included methodology, findings, recommendations, technical details
- 13 main sections covering all aspects of the analysis
- Delivered in both Markdown and DOCX formats

**Q2: "Give this to me with an executive summary, put it in a subdir in downloads and convert to docx"**
- Created `/Users/rachael/Downloads/311_nlp_analysis_report/` directory
- Added executive summary at top of report
- Converted to DOCX using pandoc
- Packaged with JSON results and README

**Q3: "Does this include animal metro services? Are there questions about adoption?"**
- Analyzed animal-related requests: 6,288 total
- Categories: Animal cruelty/neglect, noise complaints, loose animals
- Adoption mentions: Only 18 out of 169,598 (0.01%)
- Conclusion: Dataset is about complaints, not adoption services

**Q4: "Do we know the source of each 311 row? As in phone, email, etc?"**
- Analyzed source field (column 10 in raw CSV)
- 106,627 records (62.9%): "Call Center" (phone)
- 73,262 records (43.2%): Empty/blank
- 762 records: "Smell My City User" (mobile app)
- Remainder: Mixed/unclear data
- Conclusion: Source field is poorly structured, mostly phone or unknown

**Q5: "Can you distill the source or understand the empty blank fields from something else like NER? Also have you considered the source as signal for contact method? What are the bottlenecks we can solve from the phone center call?"**
- **Source Inference from NER:** Only 821 records (1.3% of blanks) had contact method clues
  - Web: 430, Phone: 292, Email: 72, Mobile: 27
- **Source as Signal:** Yes! 62.9% use call center (expensive channel), revealing massive self-service opportunity
- **Call Center Bottlenecks:** 3 major bottlenecks identified:
  1. NSR (48.4%) - Information requests → FAQ/Chatbot solution
  2. Waste Management (14.9%) - Cart orders/missed pickups → Online ordering/tracking
  3. Status Checks (49.4%) - "Where's my request?" → Self-service portal
- **Business Case:** Can reduce call volume by 56.3%, save $125K/year

**Q6: "Put this in the same folder as possible business opportunities"**
- Copied analysis files to report package directory
- Created BUSINESS_OPPORTUNITIES.md and DOCX
- Added BOTTLENECK_ANALYSIS_REPORT.md for technical details
- Included all Python analysis scripts
- Updated README.txt with new content

**Q7: "I want a FastHTML web app that can serve a dashboard to let people understand what we have. This agent has lots of sample code [Zendesk CLAUDE.md]"**
- Built complete FastHTML dashboard (dashboard_app.py)
- 6 pages: Overview, Call Center, Topics, Sentiment, Urgency, Business
- Interactive Plotly charts (sentiment pie, urgency bar, top services, topics)
- Bootstrap 5 styling with gradient navigation
- One-click launcher script (start_dashboard.sh)
- Complete documentation (README_DASHBOARD.md)
- Ready for deployment to Render/Heroku/Railway

---

## Research Findings

### Call Center Analysis Results

**Source Distribution:**
- Call Center: 106,631 (62.9%)
- Unknown: 73,262 (43.2%)
- Smell My City: 762 (0.4%)
- Other: ~5,947 (mixed data)

**Source Inference from NER:**
- Total blank source fields: 62,967 (37.1%)
- NER found contact clues: 821 (1.3%)
- Web mentions: 430 (52.4% of clues)
- Phone numbers: 292 (35.6% of clues)
- Email addresses: 72 (8.8% of clues)
- Mobile/app: 27 (3.3% of clues)

**Call Center Volume Breakdown:**
| Service Type | Annual Calls | % of Total |
|-------------|--------------|------------|
| NSR Metro Agencies | 34,981 | 32.8% |
| Streets | 6,839 | 6.4% |
| NSR Social Services | 6,075 | 5.7% |
| Solid Waste Container | 5,993 | 5.6% |
| Solid Waste Missed | 5,225 | 4.9% |

**Urgency Distribution:**
- Low: 72,132 (67.6%)
- Medium: 21,311 (20.0%)
- High: 12,937 (12.1%)

**Sentiment Distribution:**
- Neutral: 61,332 (57.5%)
- Negative: 42,911 (40.2%)
- Positive: 116 (0.1%)

**Systemic Bottlenecks (High Urgency + Negative):**
- Total: 11,765 calls (11.0%)
- Top agencies: C&R Property Maintenance (804), Animal Services (803), LMPD (277)

**Self-Service Potential:**
- Low/medium urgency: 72,892 calls (68.4%)
- Neutral + low/med urgency: 60,625 calls (56.9%)
- Empty/minimal descriptions: 52,646 calls (49.4%)

**NSR Deep Dive:**
- Total NSR calls: 51,557 (48.4% of call center volume)
- Sentiment: 99.9% neutral
- Urgency: 99.7% low
- Description quality: Only 0.5% have meaningful descriptions
- Examples: "Advised it is collected every other week", "Garbage cart was stolen", "Called to report garbage was missed"

### Animal Services Analysis Results

**Total Animal Requests: 6,288**
- Main categories: Cruelty/neglect, noise complaints, loose animals
- NOT adoption services - enforcement/complaint focused

**Adoption Mentions: 18 total (0.01%)**
- Most are referrals to Metro Animal Services
- Dataset does not track adoption questions

**Source Field Analysis:**
- Field is poorly structured
- Primarily "Call Center" or empty
- Does not reliably track digital vs phone channels
- Recommendation: Improve data collection for source tracking

---

## Technical Details

### NLP Pipeline Architecture

**Processing Script:** `process_311_parallel_checkpoint.py`
- Async processing with 20 concurrent requests
- Checkpoint/resume support for fault tolerance
- Saves progress every 10 batches (1,000 records)

**NLP Tasks (all async/concurrent):**
1. **Sentiment Analysis** - positive/negative/neutral classification
2. **Urgency Classification** - level (low/med/high) + score (0-10)
3. **Named Entity Recognition** - locations, dates, people, organizations
4. **Topic Extraction** - primary topics with keywords
5. **Aspect-Based Sentiment** - granular sentiment per aspect

**Model:** Claude Sonnet 4.5 via OpenRouter API
- Temperature: 0 (deterministic)
- Response format: JSON for structured outputs
- Prompts: Located in `nlp311/nlp/prompts.py`

**Topic Modeling (post-processing):**
- LDA (Latent Dirichlet Allocation): 15 topics
- NMF (Non-negative Matrix Factorization): 15 topics
- Coherence scoring for quality assessment

### Data Quality

**Success Rates:**
- Sentiment: 97.3% (164,992/169,598)
- Urgency: 99.7% (169,089/169,598)
- NER: 99.6% (168,920/169,598)
- ABSA: 77.2% (130,965/169,598) - lower due to complexity

**Edge Cases:**
- Empty descriptions: Skipped NLP processing
- Malformed JSON: Retry logic with JSON repair
- API timeouts: Exponential backoff with retries

### Performance Metrics

**Runtime:** 13 hours 33 minutes
- Average: 0.29 seconds per record
- 20 concurrent requests maintained throughout
- Checkpoint saved every 1,000 records

**Cost Breakdown:**
- Total API calls: 848,042
- Total cost: $998
- Per-record cost: $0.0059
- Per-task cost: ~$0.0012 (5 tasks per record)

**Infrastructure:**
- OpenRouter API gateway
- Claude Sonnet 4.5 model
- Async Python with asyncio
- PostgreSQL for checkpoint storage

---

## Dashboard Technical Details

### FastHTML Architecture

**Framework:** FastHTML (https://fastht.ml)
- Server-side rendering
- Component-based UI
- Built-in routing
- Starlette backend

**Dependencies:**
```
fasthtml>=0.6.0
pandas>=2.0.0
plotly>=5.18.0
uvicorn>=0.24.0
```

**Key Components:**
```python
# App setup
app, rt = fast_app(hdrs=(...))

# Navigation
def create_nav(current_page=None)
    # Bootstrap nav with gradient background

# Routes
@rt('/')  # Overview
@rt('/call-center')  # Call center analysis
@rt('/business')  # Business opportunities

# Charts
create_sentiment_pie()  # Plotly donut chart
create_urgency_bar()  # Plotly bar chart
create_top_services_bar()  # Horizontal bar
create_topic_wordcloud()  # Topic visualization
```

**Styling:**
- Bootstrap 5 for layout
- Custom gradient navigation
- Plotly for interactive charts
- Responsive design (mobile-friendly)

**Performance:**
- Data loaded on startup: ~2 seconds (168MB CSV)
- Page render: <100ms after data loaded
- Charts: Client-side Plotly rendering
- Memory: ~500MB with full dataset

**Deployment Options:**
- Render.com (recommended - free tier available)
- Heroku
- Railway
- Fly.io
- Internal server

---

## Next Steps & Opportunities

### Immediate (This Week)
1. **Deploy dashboard** to Render.com for stakeholder access
2. **Manual testing** of dashboard across different browsers
3. **Add authentication** (optional) for public deployment

### Short Term (1-2 Weeks)
4. **Geographic heat maps** - Leaflet/Mapbox integration
   - Illegal dumping hot spots
   - Street lighting dark zones
   - Complaint density by neighborhood
5. **Temporal analysis** - Time series trends
   - Seasonality patterns
   - Day of week/hour patterns
   - Year-over-year comparisons
6. **Agency deep dives** - Performance metrics per agency
   - Response time analysis
   - Resolution rates
   - Repeat request patterns

### Medium Term (1 Month)
7. **Predictive models** - ML forecasting
   - High-volume period prediction
   - Resource allocation optimization
   - Proactive issue identification
8. **API endpoints** - REST API for programmatic access
9. **Export functionality** - Download charts as PNG/PDF
10. **Search functionality** - Full-text search across descriptions

### Long Term (2-3 Months)
11. **Real-time integration** - Live data updates
12. **Mobile app** - Native iOS/Android for field reporting
13. **Citizen portal** - Public-facing self-service
14. **Integration testing** - Connect with existing Louisville Metro systems

### Self-Service Portal Features (Call Center Reduction)
**Phase 1 (0-3 months):**
- FAQ page with top 20 NSR topics
- Waste collection schedule lookup by address
- Basic IVR for common questions

**Phase 2 (3-6 months):**
- Web portal for service request submission
- Mobile app with GPS-enabled reporting
- Chatbot for 24/7 automated assistance
- Online cart ordering/replacement
- Status tracking dashboard

**Phase 3 (6-12 months):**
- SMS/email notification system
- Proactive missed pickup alerts
- Predictive issue identification
- Community dashboards by neighborhood

---

## Meta Lessons Learned

### FastHTML Dashboard Development
**Success:** Leveraged existing Zendesk annotation app patterns
- Same framework (FastHTML) reduces learning curve
- Bootstrap 5 for consistent professional styling
- Plotly integration for interactive charts
- Component-based approach for maintainability

**Key Learning:** Reusing proven architecture patterns accelerates development
- Navigation component reused from Zendesk app
- Chart generation follows same pattern
- Route structure mirrors annotation app
- One-click launcher script for easy testing

### Data Analysis Insights
**Discovery:** Source field analysis revealed business opportunity
- Original question: "Do we know the source?"
- Finding: 62.9% use call center, 43.2% unknown
- Insight: This is a signal, not just metadata
- Outcome: Identified $125K savings opportunity

**Key Learning:** Always ask "what does this tell us about behavior?"
- Metadata fields can reveal user preferences
- High call center usage = opportunity for self-service
- Data gaps (blank sources) indicate collection issues

### NER for Metadata Enrichment
**Experiment:** Can NER fill in blank source fields?
- Attempted to infer contact method from entities
- Result: Only 1.3% coverage (821 of 62,967 blanks)
- Finding: NER finds contact details but not original channel

**Key Learning:** NER is supplementary, not a substitute for proper data collection
- Named entities != data provenance
- Improve source tracking at intake
- Don't rely on inference for critical metadata

### Business Impact Communication
**Success:** Translated technical findings into business value
- Sentiment analysis → Customer satisfaction issues
- Urgency classification → Resource allocation gaps
- Topic modeling → Strategic priorities
- NSR analysis → $125K cost savings opportunity

**Key Learning:** Always connect data to dollars and decisions
- Every insight should have an action
- Quantify impact in financial terms
- Provide concrete implementation roadmap
- Make recommendations specific and measurable

---

## Session Recovery

If session crashes, read this file (CLAUDE.md) and:

1. **Check Current Status** section above for latest state
2. **Review Key Files** section for locations of all deliverables
3. **Quick Commands** for running dashboard or analysis scripts
4. **Data Schema** for understanding CSV structure
5. **Next Steps** for continuation priorities

**Key Locations:**
- Report package: `/Users/rachael/Downloads/311_nlp_analysis_report/`
- Data files: `/Users/rachael/Documents/projects/rachaelroland/pipelines/pipelines/311/`
- Dashboard: `dashboard_app.py` in report package
- Processing script: `process_311_parallel_checkpoint.py` in pipeline directory

**Quick Resume:**
```bash
# Launch dashboard
cd /Users/rachael/Downloads/311_nlp_analysis_report
./start_dashboard.sh

# View reports
open Louisville_311_NLP_Analysis_Report.docx
open BUSINESS_OPPORTUNITIES.docx

# Run analysis
cd /Users/rachael/Documents/projects/rachaelroland/pipelines/pipelines/311/analysis
uv run python call_center_bottleneck_analysis.py
```

---

## Related Projects

### Zendesk NLP Analysis (Applied Industrials/Lucifer)
**Location:** `/Users/rachael/Documents/projects/roar_appliedindustrials/lucifer/projects/zendesk/`
**Context:** See `CLAUDE.md` in that directory
**Similarities:**
- FastHTML web application framework
- NLP analysis with Claude Sonnet 4.5
- Interactive dashboards with Plotly
- PostgreSQL database backend
- Annotation system for model improvement

**Key Differences:**
- Zendesk: 5,841 support tickets
- 311: 169,598 service requests
- Zendesk: Customer support optimization
- 311: Municipal service improvement

**Shared Learnings:**
- FastHTML patterns for rapid dashboard development
- Chart generation and interactivity
- Navigation and routing structure
- Deployment to Render.com

---

*Auto-generated for Claude Code context*
*Last updated: February 1, 2026 - 10:00 AM MT*
