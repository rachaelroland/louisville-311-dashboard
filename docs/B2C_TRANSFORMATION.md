# B2C Customer Service Transformation

## Overview

The Louisville 311 Dashboard chat agent has been successfully transformed from a business intelligence/analytics tool into a customer service agent for Louisville residents.

**Commit:** `66f218c`
**Date:** February 9, 2026
**Status:** ✅ Deployed

---

## What Changed

### Before: Business Intelligence Agent
- **Audience:** City officials, analysts, business stakeholders
- **Purpose:** Analyze 311 data for insights, trends, cost savings
- **Tone:** Analytical, data-driven, professional
- **Questions:** "What are the top service types?", "Show sentiment breakdown"

### After: Customer Service Agent
- **Audience:** Louisville residents
- **Purpose:** Help people use 311 services, submit requests, get answers
- **Tone:** Warm, friendly, supportive, empathetic
- **Questions:** "How do I submit a request?", "Can I track my request?"

---

## System Prompt Transformation

### Old Role
```
You are a helpful assistant for the Louisville Metro 311 Service Request Dashboard.
- Provide insights based on this dataset
- Answer questions about trends and patterns
- Give specific numbers and percentages
```

### New Role
```
You are a friendly and helpful customer service representative for Louisville Metro 311 services.
- Help residents understand what 311 services are available
- Guide people on how to submit service requests
- Provide positive, factual information about city services
- Make residents feel heard and supported
```

---

## Key Content Changes

### Welcome Message

**Before:**
> "I have information about 9,337 service requests from 2024. Ask questions in plain English and I'll provide insights based on the data."

**After:**
> "Welcome! I'm here to help you understand Louisville Metro's 311 services and answer your questions about reporting non-emergency city issues. Whether you need to report a pothole, request trash pickup, or learn about city services, I'm happy to help!"

### Page Title

**Before:** "💬 Ask Me Anything About 311 Data"

**After:** "💬 Ask Me About Louisville 311 Services"

### Initial Greeting

**Before:** "👋 Hello! I'm your 311 data assistant. Ask me anything about the service requests!"

**After:** "👋 Hello! I'm here to help you with Louisville Metro 311 services. Ask me how to report issues, what services are available, or anything else about 311!"

---

## Quick Questions Transformation

### Old Questions (Analytics-Focused)
1. ❌ "What are the top 5 service request types?"
2. ❌ "How many requests are high urgency?"
3. ❌ "What is the sentiment breakdown?"
4. ❌ "Tell me about the call center bottlenecks"
5. ❌ "How much money can we save?"
6. ❌ "What are the critical issues right now?"

### New Questions (Resident-Focused)
1. ✅ "How do I submit a 311 service request?"
2. ✅ "What types of issues can I report to 311?"
3. ✅ "How long does it take to fix a pothole?"
4. ✅ "How do I request bulk trash pickup?"
5. ✅ "Can I track the status of my request?"
6. ✅ "What's the difference between 311 and 911?"

---

## Follow-Up Question Generation

### Old Suggestions (Analytics)
- "What's the sentiment breakdown for the top service types?"
- "Which service types have the highest urgency?"
- "What are the main call center bottlenecks?"
- "What business opportunities exist?"

### New Suggestions (Customer Service)
- "Can I track the status of my request?"
- "How do I get my request tracking number?"
- "Is there a mobile app for 311?"
- "When is my regular trash pickup day?"
- "How do I report a streetlight that's out?"
- "What happens after I submit a 311 request?"

---

## Safety Guidelines Updates

### Core Principles (Maintained)
- ✅ Respect all Louisville community members equally
- ✅ Stay on topic (311 services only)
- ✅ Be factual and helpful
- ✅ Refuse inappropriate or discriminatory questions
- ✅ Maintain professionalism

### New Customer Service Focus

**Tone Shift:**
- Old: "I can only provide objective data about 311 service requests"
- New: "I'm here to help all Louisville residents get the city services they need"

**Refusals:**
- Old: "I can only provide factual data about service request volumes"
- New: "I'm here to help you with any 311 service needs you have! What issue can I help you report today?"

**Empathy Added:**
- "I understand that's frustrating"
- "I'm glad you reached out"
- "I'm happy to help!"

---

## Customer Service Approach

The agent now follows these principles:

1. **Be Warm & Welcoming**
   - Use friendly, encouraging language
   - Show appreciation for questions
   - End with offers to help further

2. **Focus on Solutions**
   - "Here's what you can do..."
   - "The best next step is..."
   - Guide residents to actionable answers

3. **Use Plain Language**
   - Avoid jargon and technical terms
   - Explain things clearly
   - Make 311 accessible to everyone

4. **Show Empathy**
   - Acknowledge concerns
   - Be patient with repeated questions
   - Treat every resident's issue as important

5. **Provide Clear Next Steps**
   - How to submit a request
   - What to expect for timing
   - How to follow up or track

---

## Example Interactions

### Example 1: How to Report a Pothole

**User:** "There's a big pothole on my street. How do I report it?"

**Agent Response:**
> "I'm happy to help you report that pothole! Here's how:
>
> **To submit a 311 request:**
> 1. Call 311 (or 574-5000 from outside Louisville)
> 2. Or visit louisvilleky.gov/311 to submit online
> 3. You can also use the Louisville Metro mobile app
>
> **What to provide:**
> - Exact location (address or cross streets)
> - Description of the pothole (size, location in road)
>
> You'll get a tracking number to check the status! Pothole repairs typically take 3-7 days depending on severity.
>
> Is there anything else I can help you with?"

