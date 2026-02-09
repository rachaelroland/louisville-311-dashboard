# Chat Interface - Visual Guide

## What You'll See

### Navigation (All Pages)
```
┌────────────────────────────────────────────────────────────────────┐
│  Louisville Metro 311 NLP Analysis Dashboard                       │
│  169,598 Service Requests • 2024 Analysis                         │
│                                                                     │
│  [🏠 Overview] [📊 Call Center] [🎯 Topics] [😊 Sentiment]        │
│  [🚨 Urgency] [💼 Business] [💬 Ask Questions] ← NEW               │
└────────────────────────────────────────────────────────────────────┘
```

### Chat Page Header
```
┌────────────────────────────────────────────────────────────────────┐
│                                                                     │
│  💬 Ask Me Anything About 311 Data                                 │
│                                                                     │
│  I have information about 9,337 service requests from 2024.        │
│  Ask questions in plain English and I'll provide insights based    │
│  on the data.                                                      │
│                                                                     │
│  💡 Tip: Try asking about sentiment, urgency levels, top issues,   │
│  or business opportunities.                                        │
│                                                                     │
└────────────────────────────────────────────────────────────────────┘
```

### Quick Questions Section
```
Try these questions:

[What are the top 5 service request types?]  [How many requests are high urgency?]

[What is the sentiment breakdown?]  [Tell me about the call center bottlenecks]

[How much money can we save?]  [What are the critical issues right now?]
```

### Chat Container
```
┌────────────────────────────────────────────────────────────────────┐
│  👋 Hello! I'm your 311 data assistant. Ask me anything about     │
│  the service requests!                                             │
│                                                                     │
│                                                                     │
│                                What are the top 3 service types? ▓ │
│                                                            7:13 PM │
│                                                                     │
│  ▓ Based on the data, the top 3 service request types are:        │
│                                                                     │
│    1. **NSR** - 4,529 requests (48.5%)                            │
│       The most common type, likely "No Service Rendered"          │
│                                                                     │
│    2. **Waste Management** - 1,393 requests (14.9%)               │
│       Second most common, includes trash/recycling issues         │
│                                                                     │
│    3. **Status Check** - 657 requests (7.0%)                      │
│       People checking on existing requests                        │
│                                                                     │
│    These three types account for 70.4% of all requests!           │
│  7:13 PM                                                           │
│                                                                     │
│                                                                     │
│                              How many are high urgency requests? ▓ │
│                                                            7:14 PM │
│                                                                     │
│  ▓ According to the data, there are **1,219 high urgency          │
│    requests** out of 9,337 total requests.                        │
│                                                                     │
│    That's **13.1%** of all service requests.                      │
│                                                                     │
│    Additionally, 10 of these high urgency requests also have      │
│    negative sentiment, making them CRITICAL priority items.       │
│  7:14 PM                                                           │
│                                                                     │
│  [Scrollable area - more messages above and below]                │
└────────────────────────────────────────────────────────────────────┘
```

### Input Form
```
┌────────────────────────────────────────────────────────────────────┐
│                                                                     │
│  ┌─────────────────────────────────────────────────────┐  ┌─────┐ │
│  │ Ask a question about 311 service requests...        │  │Send │ │
│  └─────────────────────────────────────────────────────┘  └─────┘ │
│                                                                     │
└────────────────────────────────────────────────────────────────────┘
```

## Color Scheme

### User Messages
- Background: Blue gradient (from #2193b0 to #6dd5ed)
- Text: White
- Alignment: Right side
- Style: Rounded corners, 75% max width

### Assistant Messages
- Background: Light gray (#f3f4f6)
- Text: Dark gray (#1f2937)
- Border: 4px solid blue (#2193b0) on left
- Alignment: Left side
- Style: Rounded corners, 75% max width

### Chat Container
- Background: White
- Border: Light gray
- Shadow: Subtle
- Height: 500px
- Scrollable: Yes

### Buttons
- Quick Questions: Outlined blue, small size
- Send: Solid blue, large size
- Hover: Darker blue

## Example Conversation Flow

### Question 1: Basic Stats
```
User:  What percentage of requests are negative?
7:15 PM

Bot:  Based on the sentiment analysis, **35.8% of requests
      have negative sentiment**.

      That's 3,346 requests out of 9,337 total.

      In contrast:
      • Positive: 11 requests (0.1%)
      • Neutral: 5,782 requests (61.9%)
      • Negative: 3,346 requests (35.8%)

      The high negative sentiment suggests significant
      dissatisfaction that should be addressed.
7:15 PM
```

### Question 2: Business Insights
```
User:  Where can we save the most money?
7:16 PM

Bot:  According to the business opportunity analysis, the
      biggest cost savings come from **reducing call center
      bottlenecks**.

      **Total Potential Savings: $125,075 annually**

      Main bottleneck areas:
      1. **NSR requests** (48.4% of bottleneck)
         • Most common issue type
         • Often require multiple follow-ups

      2. **Waste Management** (14.9% of bottleneck)
         • Second most common
         • Frequent status check calls

      3. **Status Checks** (49.4% of calls)
         • People calling to check on requests
         • Could be solved with self-service portal

      Recommendation: Build a self-service portal to reduce
      call volume by 56.3%.
7:16 PM
```

### Question 3: Comparisons
```
User:  Compare NSR to Waste Management
7:17 PM

Bot:  Here's a comparison of NSR vs Waste Management:

      **Volume:**
      • NSR: 4,529 requests (48.5%)
      • Waste: 1,393 requests (14.9%)
      • NSR has 3.2x more requests

      **Sentiment:**
      • Both have predominantly negative/neutral sentiment
      • NSR: Higher volume of complaints
      • Waste: More urgent issues

      **Business Impact:**
      • NSR is the #1 call center bottleneck
      • Waste is #2 but more time-sensitive

      **Recommendation:**
      Focus on NSR first for volume reduction, but prioritize
      Waste for urgency response.
7:17 PM
```

## Mobile View

On mobile devices (< 768px):
- Messages stack vertically
- Buttons wrap to multiple rows
- Input field full width
- Chat container adjusts height
- All features remain functional

## Loading States

When sending a message:
- Input field clears immediately
- New messages append to chat
- Auto-scroll to bottom
- Timestamps update

## Error States

If API fails:
```
Bot:  I apologize, but I encountered an error processing
      your question. Please try again or contact support.

      [Technical details hidden from user]
7:18 PM
```

## Empty State

When chat first loads:
```
👋 Hello! I'm your 311 data assistant. Ask me anything
   about the service requests!
```

## How to Try It

1. **Open your browser**
   - Go to: http://localhost:5002/chat

2. **Click a quick question**
   - Try: "What are the top 5 service request types?"
   - See the response appear instantly

3. **Type your own question**
   - Click in the input field
   - Type: "What should we prioritize?"
   - Click "Send" or press Enter

4. **Explore the data**
   - Ask follow-up questions
   - Compare different metrics
   - Get business insights

The chat remembers the context about the 311 data, so you can ask complex questions and get accurate, data-driven answers!
