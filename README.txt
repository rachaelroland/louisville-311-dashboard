LOUISVILLE METRO 311 NLP ANALYSIS - REPORT PACKAGE
==================================================

Generated: February 1, 2026
Analysis: 169,598 Louisville Metro 311 Service Requests (2024)

CONTENTS:
---------

=== TECHNICAL ANALYSIS ===

1. Louisville_311_NLP_Analysis_Report.docx (32KB)
   - Main report in Microsoft Word format
   - Includes executive summary, findings, recommendations
   - Fully formatted with sections and structure

2. Louisville_311_NLP_Analysis_Report.md (39KB)
   - Same report in Markdown format
   - For version control and text editing

3. 311_nlp_results.json (19KB)
   - Topic modeling results (LDA + NMF)
   - 15 topics each with keywords and weights
   - Coherence scores and metadata

=== BUSINESS OPPORTUNITIES ===

4. BUSINESS_OPPORTUNITIES.md (15KB) **NEW**
   - Executive summary for leadership
   - Call center bottleneck analysis
   - ROI projections: $125K annual savings
   - 3-phase implementation roadmap
   - Self-service automation opportunities

5. BUSINESS_OPPORTUNITIES.docx (12KB) **NEW**
   - Same content in Microsoft Word format
   - Ready for executive presentation

6. BOTTLENECK_ANALYSIS_REPORT.md (14KB) **NEW**
   - Complete technical deep-dive
   - Source inference from NER analysis
   - Call center volume breakdown by service type
   - Urgency and sentiment distributions
   - Actionable automation recommendations

=== ANALYSIS SCRIPTS ===

7. call_center_bottleneck_analysis.py (15KB)
   - Main bottleneck analysis script
   - Analyzes source, urgency, sentiment patterns

8. nsr_deep_dive.py (4.9KB)
   - Deep analysis of NSR categories
   - Sample descriptions and patterns

9. generate_summary_stats.py (5.8KB)
   - Quick statistics generator
   - Action plan with impact projections

=== INTERACTIVE DASHBOARD ===

10. dashboard_app.py (20KB) **NEW**
    - FastHTML web application
    - Interactive visualizations (Plotly charts)
    - Multiple pages: Overview, Call Center, Business Opportunities
    - Run: uv run python dashboard_app.py

11. requirements.txt **NEW**
    - Python dependencies for dashboard
    - Install: uv pip install -r requirements.txt

12. README_DASHBOARD.md **NEW**
    - Complete dashboard documentation
    - Setup instructions and customization guide

13. README.txt (this file)
    - Package contents and data locations

FULL DATASET LOCATION:
----------------------
The complete 168MB processed CSV with all 169,598 records is located at:
/Users/rachael/Documents/projects/rachaelroland/pipelines/pipelines/311/data/processed/311_processed_with_nlp.csv

This CSV contains:
- All original 311 data fields
- Sentiment classifications
- Urgency levels and scores
- Named entities (JSON)
- Topics extracted (JSON)
- Aspect-based sentiment analysis (JSON)

KEY FINDINGS (EXECUTIVE SUMMARY):
---------------------------------

SENTIMENT:
- 55% Neutral (90,163 requests)
- 45% Negative (74,616 requests)
- <1% Positive (261 requests)

TOP ISSUES:
1. Illegal Dumping Crisis (16.6% topic weight) - IMMEDIATE ACTION REQUIRED
2. Missed Service Collections (15.3% topic weight) - SERVICE RELIABILITY PROBLEM
3. Street Lighting Failures (18.9% topic weight) - INFRASTRUCTURE DECAY
4. Waste Management (30-35% of all requests) - LARGEST CATEGORY
5. Parking Violations (10-15% of requests)

PROCESSING STATS:
- Runtime: 13 hours 33 minutes
- API Calls: 848,042 total
- Cost: $998 ($0.0059 per record)
- Success Rate: 99.7% urgency, 97.3% sentiment, 99.6% NER

BUSINESS OPPORTUNITIES (CALL CENTER):
-------------------------------------

CURRENT STATE:
- 106,631 calls/year (62.9% of all 311 requests)
- $222,150 annual cost in agent time
- 48.4% are simple information requests (NSR)
- 87.6% are low/medium urgency

OPPORTUNITY:
- Reduce call volume by 56.3% (60,035 calls)
- Save $125,075/year in agent time
- Improve customer satisfaction with 24/7 self-service
- Focus agents on 11,765 truly urgent calls (11%)

TOP BOTTLENECKS TO AUTOMATE:
1. NSR Metro Agencies (34,981 calls) - Info requests, referrals
2. Solid Waste Container (5,993 calls) - Cart ordering
3. Solid Waste Missed (5,225 calls) - Pickup complaints
4. NSR Social Services (6,075 calls) - Resource lookups

3-PHASE IMPLEMENTATION:
Phase 1 (0-3 months): FAQ + IVR → 15,467 calls saved (14.5%)
Phase 2 (3-6 months): Self-service portal → 36,446 calls saved (34.2%)
Phase 3 (6-12 months): Proactive alerts → 8,122 calls saved (7.6%)

RECOMMENDATIONS:
1. Launch anti-dumping task force in identified hot spot alleys
2. Implement GPS tracking for waste collection vehicles
3. Priority street lighting repairs in dark zones
4. Deploy geographic heat maps for resource allocation
5. Create predictive models for high-volume periods
6. Build self-service portal for routine requests **NEW**
7. Implement chatbot for FAQ and information lookups **NEW**
8. Deploy proactive SMS/email notifications for service updates **NEW**

FOR MORE INFORMATION:
--------------------
Technical Analysis:
- See Louisville_311_NLP_Analysis_Report.docx for detailed topic modeling,
  geographic analysis, agency performance metrics, data visualization,
  technical methodology, and complete findings

Business Opportunities:
- See BUSINESS_OPPORTUNITIES.docx for executive summary, ROI analysis,
  implementation roadmap, and cost-benefit projections
- See BOTTLENECK_ANALYSIS_REPORT.md for complete technical details

Interactive Dashboard:
- Run: uv run python dashboard_app.py
- Visit: http://localhost:5002
- Features: Interactive charts, call center analysis, business opportunities
- See README_DASHBOARD.md for complete setup and customization guide

Questions? Contact the data analysis team.
