# Louisville Metro 311 Call Center Bottleneck Analysis
**Date:** February 1, 2026
**Dataset:** 2024 Louisville Metro 311 Service Requests (169,598 records)
**Call Center Volume:** 106,631 requests (62.9% of total)

---

## Executive Summary

This analysis identifies **critical bottlenecks** in the Louisville Metro 311 call center and provides **actionable recommendations** to reduce call volume by **up to 68%** through self-service automation, improved information access, and proactive notifications.

### Key Findings

1. **48.4% of call center volume** (51,557 calls) are **NSR (Non-Service Request)** categories - primarily information requests and referrals that could be handled through web/app self-service

2. **87.6% of calls** (93,443) are **low or medium urgency**, indicating most callers don't need immediate human assistance

3. **56.9% of calls** (60,625) have **neutral sentiment and low/medium urgency** - these are routine, informational requests perfect for self-service

4. **49.4% of calls** (52,646) have **empty or minimal descriptions**, suggesting they are simple status checks or basic requests

5. Only **11.0%** (11,765) are **high urgency + negative sentiment** - these are the calls that truly need human intervention

---

## Task 1: Source Inference from NER Entities

### Blank Source Field Analysis

- **62,967 records (37.1%)** have blank source fields
- **NER analysis found contact clues in 821 records:**
  - **Web:** 430 records (52.4%)
  - **Phone:** 292 records (35.6%)
  - **Email:** 72 records (8.8%)
  - **Mobile:** 27 records (3.3%)

### Implications

While only 1.3% of blank source records could be inferred from NER entities, this suggests:
- Many requests lack detailed contact information in descriptions
- Web/app-based submissions are underutilized
- Better structured data collection could improve routing and analytics

---

## Task 2: Call Center Bottleneck Analysis

### 2.1 Most Common Service Types (Top 10)

| Rank | Service Type | Volume | % of CC Volume |
|------|--------------|--------|----------------|
| 1 | **NSR Metro Agencies** | 34,981 | 32.8% |
| 2 | Streets | 6,839 | 6.4% |
| 3 | **NSR Social Services** | 6,075 | 5.7% |
| 4 | **Solid Waste Container Request** | 5,993 | 5.6% |
| 5 | **Solid Waste Missed Services** | 5,225 | 4.9% |
| 6 | **NSR Miscellaneous** | 4,488 | 4.2% |
| 7 | Exterior | 3,850 | 3.6% |
| 8 | **NSR Government** | 3,682 | 3.5% |
| 9 | Animal Issue | 3,335 | 3.1% |
| 10 | High Weeds/Grass | 3,171 | 3.0% |

**Bold** = Self-service candidates

#### Top Topics from NLP Analysis

1. **Metro Transit Services** - 34,736 mentions
2. **Waste Management** - 18,563 mentions
3. **Government Agencies** - 16,534 mentions
4. Public Safety - 14,198 mentions
5. Property Maintenance - 12,844 mentions

### 2.2 Urgency Distribution

| Urgency Level | Count | Percentage |
|--------------|-------|------------|
| **LOW** | 72,132 | **67.6%** |
| **MEDIUM** | 21,311 | **20.0%** |
| HIGH | 12,937 | 12.1% |
| Blank/Other | 251 | 0.2% |

**Key Insight:** **87.6% of calls are low or medium urgency** - these don't require immediate human intervention.

#### High Urgency Service Types (Top 5)

1. Streets - 2,155 (16.7%)
2. Interior - 1,653 (12.8%)
3. Exterior - 1,508 (11.7%)
4. Traffic Signals - 1,297 (10.0%)
5. Trees - 1,112 (8.6%)

### 2.3 Sentiment Distribution

| Sentiment | Count | Percentage |
|-----------|-------|------------|
| **NEUTRAL** | 61,332 | **57.5%** |
| NEGATIVE | 42,911 | 40.2% |
| POSITIVE | 116 | 0.1% |
| Blank | 2,272 | 2.1% |

**Key Insight:** Over half of calls have neutral sentiment, suggesting informational/routine nature.

#### Negative Sentiment Service Types (Top 5)

