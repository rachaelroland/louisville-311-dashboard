# API Automation Research: Louisville Metro311
## Can We Automate Service Request Submission?

**Date:** February 19, 2026
**Question:** Can the AI agent directly submit service requests to Metro311 instead of directing users to call 311?

---

## TL;DR - YES, API Integration is Possible

✅ **Louisville Metro311 has API capabilities**
✅ **Accela platform supports programmatic access**
✅ **Louisville adheres to Open311 standards**
⚠️ **BUT: Need API credentials and technical integration**

---

## What We Know

### 1. Louisville Uses Accela Civic Platform

Louisville Metro's 311 system is powered by **[Accela](https://louisvilleky.gov/government/metro-technology-services/accela)**, a major civic engagement platform.

**Key Facts:**
- [Accela launched in Louisville](https://louisvilleky.gov/news/louisville-metro-government-launches-new-accela-business-customer-portals) with new Business Portal, Metro311 Online Portal, and mobile app
- Service requests route directly to appropriate City Departments via Accela
- Mobile app package ID: `com.accela.louisville_ky`
- System supports automated workflows and routing

**Sources:**
- [Accela on LouisvilleKY.gov](https://louisvilleky.gov/government/metro-technology-services/accela)
- [Louisville Metro Government launches new Accela portals](https://louisvilleky.gov/news/louisville-metro-government-launches-new-accela-business-customer-portals)

---

### 2. Accela Has Full REST API

Accela provides a comprehensive REST API for programmatic access:

**[Accela Civic Platform API Documentation](https://developer.accela.com/docs/construct-civicPlatformAndConstructApi.html)**

**Capabilities:**
- ✅ Create service requests programmatically
- ✅ Update request status
- ✅ Query existing requests
- ✅ Attach photos/documents
- ✅ Get service definitions and codes
- ✅ OAuth2 authentication via CivicID

**SDKs Available:**
- iOS, Android, .NET, Windows, PHP, Node.js, Ruby

**API Methods:**
- `POST /records` - Create new service requests
- `GET /records/{id}` - Get request details
- `PUT /records/{id}` - Update requests
- `GET /services` - List available service types

**Sources:**
- [The Civic Platform and the Accela API](https://developer.accela.com/docs/accela_construct_api_developers_guide/overview/the_civic_platform_and_the_construct_api.htm)
- [Accela Civic Platform](https://www.accela.com/civic-platform/)

---

### 3. Louisville Adheres to Open311 Standards

Louisville's Metro311 system is based on **[Open311 GeoReport specification](https://wiki.open311.org/GeoReport_v2/)**.

**What is Open311?**
- Standardized API for civic issue tracking
- REST/JSON interface
- Supports service request creation, querying, and updates
- Used by hundreds of cities worldwide

**Louisville's Implementation:**
- Based on [proposed GeoReport Bulk specification](https://wiki.open311.org/GeoReport/bulk)
- Data adheres to Open311.org Data Standards
- Partnership with Center for Government Excellence

**Standard Open311 Endpoints:**
```
GET  /services.json                    # List available service types
GET  /services/{service_code}.json     # Get service definition
POST /requests.json                     # Create new service request
GET  /requests.json                     # Query service requests
GET  /requests/{service_request_id}.json # Get specific request
```

**Sources:**
- [Louisville Metro 311 Service Request 2025 (data.gov)](https://catalog.data.gov/dataset/louisville-metro-ky-metro-311-service-request-2025)
- [GeoReport v2 API Documentation](https://wiki.open311.org/GeoReport_v2/)

---

### 4. Data Available via ArcGIS REST API (Read-Only)

Louisville publishes 311 data through **ArcGIS FeatureServer** (read-only):

**Access Points:**
- [Louisville Metro Open Data Hub](https://louisville-metro-opendata-lojic.hub.arcgis.com/)
- ArcGIS services hosted at `services1.arcgis.com/79kfd2K6fskCAkyg/`
- Datasets include: Active permits, inspection results, 311 service requests

**Limitation:** These appear to be **read-only** endpoints for open data transparency, NOT for submitting new requests.

**Sources:**
- [Louisville Open Data Portal](https://louisvilleky.gov/government/metro-technology-services/services/open-data-portal)
- [ArcGIS REST APIs](https://developers.arcgis.com/rest/)

---

## What We Need

### To Enable AI-Automated Service Requests

#### 1. **API Access Credentials**
**Contact:** Louisville Metro Technology Services
- API key or OAuth2 credentials for Accela system
- Environment: Production vs. Sandbox/Test
- Rate limits and usage policies
- Service account setup

**Action:** Email/call Metro Technology Services requesting API access for AI assistant integration

#### 2. **API Endpoints & Documentation**
**Need to Know:**
- ✅ Accela API base URL for Louisville (e.g., `https://apis.accela.com/v4/louisville/`)
- ✅ OR Open311 endpoint (e.g., `https://311.louisvilleky.gov/open311/v2/`)
- ✅ Available service codes (waste collection, cart request, illegal dumping, etc.)
- ✅ Required fields for each service type
- ✅ Authentication method (API key vs OAuth2)

**Action:** Request Louisville-specific API documentation from Metro Tech Services

#### 3. **Service Type Mapping**
Map our Q&As to Accela/Open311 service codes:

| Q&A Category | Likely Service Code | Required Fields |
|--------------|---------------------|-----------------|
| Request new cart | `WASTE_CONTAINER_NEW` | Address, cart type (trash/recycling) |
| Report damaged cart | `WASTE_CONTAINER_DAMAGED` | Address, damage description |
| Report stolen cart | `WASTE_CONTAINER_STOLEN` | Address |
| Report missed pickup | `MISSED_WASTE_SERVICE` | Address, service type, date |
| Report illegal dumping | `ILLEGAL_DUMPING` | Location, description, photos? |

**Action:** Get official service code list from Louisville

#### 4. **Technical Integration**
Build API integration layer:

**Components Needed:**
- Authentication handler (OAuth2 or API key)
- Request builder (format AI conversation → API payload)
- Error handling and validation
- Response parser and confirmation messaging
- Logging and monitoring

**Workflow Example:**
```
User: "My trash cart was stolen"
AI: "I can help you report that. What's your address?"
User: "123 Main St, Louisville, KY 40202"
AI: [Validates address, builds API request]
    POST /requests.json
    {
      "service_code": "WASTE_CONTAINER_STOLEN",
      "address": "123 Main St",
      "city": "Louisville",
      "state": "KY",
      "zip": "40202",
      "description": "Trash cart stolen"
    }
AI: "Your stolen cart has been reported (Request #SR-12345).
    A replacement cart will be delivered within 7-10 business days."
```

**Development Time Estimate:** 2-4 weeks for full integration

---

## Options for Implementation

### Option A: Informational Only (Current Approach)
**What:** AI provides information and directs to Metro311 app/phone
**Pros:**
- No API integration needed
- Quick deployment
- No technical dependencies
**Cons:**
- User still has to make a second call/app interaction
- Not truly automated
- Doesn't address Oliver's feedback

### Option B: Partial Automation (Hybrid)
**What:** AI collects information, then submits via API
**Pros:**
- Better user experience - one-stop shop
- Reduces 311 call volume even more
- AI can validate data before submission
**Cons:**
- Requires API credentials and integration
- 2-4 weeks development time
- Need error handling for API failures
**Best For:** Transactional requests (cart orders, missed pickup reports)

### Option C: Full Automation + Smart Routing
**What:** AI decides when to auto-submit vs. escalate to human
**Pros:**
- Best user experience
- Maximum call deflection
- Can handle complex scenarios
**Cons:**
- Most complex to build
- Requires sophisticated decision logic
- Higher maintenance burden
**Best For:** Production-ready, long-term solution

---

## Recommended Approach

### Phase 1: Deploy Informational Q&As (Week 1)
- ✅ Use current Q&As as-is
- ✅ Provide information + direct to Metro311
- ✅ Get initial deflection value

### Phase 2: API Access & Testing (Weeks 2-3)
- 📧 Contact Metro Technology Services for API access
- 📋 Get service codes and documentation
- 🔧 Set up test environment
- ✅ Build proof-of-concept for 2-3 simple workflows

### Phase 3: Hybrid Automation (Weeks 4-6)
- 🤖 Implement API integration for high-volume, simple requests:
  - Cart requests (new, damaged, stolen)
  - Missed pickup reports
  - Maybe illegal dumping reports
- 📝 Keep informational answers for complex scenarios
- 🧪 Test with real users

### Phase 4: Full Automation (Month 2+)
- 🚀 Expand to more service types
- 🧠 Add smart routing logic
- 📊 Monitor and optimize

---

## Action Items - Next Steps

### Immediate (This Week)
1. **Deploy informational Q&As** as planned
   - Addresses Oliver's content feedback
   - Starts delivering value immediately
   - Sets baseline for comparison

2. **Contact Louisville Metro Technology Services**
   - Email: Request API access for AI assistant integration
   - Phone: Call 311 and ask for Metro Tech Services developer relations
   - Ask for:
     - Accela API credentials
     - Open311 endpoint (if available)
     - Service code documentation
     - Test environment access

### Short-term (Weeks 2-4)
3. **API Discovery & Testing**
   - Get API credentials
   - Build test integration for 1 service type (e.g., cart requests)
   - Validate with Louisville Metro team
   - Measure time savings vs. informational approach

4. **Decision Meeting with Oliver/Partner**
   - Show API automation proof-of-concept
   - Discuss investment vs. benefit
   - Decide which workflows to automate first
   - Set timeline for full implementation

### Medium-term (Months 2-3)
5. **Production Implementation**
   - Build production-ready API integration
   - Deploy for high-value workflows
   - Monitor success rates and user satisfaction
   - Iterate and expand

---

## Key Contacts

**Louisville Metro Technology Services:**
- Main: Call 311 → ask for Metro Tech Services
- Website: https://louisvilleky.gov/government/metro-technology-services
- Open Data: https://louisvilleky.gov/government/metro-technology-services/open-data

**Accela Support:**
- Developer Portal: https://developer.accela.com
- Documentation: https://developer.accela.com/docs

---

## Bottom Line

**YES, we can automate service request submission via API.**

**Options:**
1. **Quick win:** Deploy informational Q&As now (addresses Oliver's content feedback)
2. **Better experience:** Add API automation for simple workflows (2-4 weeks)
3. **Best experience:** Full automation with smart routing (2-3 months)

**Next move:** Contact Louisville Metro Technology Services to request API access while deploying Phase 1 informational Q&As.

**This addresses Oliver's recurring feedback:** "ideally the agent builds out the workflow to handle [X] process"

---

## Sources

- [Accela on LouisvilleKY.gov](https://louisvilleky.gov/government/metro-technology-services/accela)
- [Louisville Metro Government launches new Accela portals](https://louisvilleky.gov/news/louisville-metro-government-launches-new-accela-business-customer-portals)
- [Accela Civic Platform API](https://developer.accela.com/docs/construct-civicPlatformAndConstructApi.html)
- [The Civic Platform and the Accela API](https://developer.accela.com/docs/accela_construct_api_developers_guide/overview/the_civic_platform_and_the_construct_api.htm)
- [Louisville Metro 311 Open Data](https://catalog.data.gov/dataset/louisville-metro-ky-metro-311-service-request-2025)
- [Open311 GeoReport v2 API](https://wiki.open311.org/GeoReport_v2/)
- [Louisville Open Data Portal](https://louisvilleky.gov/government/metro-technology-services/services/open-data-portal)
- [Making a Service Request](https://louisvilleky.gov/government/metro311/making-service-request)
- [Metro311 main page](https://louisvilleky.gov/government/metro311)

---

**Research by:** Rachael + Claude Code (Sonnet 4.5)
**Date:** February 19, 2026
