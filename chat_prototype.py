"""
Proof of Concept: Chat Interface for 311 Dashboard
Simple implementation using FastHTML + Anthropic API

This can be integrated into dashboard_app.py with minimal changes
"""

from fasthtml.common import *
from anthropic import Anthropic
import pandas as pd
import json
import os
from pathlib import Path
from datetime import datetime

# Initialize
app, rt = fast_app(
    hdrs=(
        Link(rel='stylesheet', href='https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css'),
        Style("""
            .chat-container {
                max-width: 800px;
                margin: 2rem auto;
                height: 600px;
                overflow-y: auto;
                border: 1px solid #e5e7eb;
                border-radius: 8px;
                padding: 1rem;
                background: white;
            }
            .message {
                margin-bottom: 1rem;
                padding: 0.75rem 1rem;
                border-radius: 8px;
                max-width: 80%;
            }
            .user-message {
                background: #2193b0;
                color: white;
                margin-left: auto;
                text-align: right;
            }
            .assistant-message {
                background: #f3f4f6;
                color: #1f2937;
            }
            .chat-input-form {
                max-width: 800px;
                margin: 0 auto;
                padding: 1rem;
                background: white;
                border: 1px solid #e5e7eb;
                border-radius: 8px;
            }
            .timestamp {
                font-size: 0.75rem;
                color: #6b7280;
                margin-top: 0.25rem;
            }
            .quick-questions {
                max-width: 800px;
                margin: 1rem auto;
            }
            .quick-question-btn {
                margin: 0.25rem;
            }
        """)
    )
)

# Load data (same as dashboard_app.py)
CURRENT_DIR = Path(__file__).parent
CSV_PATH = CURRENT_DIR / "sample_311_data.csv"
JSON_PATH = CURRENT_DIR / "311_nlp_results.json"

print("Loading 311 NLP data for chat...")
df = pd.read_csv(CSV_PATH)
with open(JSON_PATH, 'r') as f:
    topic_data = json.load(f)

# Initialize Anthropic client
client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

# Build static context (done once at startup for efficiency)
def build_311_context():
    """Build context about the 311 dataset for Claude"""

    # Basic stats
    total = len(df)
    sentiment_counts = df['sentiment'].value_counts().to_dict()
    urgency_counts = df['urgency_level'].value_counts().to_dict()

    # Top issues
    top_services = df['service_name'].value_counts().head(10).to_dict()

    # Critical requests
    critical = df[
        (df['urgency_level'] == 'high') &
        (df['sentiment'] == 'negative')
    ]
    critical_count = len(critical)

    context = f"""You are a helpful assistant for the Louisville Metro 311 Service Request Dashboard.

DATASET OVERVIEW:
- Total service requests: {total:,}
- Date range: 2024
- Data source: Louisville Metro Government 311 system

SENTIMENT DISTRIBUTION:
{json.dumps(sentiment_counts, indent=2)}

URGENCY DISTRIBUTION:
{json.dumps(urgency_counts, indent=2)}

TOP 10 SERVICE REQUEST TYPES:
{json.dumps(top_services, indent=2)}

KEY INSIGHTS:
- {critical_count} CRITICAL requests (high urgency + negative sentiment)
- Most common issue: {df['service_name'].value_counts().index[0]} ({df['service_name'].value_counts().iloc[0]:,} requests)
- {sentiment_counts.get('negative', 0):,} requests have negative sentiment ({sentiment_counts.get('negative', 0)/total*100:.1f}%)
- {urgency_counts.get('high', 0):,} requests are high urgency ({urgency_counts.get('high', 0)/total*100:.1f}%)

BUSINESS OPPORTUNITY:
- Call center bottleneck analysis shows $125,075 annual savings potential
- Main bottlenecks: NSR (48.4%), Waste Management (14.9%), Status Checks (49.4%)

INSTRUCTIONS:
- Answer questions concisely and helpfully based on this dataset
- Provide specific numbers and percentages when relevant
- If asked about trends or patterns, refer to the data above
- If a question can't be answered with this data, say so clearly
- Keep responses under 200 words unless more detail is specifically requested
- Be friendly and professional
"""
    return context

