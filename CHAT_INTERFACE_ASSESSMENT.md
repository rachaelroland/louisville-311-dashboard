# Chat Interface Assessment for 311 Dashboard

## Request from Oliver

> "How much of a lift would it be to enable a chat interface where any human with a link to the chatbot could ask 311 related questions and get back answers…. Easy answers to easy questions?"

---

## TL;DR: **SMALL TO MEDIUM LIFT** (~4-8 hours)

**Complexity:** Medium
**Risk:** Low
**Value:** High (great user engagement feature)

---

## What's Needed

### 1. Chat UI Component (2-3 hours)
- Simple chat interface with message bubbles
- Input field for questions
- Chat history display
- Can use FastHTML + HTMX (already in stack)
- Bootstrap styling (already loaded)

### 2. Claude API Integration (1-2 hours)
- Add `anthropic` package to requirements.txt
- Create chat endpoint to handle messages
- Simple prompt engineering for 311 context
- Stream responses back to UI

### 3. Context Management (1-2 hours)
- Load 311 data summary into context
- Include key statistics (sentiment, urgency, top issues)
- Reference the topic modeling results
- Keep context window manageable

### 4. Session Management (1 hour)
- Simple in-memory chat history per session
- Could use cookies or URL params for session ID
- No database needed initially

### 5. Deploy & Test (1 hour)
- Test with real questions
- Verify API key handling
- Deploy to Render (already set up)

---

## Technical Approach

### Option A: Simple Implementation (Recommended)
**Time: ~4-6 hours**

```python
# Add to dashboard_app.py

from anthropic import Anthropic
import os

# Initialize Anthropic client
client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

# Chat endpoint
@rt('/chat')
def get():
    return Titled("311 Chat Assistant",
        Div(id="chat-history", cls="chat-container"),
        Form(
            Input(name="message", placeholder="Ask about Louisville 311 data...", cls="form-control"),
            Button("Send", cls="btn btn-primary"),
            hx_post="/chat/send",
            hx_target="#chat-history",
            hx_swap="beforeend"
        )
    )

@rt('/chat/send')
def post(message: str):
    # Build context from our data
    context = f"""You are a helpful assistant for Louisville Metro 311 service request data.

    Dataset: {len(df)} service requests from 2024
    Top Issues: {df['service_name'].value_counts().head(5).to_dict()}
    Sentiment: {df['sentiment'].value_counts().to_dict()}
    Urgency: {df['urgency_level'].value_counts().to_dict()}

    Answer questions concisely and helpfully based on this data."""

    # Call Claude API
    response = client.messages.create(
        model="claude-sonnet-4-5-20250929",
        max_tokens=1024,
        messages=[
            {"role": "user", "content": context + "\n\nQuestion: " + message}
        ]
    )

    # Return chat bubbles
    return (
        Div(message, cls="user-message"),
        Div(response.content[0].text, cls="assistant-message")
    )
```

**Pros:**
- Fast to implement
- Uses existing FastHTML patterns
- No complex state management
- Works with Anthropic API key already in env

**Cons:**
- No persistent chat history
- Each question is independent (no conversation memory)
- Could get expensive if lots of traffic

### Option B: Stateful Chat with History (More Complex)
**Time: ~6-8 hours**

Add conversation history tracking, use Claude's multi-turn chat properly, store sessions in memory or simple DB.

**Pros:**
- Better user experience (remembers context)
- Can have multi-turn conversations
- More natural Q&A flow

**Cons:**
- More complex state management
- Need to handle session cleanup
- Slightly higher implementation time

---

## Cost Considerations

**Claude API Pricing (Sonnet 4.5):**
- Input: ~$3 per million tokens
- Output: ~$15 per million tokens

**Estimated costs for 311 chat:**
- Average question: ~100 input tokens + 311 data context (~500 tokens) = 600 tokens
- Average response: ~200 output tokens
- Cost per interaction: ~$0.003 (less than a penny)
- 1000 questions/month: ~$3
- 10,000 questions/month: ~$30

**Very affordable for a public-facing chat interface.**

---

## Example Questions It Could Answer

**Easy Questions (works great):**
- "What are the top 5 service request types?"
- "How many requests were negative sentiment?"
- "What percentage of requests are high urgency?"
- "What's the most common complaint?"
- "How can the call center reduce bottlenecks?"

**Medium Questions (should work):**
- "Show me trends in waste management requests"
- "What areas need the most attention?"
- "Compare NSR vs other service types"
- "What are the critical issues right now?"

**Harder Questions (might need data access):**
- "Show me a map of requests by neighborhood" (would need geographic data)
- "What's the average resolution time?" (would need dates/status data)
- "Which requests are still open?" (would need status tracking)

---

## Implementation Plan

### Phase 1: Basic Chat (4-6 hours)
1. Add `/chat` route with simple UI
2. Integrate Anthropic API
3. Load 311 data context into prompts
4. Test with common questions
5. Deploy to Render

### Phase 2: Enhanced Chat (optional, +2-4 hours)
1. Add conversation history
2. Better prompt engineering
3. Add quick question buttons
4. Improve UI/UX with streaming responses

---

## Risks & Mitigations

### Risk 1: API Costs
**Mitigation:**
- Add rate limiting (max 10 questions/session)
- Monitor usage via Anthropic dashboard
- Set monthly budget alerts

### Risk 2: Bad Answers
**Mitigation:**
- Prompt engineering to stay on topic
- Add disclaimer "AI-generated, verify important info"
- Test thoroughly before launch

### Risk 3: Abuse/Spam
**Mitigation:**
- Rate limiting per IP or session
- Simple CAPTCHA if needed
- Monitor for unusual patterns

---

## Recommendation

**✅ GO FOR IT - Small lift, high value**

**Suggested Approach:**
1. Start with Option A (Simple Implementation)
2. Deploy quickly and gather user feedback
3. Enhance based on real usage patterns
4. Could be done in a single development session

**Next Steps:**
1. Confirm you want this feature
2. Verify Anthropic API key is available in Render env vars
3. I can implement Option A (~4-6 hours work, can do today)
4. Test locally, then deploy to Render

---

## Resources Needed

- ✅ Anthropic API key (already have in OS env)
- ✅ FastHTML (already using)
- ✅ 311 data (already loaded)
- ✅ Render deployment (already set up)
- 🆕 Add `anthropic>=0.39.0` to requirements.txt

**No additional infrastructure or services needed!**

---

## Bottom Line

This is a **high-value, low-risk addition** that would make the dashboard much more interactive and useful. Users could ask natural language questions instead of navigating charts.

**Estimated time to working prototype: 4-6 hours**
**Estimated cost: ~$3-30/month depending on usage**
**User value: High (makes data accessible to non-technical users)**

Let me know if you want me to build it!