1. Streets - 5,055 (11.8%)
2. Solid Waste Missed Services - 4,764 (11.1%)
3. Exterior - 3,536 (8.2%)
4. Animal Issue - 2,952 (6.9%)
5. Parking Concern - 2,776 (6.5%)

### 2.4 Agency Volume Distribution

| Agency | Call Volume | % |
|--------|-------------|---|
| LMPD | 2,255 | 2.1% |
| C&R Property Maintenance Enforcement | 1,925 | 1.8% |
| Louisville Animal Services | 1,912 | 1.8% |
| Parking Authority River City | 930 | 0.9% |
| Public Works Electrical Maint | 801 | 0.8% |

**Note:** Most NSR calls (51,557) have no agency assignment, as they are referrals/information requests.

### 2.5 Systemic Bottlenecks: High Urgency + Negative Sentiment

**11,765 calls (11.0%)** represent true bottlenecks requiring human intervention.

#### Top Service Types (Bottleneck Calls)

| Service Type | Count | % of Bottlenecks |
|--------------|-------|------------------|
| Streets | 1,949 | 16.6% |
| Interior | 1,644 | 14.0% |
| Exterior | 1,476 | 12.5% |
| Traffic Signals | 1,014 | 8.6% |
| Trees | 977 | 8.3% |
| Animal Issue | 963 | 8.2% |

#### Top Agencies (Bottleneck Calls)

1. C&R Property Maintenance Enforcement - 804 (6.8%)
2. Louisville Animal Services - 803 (6.8%)
3. LMPD - 277 (2.4%)
4. APCD Community Compliance - 171 (1.5%)
5. Public Works Electrical Maint - 109 (0.9%)

---

## Task 3: Actionable Bottleneck Findings

### 3.1 NSR Deep Dive: The Biggest Opportunity

**NSR (Non-Service Request) categories account for 48.4% of call center volume** (51,557 calls).

#### NSR Category Breakdown

| Category | Volume | % of NSR | Characteristics |
|----------|--------|----------|-----------------|
| **NSR Metro Agencies** | 34,981 | 67.8% | 99.9% neutral, 99.7% low urgency |
| **NSR Social Services** | 6,075 | 11.8% | 99.9% neutral, 99.4% low urgency |
| **NSR Miscellaneous** | 4,488 | 8.7% | 99.6% neutral, 99.4% low urgency |
| **NSR Government** | 3,682 | 7.1% | 99.9% neutral, 99.5% low urgency |
| **NSR Utility** | 1,699 | 3.3% | 99.7% neutral, 99.3% low urgency |
| NSR Severe Weather | 332 | 0.6% | 93.7% negative, 94.3% high urgency |

#### What Are NSR Metro Agencies Calls?

Sample descriptions reveal these are primarily:
- **Garbage/recycling collection questions** ("Advised it is collected every other week")
- **Cart replacement requests** ("garbage cart was stolen")
- **Status checks** ("called to report the garbage was missed")
- **Service guidelines** ("Was advised the guidelines for collection")
- **Referrals to other departments** ("Phone number given to Solid Waste")
- **General information requests** ("Question about free radon test kit")

**Critical Insight:** Only **0.5%** of NSR Metro Agencies calls have meaningful descriptions. This suggests they are brief, routine inquiries that could be handled by:
- Automated phone system (IVR)
- Web-based self-service portal
- Mobile app
- Chatbot
- FAQ database

### 3.2 Prime Candidates for Self-Service

**93,443 calls (87.6%)** are low or medium urgency.

#### Top 10 Self-Service Candidates

| Service Type | Volume | % of CC | Urgency Breakdown |
|--------------|--------|---------|-------------------|
| NSR Metro Agencies | 34,888 | 32.7% | 99.9% low |
| NSR Social Services | 6,055 | 5.7% | 99.5% low |
| Solid Waste Container Request | 5,968 | 5.6% | 84.8% low, 15.1% med |
| Solid Waste Missed Services | 5,157 | 4.8% | 57.0% low, 43.0% med |
| Streets | 4,671 | 4.4% | 83.6% med, 16.4% low |
| NSR Miscellaneous | 4,472 | 4.2% | 99.7% low |
| NSR Government | 3,664 | 3.4% | 99.9% low |
| High Weeds/Grass | 2,910 | 2.7% | 79.5% low, 20.5% med |
| Parking Concern | 2,771 | 2.6% | 62.6% low, 37.4% med |
| Animal Issue | 2,336 | 2.2% | 81.0% med, 19.0% low |