SYSTEM_CONTEXT = build_311_context()

# Simple in-memory chat history (per session)
# In production, you'd use a proper session store
chat_sessions = {}

def get_session_id():
    """Generate simple session ID - in production use cookies/proper sessions"""
    return "default_session"  # Simplified for POC

@rt('/')
def get():
    """Chat interface homepage"""
    session_id = get_session_id()

    return Titled("Louisville 311 Chat Assistant",
        # Header
        Div(
            H1("311 Service Request Chat Assistant", cls="text-center mb-4", style="color: #2193b0;"),
            P(
                "Ask questions about Louisville Metro's 311 service requests. "
                f"I have information about {len(df):,} requests from 2024.",
                cls="text-center text-muted mb-4"
            ),
            cls="container mt-4"
        ),

        # Quick question suggestions
        Div(
            H5("Try asking:", cls="mb-3"),
            Button("What are the top 5 issues?",
                   cls="btn btn-sm btn-outline-primary quick-question-btn",
                   hx_post="/ask",
                   hx_vals='{"message": "What are the top 5 service request types?"}',
                   hx_target="#chat-history",
                   hx_swap="beforeend"),
            Button("How many requests are high urgency?",
                   cls="btn btn-sm btn-outline-primary quick-question-btn",
                   hx_post="/ask",
                   hx_vals='{"message": "How many requests are high urgency?"}',
                   hx_target="#chat-history",
                   hx_swap="beforeend"),
            Button("What's the sentiment breakdown?",
                   cls="btn btn-sm btn-outline-primary quick-question-btn",
                   hx_post="/ask",
                   hx_vals='{"message": "What is the sentiment breakdown?"}',
                   hx_target="#chat-history",
                   hx_swap="beforeend"),
            Button("Tell me about call center bottlenecks",
                   cls="btn btn-sm btn-outline-primary quick-question-btn",
                   hx_post="/ask",
                   hx_vals='{"message": "Tell me about the call center bottlenecks"}',
                   hx_target="#chat-history",
                   hx_swap="beforeend"),
            cls="quick-questions"
        ),

        # Chat history container
        Div(id="chat-history", cls="chat-container"),

        # Chat input form
        Form(
            Div(
                Input(
                    name="message",
                    placeholder="Ask a question about 311 service requests...",
                    cls="form-control",
                    required=True,
                    autofocus=True
                ),
                Button("Send", type="submit", cls="btn btn-primary mt-2"),
                cls="chat-input-form"
            ),
            hx_post="/ask",
            hx_target="#chat-history",
            hx_swap="beforeend",
            hx_on="htmx:afterRequest: this.reset()"  # Clear form after submit
        )
    )

@rt('/ask')
def post(message: str):
    """Handle chat message and return response"""

    if not message or message.strip() == "":
        return Div("Please enter a question.", cls="alert alert-warning")

    timestamp = datetime.now().strftime("%I:%M %p")

    # User message bubble
    user_msg = Div(
        Div(message, cls="message user-message"),
        Div(timestamp, cls="timestamp text-end"),
        style="display: flex; flex-direction: column; align-items: flex-end;"
    )

    # Call Claude API
    try:
        response = client.messages.create(
            model="claude-sonnet-4-5-20250929",
            max_tokens=1024,
            temperature=0.7,
            system=SYSTEM_CONTEXT,
            messages=[
                {"role": "user", "content": message}
            ]
        )

        assistant_text = response.content[0].text

    except Exception as e:
        assistant_text = f"Sorry, I encountered an error: {str(e)}"

    # Assistant message bubble
    assistant_msg = Div(
        Div(assistant_text, cls="message assistant-message"),
        Div(timestamp, cls="timestamp"),
        style="display: flex; flex-direction: column; align-items: flex-start;"
    )

    # Return both messages
    return Div(user_msg, assistant_msg)

if __name__ == '__main__':
    print(f"\n🤖 311 Chat Assistant starting...")
    print(f"📊 Loaded {len(df):,} service requests")
    print(f"🚀 Chat interface at http://localhost:5003\n")
    serve(port=5003)