### Example 2: Trash Pickup Question

**User:** "When is bulk trash pickup in my area?"

**Agent Response:**
> "Great question! To find your specific bulk trash pickup schedule:
>
> **Best option:** Call 311 with your address, and they'll tell you your exact pickup day
>
> **Or check online:** Visit louisvilleky.gov/311 and enter your address
>
> **General info:** Louisville Metro offers bulk item pickup on scheduled days based on your neighborhood. You'll need to set items at the curb the night before your pickup day.
>
> Would you like to know what items can be picked up?"

### Example 3: Tracking a Request

**User:** "I submitted a request last week. How do I check if it's been addressed?"

**Agent Response:**
> "You can track your request using your tracking number! Here's how:
>
> **Online:** Visit louisvilleky.gov/311 and enter your tracking number
>
> **By phone:** Call 311 and provide your tracking number
>
> **Typical timeframes:**
> - High urgency issues: 24-48 hours
> - Standard requests: 3-7 days
> - Routine maintenance: 1-2 weeks
>
> If you don't have your tracking number, you can still call 311 with your address and request details. They can look it up for you!
>
> Is there anything else I can help you with?"

---

## What Stayed the Same

✅ **All safety features maintained:**
- Rate limiting (20 questions/session, 50/hour)
- Conversation memory (20 messages)
- Feedback buttons
- Export transcripts
- Clear chat functionality
- Typing indicator
- Follow-up question suggestions

✅ **Technical infrastructure:**
- OpenRouter API integration
- Claude Sonnet 4.5 model
- FastHTML framework
- Render.com deployment
- All security guidelines

✅ **Respect for community:**
- Equal treatment of all residents
- No discriminatory responses
- Focus on helping everyone
- Professional boundaries

---

## Impact on User Experience

### For Louisville Residents ✅
- **Clear guidance** on how to use 311 services
- **Actionable answers** (not just data)
- **Welcoming tone** that makes them feel supported
- **Practical help** with submitting and tracking requests
- **Easy to understand** plain language responses

### For City Officials 📊
- The analytics/business intelligence features still exist in other dashboard tabs
- The chat is now focused on serving residents
- Reduces 311 call volume by providing self-service answers
- Improves resident satisfaction with city services

---

## Deployment

- **Status:** ✅ Deployed to production
- **URL:** https://louisville-311-dashboard.onrender.com
- **Build:** Automatic from main branch
- **Files reorganized:** All docs moved to `docs/` subdirectory

---

## Testing Recommendations

After deployment, test these scenarios:

1. **Basic Service Questions:**
   - "How do I submit a 311 request?"
   - "What services does 311 offer?"

2. **Specific Issues:**
   - "How do I report a pothole?"
   - "How long does trash pickup take?"

3. **Tracking & Follow-up:**
   - "Can I track my request?"
   - "How do I know when it's fixed?"

4. **Safety Guidelines:**
   - Ask off-topic question → Should redirect warmly
   - Ask inappropriate question → Should refuse politely
   - Ask same question twice → Should answer patiently

5. **Follow-up Suggestions:**
   - Verify suggestions are resident-focused
   - Check that they're contextually relevant
   - Ensure they guide to actionable next steps

---

## Success Metrics

Track these to measure B2C transformation impact:

1. **Resident Engagement:**
   - Questions per session (expect similar or higher)
   - Return visitors (should increase)
   - Session duration

2. **Question Types:**
   - % asking "how to" questions (should increase)
   - % asking analytics questions (should decrease)
   - % asking about tracking/status

3. **Satisfaction:**
   - 👍 vs 👎 ratio (monitor improvement)
   - Repeat questions (should decrease as clarity improves)
   - Resident feedback

4. **Call Center Impact:**
   - Track if 311 call volume decreases
   - Monitor common questions answered by agent
   - Measure self-service success rate

---

## Next Steps

1. **Monitor Usage:**
   - Watch for common questions residents ask
   - Identify gaps in agent knowledge
   - Collect feedback via thumbs up/down

2. **Iterate on Responses:**
   - Update system prompt based on resident needs
   - Add more specific Louisville Metro information
   - Refine follow-up question generation

3. **Enhance Features:**
   - Consider adding integration with 311 tracking system
   - Could add real-time status updates if API available
   - Might add neighborhood-specific information

4. **Promote to Residents:**
   - Share link on Louisville Metro website
   - Promote through social media
   - Include in 311 marketing materials

---

## Files Changed

**Main Changes:**
- `dashboard_app.py` - Complete system prompt and UI transformation

**Organization:**
- Created `docs/` subdirectory
- Moved all documentation to `docs/`
- Created comprehensive `README.md`
- Added this `B2C_TRANSFORMATION.md` guide

**Git History:**
- All changes properly committed and pushed
- Full git history preserved
- Clean diff showing before/after

---

## Conclusion

The Louisville 311 Dashboard chat agent has been successfully transformed from a business intelligence tool to a customer service agent focused on helping Louisville residents. The agent now provides warm, helpful, actionable guidance on using 311 services while maintaining all safety features and technical capabilities.

**Key Achievement:** Residents can now get friendly, helpful answers about how to use 311 services instead of analytics about 311 data patterns.

All changes are deployed and ready for resident use! 🎉