**Potential Impact: 72,892 calls (68.4%) could be moved to self-service**

### 3.3 Routine Services (Neutral + Low/Medium Urgency)

**60,625 calls (56.9%)** are neutral sentiment AND low/medium urgency.

#### Top 10 Routine Services

1. NSR Metro Agencies - 34,862 (57.5%)
2. NSR Social Services - 6,053 (10.0%)
3. NSR Miscellaneous - 4,460 (7.4%)
4. NSR Government - 3,663 (6.0%)
5. Solid Waste Container Request - 3,080 (5.1%)
6. NSR Utility - 1,688 (2.8%)
7. Large Item Appointment - 1,387 (2.3%)
8. Streets - 1,354 (2.2%)
9. Street Signs - 452 (0.7%)
10. Sidewalks/Curbs - 367 (0.6%)

**Recommendation:** Create comprehensive FAQ/knowledge base for these topics.

**Potential Impact: 57,366 calls (53.8%) could be deflected with better information**

### 3.4 Empty/Minimal Descriptions: Simple Requests

**52,646 calls (49.4%)** have empty or minimal descriptions (< 20 characters).

This strongly suggests:
- Simple status checks
- Basic appointment scheduling
- Quick information lookups
- Cart/container requests

#### Top Services with Empty Descriptions

1. NSR Metro Agencies - 34,844 (66.2%)
2. NSR Social Services - 6,049 (11.5%)
3. NSR Miscellaneous - 4,392 (8.3%)
4. NSR Government - 3,635 (6.9%)
5. NSR Utility - 1,687 (3.2%)
6. Large Item Appointment - 829 (1.6%)

**Recommendation:** These are perfect candidates for automation (IVR, chatbot, web forms).

### 3.5 Repeat Callers: Proactive Notification Opportunity

**5,538 addresses** made repeat calls for the same service type, totaling **13,537 calls**.

#### Top Repeat Service Patterns

| Service Type | Repeat Calls | # Addresses | Avg per Address |
|--------------|--------------|-------------|-----------------|
| Solid Waste Container Request | 2,334 | 1,080 | 2.2 |
| Solid Waste Missed Services | 2,317 | 880 | 2.6 |
| Exterior | 1,278 | 506 | 2.5 |
| High Weeds/Grass | 1,102 | 447 | 2.5 |
| Streets | 974 | 414 | 2.4 |
| Animal Issue | 833 | 313 | 2.7 |
| Trash | 646 | 264 | 2.4 |
| Parking Concern | 551 | 242 | 2.3 |
| Interior | 468 | 197 | 2.4 |
| Maintenance | 399 | 69 | **5.8** |

**Key Insights:**
- Maintenance issues average 5.8 calls per address - systemic problem
- Waste collection services have highest repeat volume
- Opportunity for proactive alerts (e.g., "Your garbage collection was missed")

**Recommendation:** Implement proactive notification system to reduce follow-up calls.

---

## Summary: Key Recommendations to Reduce Call Center Load

### Recommendation 1: Implement Self-Service Portal/App
**Potential Impact: 72,892 calls (68.4% reduction)**

**Priority Services:**
1. NSR Metro Agencies (34,888 calls) - Information requests, referrals
2. NSR Social Services (6,055 calls) - Resource lookups, referrals
3. Solid Waste Container Request (5,968 calls) - Cart ordering/replacement
4. Solid Waste Missed Services (5,157 calls) - Report missed pickup
5. Streets (4,671 calls) - Pothole/street issue reporting

**Features to Build:**
- Service request submission forms
- Status tracking/lookup by address or SR number
- Garbage/recycling schedule lookup by address
- Cart ordering/replacement requests
- Department contact directory
- Service guidelines and FAQs

### Recommendation 2: Create Comprehensive FAQ/Knowledge Base
**Potential Impact: 57,366 calls (53.8% reduction)**

**Priority Topics:**
1. Waste collection schedules and guidelines
2. Social services resources and referrals
3. Government agency contact information
4. Utility service information
5. Large item pickup procedures
6. Street maintenance procedures

**Channels:**
- Website
- Mobile app
- Automated phone system (IVR)
- Chatbot

### Recommendation 3: Proactive Notifications System
**Potential Impact: 13,537 calls (12.7% reduction)**

**Use Cases:**
- Alert residents when garbage collection is missed
- Notify about service delays
- Send reminders before large item pickup appointments
- Update residents on status of their service requests
- Alert about recurring issues in their area

**Delivery Methods:**
- SMS/text messages
- Email
- Push notifications (mobile app)
- Automated phone calls

### Recommendation 4: Enhanced IVR System
**Potential Impact: 52,646 calls (49.4% reduction)**

Since 49.4% of calls have minimal/no descriptions, implement:
- Speech recognition for common requests
- Automated status lookup by address
- Appointment scheduling automation
- Cart ordering automation
- Transfer to web/app for complex issues

### Recommendation 5: Focus Call Center on High-Impact Issues
**11,765 calls (11.0%) truly need human intervention**

**Priority Support Areas:**
1. C&R Property Maintenance Enforcement (804 high-priority calls)
2. Louisville Animal Services (803 high-priority calls)
3. LMPD (277 high-priority calls)
4. APCD Community Compliance (171 high-priority calls)

**Staff Optimization:**
- Train agents for complex issues
- Reduce time on routine inquiries
- Improve first-call resolution for urgent issues

---

## Implementation Priorities

### Phase 1: Quick Wins (0-3 months)
1. **Enhanced IVR system** - Handle basic lookups and status checks
2. **FAQ page** - Document top 50 most common questions
3. **Email notifications** - Automated updates for service requests

**Expected Impact: 20-30% call reduction**

### Phase 2: Self-Service Platform (3-6 months)
1. **Web portal** - Service request submission and tracking
2. **Mobile app** - On-the-go service requests
3. **Chatbot** - Automated question answering
4. **Waste collection schedule lookup** - By address

**Expected Impact: 40-50% call reduction**

### Phase 3: Proactive Engagement (6-12 months)
1. **SMS/text notifications** - Missed pickups, status updates
2. **Predictive analytics** - Identify repeat callers proactively
3. **Automated follow-ups** - Status updates without call prompts
4. **Community dashboards** - Show service issues by neighborhood

**Expected Impact: 50-68% call reduction**

---

## Measurement & Success Metrics

### Key Performance Indicators

1. **Call Volume Reduction**
   - Target: 50% reduction in 12 months
   - Track by service type and urgency level

2. **Self-Service Adoption**
   - Target: 60% of requests via web/app/IVR
   - Track by channel (web, app, phone, IVR)

3. **First Call Resolution**
   - Target: 80% for high-urgency calls
   - Measure time to resolution

4. **Customer Satisfaction**
   - Target: 90% satisfaction for self-service
   - Survey all channels

5. **Repeat Call Rate**
   - Target: 50% reduction in repeat calls
   - Track by address and service type

### Monthly Tracking

- Call volume by source (Call Center vs. Web/App)
- Top 20 service types by volume
- Urgency and sentiment distributions
- Repeat caller patterns
- Average handle time for call center

---

## Appendix: Data Sources

- **Processed CSV:** `/Users/rachael/Documents/projects/rachaelroland/pipelines/pipelines/311/data/processed/311_processed_with_nlp.csv`
- **Raw CSV:** `/Users/rachael/Documents/projects/rachaelroland/pipelines/pipelines/311/data/raw/louisville_311_2024.csv`
- **Analysis Scripts:**
  - `/Users/rachael/Documents/projects/rachaelroland/pipelines/pipelines/311/analysis/call_center_bottleneck_analysis.py`
  - `/Users/rachael/Documents/projects/rachaelroland/pipelines/pipelines/311/analysis/nsr_deep_dive.py`

**Total Records Analyzed:** 169,598
**Call Center Records:** 106,631 (62.9%)
**Date Range:** January 1, 2024 - December 31, 2024
