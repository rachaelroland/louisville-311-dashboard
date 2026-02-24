#!/usr/bin/env python3
"""
Louisville Metro 311 NLP Analysis Dashboard
FastHTML web application for interactive data exploration
"""

from fasthtml.common import *
import pandas as pd
import json
import plotly.graph_objects as go
import plotly.express as px
from pathlib import Path
import os
from datetime import datetime
import requests
import uuid
from collections import defaultdict, deque
import psycopg2
from psycopg2.pool import SimpleConnectionPool
from psycopg2.extras import RealDictCursor

# ============================================================================
# CONFIGURATION
# ============================================================================

# Data paths
CURRENT_DIR = Path(__file__).parent
# Use sample data for deployment, full data for local development
CSV_PATH = CURRENT_DIR / "sample_311_data.csv"
if not CSV_PATH.exists():
    # Fallback to full dataset if available locally
    CSV_PATH = Path("/Users/rachael/Documents/projects/rachaelroland/pipelines/pipelines/311/data/processed/311_processed_with_nlp.csv")
JSON_PATH = CURRENT_DIR / "311_nlp_results.json"
FEEDBACK_PATH = CURRENT_DIR / "chat_feedback.json"

# Load data on startup
print("Loading 311 NLP data...")
df = pd.read_csv(CSV_PATH, low_memory=False)
with open(JSON_PATH, 'r') as f:
    topic_data = json.load(f)

print(f"Loaded {len(df):,} service requests")

# Initialize OpenRouter for chat
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
if OPENROUTER_API_KEY:
    CHAT_ENABLED = True
    print("✅ OpenRouter API key found - chat enabled")
else:
    CHAT_ENABLED = False
    print("⚠️  OpenRouter API key not found - chat disabled")

# ============================================================================
# DATABASE CONNECTION (Approved Questions)
# ============================================================================

SUPABASE_HOST = "db.cxzhgidmzosdavugggks.supabase.co"
SUPABASE_DB = "postgres"
SUPABASE_USER = "postgres"
SUPABASE_PASSWORD = os.getenv("SUPABASE_PASSWORD", "5kvsZGhH")  # Default for dev

# Create connection pool
db_pool = None
if SUPABASE_PASSWORD:
    try:
        db_pool = SimpleConnectionPool(
            minconn=1,
            maxconn=10,
            host=SUPABASE_HOST,
            database=SUPABASE_DB,
            user=SUPABASE_USER,
            password=SUPABASE_PASSWORD,
            port=5432
        )
        print("✅ Database connection pool initialized - approved questions enabled")
    except Exception as e:
        print(f"⚠️  Database connection failed: {e}")
        print("   Chat will fall back to generic Claude responses")
        db_pool = None
else:
    print("⚠️  SUPABASE_PASSWORD not set - approved questions disabled")

# ============================================================================
# DATABASE CONNECTION MANAGEMENT (Supabase Best Practices)
# ============================================================================

import time
from contextlib import contextmanager

@contextmanager
def get_db_connection():
    """
    Context manager for database connections with proper lifecycle management
    Implements Supabase best practices for connection pooling

    Usage:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            # ... use connection
    """
    conn = None
    try:
        if not db_pool:
            raise Exception("Database pool not initialized")

        conn = db_pool.getconn()
        yield conn

    except Exception as e:
        print(f"⚠️  Database connection error: {e}")
        if conn:
            conn.rollback()  # Rollback on error
        raise
    finally:
        if conn:
            db_pool.putconn(conn)

def log_slow_query(query_name: str, duration: float, threshold: float = 0.5):
    """
    Log queries that exceed performance threshold
    Implements monitoring best practices

    Args:
        query_name: Name/description of the query
        duration: Query execution time in seconds
        threshold: Threshold in seconds (default: 0.5s)
    """
    if duration > threshold:
        print(f"⚠️  SLOW QUERY: {query_name} took {duration:.3f}s (threshold: {threshold}s)")

# ============================================================================
# CONVERSATION MEMORY
# ============================================================================

# Simple in-memory session store
# Key: session_id, Value: deque of message dicts (max 20 messages)
chat_sessions = defaultdict(lambda: deque(maxlen=20))

# Session cleanup (remove sessions older than 1 hour)
session_timestamps = {}

# Rate limiting
# Key: session_id, Value: count of questions asked
session_question_counts = defaultdict(int)

# Key: IP address, Value: list of timestamps for questions
ip_question_timestamps = defaultdict(list)

# Rate limits
MAX_QUESTIONS_PER_SESSION = 20
MAX_QUESTIONS_PER_IP_PER_HOUR = 50

def get_session_id(request):
    """Get or create session ID from cookie"""
    session_id = request.cookies.get('chat_session_id')
    if not session_id:
        session_id = str(uuid.uuid4())
    return session_id

def get_client_ip(request):
    """Get client IP address from request"""
    # Check for forwarded IP (when behind proxy/load balancer)
    forwarded = request.headers.get('X-Forwarded-For')
    if forwarded:
        return forwarded.split(',')[0].strip()
    return request.client.host if hasattr(request, 'client') else '127.0.0.1'

def check_rate_limit(session_id: str, ip_address: str):
    """
    Check if user has exceeded rate limits
    Returns: (is_allowed: bool, remaining_questions: int, error_message: str)
    """
    current_time = datetime.now()

    # Check session-based limit (20 questions per session)
    session_count = session_question_counts[session_id]
    if session_count >= MAX_QUESTIONS_PER_SESSION:
        return False, 0, f"You've reached the limit of {MAX_QUESTIONS_PER_SESSION} questions per session. Please clear your chat to start a new session."

    # Check IP-based limit (50 questions per hour)
    # Remove timestamps older than 1 hour
    timestamps = ip_question_timestamps[ip_address]
    recent_timestamps = [ts for ts in timestamps if (current_time - ts).seconds < 3600]
    ip_question_timestamps[ip_address] = recent_timestamps

    if len(recent_timestamps) >= MAX_QUESTIONS_PER_IP_PER_HOUR:
        return False, 0, f"You've reached the limit of {MAX_QUESTIONS_PER_IP_PER_HOUR} questions per hour. Please try again later."

    # Calculate remaining questions
    remaining = min(
        MAX_QUESTIONS_PER_SESSION - session_count,
        MAX_QUESTIONS_PER_IP_PER_HOUR - len(recent_timestamps)
    )

    return True, remaining, ""

def increment_rate_limit(session_id: str, ip_address: str):
    """Increment rate limit counters after a successful question"""
    session_question_counts[session_id] += 1
    ip_question_timestamps[ip_address].append(datetime.now())

def cleanup_old_sessions():
    """Remove sessions older than 1 hour (basic cleanup)"""
    current_time = datetime.now()
    old_sessions = [
        sid for sid, timestamp in session_timestamps.items()
        if (current_time - timestamp).seconds > 3600
    ]
    for sid in old_sessions:
        if sid in chat_sessions:
            del chat_sessions[sid]
        del session_timestamps[sid]
        if sid in session_question_counts:
            del session_question_counts[sid]

def generate_follow_up_questions(user_question: str):
    """
    Generate contextual follow-up questions for residents based on keywords in the user's question
    Returns a list of 2-3 follow-up question strings focused on helping residents use 311 services
    """
    question_lower = user_question.lower()

    # Keyword-based follow-up generation for resident questions
    follow_ups = []

    # Submit/report related questions
    if any(word in question_lower for word in ['submit', 'report', 'how', 'request', 'file']):
        follow_ups.extend([
            "Can I track the status of my request?",
            "What information do I need to submit a request?",
            "Is there a mobile app for 311?"
        ])

    # Service type questions (what can 311 help with)
    if any(word in question_lower for word in ['service', 'type', 'what', 'help', 'handle']):
        follow_ups.extend([
            "How do I report a pothole?",
            "Can 311 help with bulk trash pickup?",
            "What's not covered by 311 services?"
        ])

    # Time/speed related questions
    if any(word in question_lower for word in ['long', 'time', 'take', 'fast', 'quick', 'when']):
        follow_ups.extend([
            "How do I check if my request is being processed?",
            "What happens after I submit a 311 request?",
            "Can I request priority service?"
        ])

    # Trash/waste related questions
    if any(word in question_lower for word in ['trash', 'waste', 'garbage', 'pickup', 'bulk']):
        follow_ups.extend([
            "When is my regular trash pickup day?",
            "How do I schedule a bulk item pickup?",
            "What items can't be picked up by waste management?"
        ])

    # Street/road related questions
    if any(word in question_lower for word in ['pothole', 'street', 'road', 'sidewalk', 'traffic']):
        follow_ups.extend([
            "How do I report a streetlight that's out?",
            "Can I request a speed limit sign?",
            "How do I report sidewalk damage?"
        ])

    # Track/status related questions
    if any(word in question_lower for word in ['track', 'status', 'check', 'update', 'progress']):
        follow_ups.extend([
            "How do I get my request tracking number?",
            "Will I be notified when my issue is fixed?",
            "Can I call 311 to check on my request?"
        ])

    # Emergency vs non-emergency
    if any(word in question_lower for word in ['911', 'emergency', 'difference', 'urgent']):
        follow_ups.extend([
            "What types of issues should I call 911 for?",
            "Can 311 help with urgent issues?",
            "Where can I report a water main break?"
        ])

    # If no specific keywords matched, provide general helpful follow-ups
    if not follow_ups:
        follow_ups = [
            "How do I submit a 311 service request?",
            "What types of issues can 311 help with?",
            "Can I track my request online?"
        ]

    # Return up to 3 unique follow-ups
    return list(dict.fromkeys(follow_ups))[:3]

def extract_question_context(user_question: str):
    """
    Extract topics, entities, and intent from user question using Claude
    Uses fast extraction to enhance search

    Returns:
        dict with keys: topics, entities, category_hints, keywords
    """
    if not OPENROUTER_API_KEY:
        return None

    try:
        # Use Claude to quickly extract context
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": "anthropic/claude-sonnet-4.5:beta",
                "messages": [{
                    "role": "user",
                    "content": f"""Extract structured information from this 311 service question:

Question: "{user_question}"

Return JSON with:
1. topics: list of main topics (e.g., "waste management", "street maintenance", "code enforcement")
2. entities: list of extracted entities (locations, dates, specific items)
3. category_hints: list of likely 311 categories (Animal Control, Code Enforcement, Emergency Services, Environmental, General, Health, Parking, Parks, Social Services, Street Maintenance, Utilities, Waste Management, Water/Sewer)
4. keywords: list of important keywords for search

Example:
{{"topics": ["waste management", "trash pickup"], "entities": ["bulk item"], "category_hints": ["Waste Management"], "keywords": ["bulk", "trash", "pickup", "schedule"]}}

Return only valid JSON, no explanation."""
                }],
                "max_tokens": 200,
                "temperature": 0
            },
            timeout=5
        )

        if response.status_code == 200:
            result = response.json()
            content = result['choices'][0]['message']['content']

            # Parse JSON from response
            import re
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                context = json.loads(json_match.group(0))
                return context

        return None

    except Exception as e:
        print(f"⚠️  Error extracting question context: {e}")
        return None

def find_approved_answer(user_question: str, use_context: bool = False):
    """
    Search l311_approved_questions for best matching Q&A pair
    Uses PostgreSQL full-text search, optionally enhanced with topic/entity extraction

    Implements Supabase best practices:
    - Proper connection lifecycle management
    - Query performance monitoring
    - Graceful error handling

    Args:
        user_question: The user's question text
        use_context: Whether to extract topics/entities for enhanced search (default: False for reliability)

    Returns:
        dict with keys: id, question_text, answer_text, service_name, category
        or None if no match found
    """
    if not db_pool:
        return None

    start_time = time.time()

    try:
        with get_db_connection() as conn:
            cursor = conn.cursor(cursor_factory=RealDictCursor)

            # Try standard search first (reliable and fast)
            # Note: Uses GIN indexes on question_text and keywords for performance
            query_start = time.time()
            query = """
            SELECT
                id,
                question_text,
                answer_text,
                service_name,
                category,
                typical_urgency,
                ts_rank(
                    to_tsvector('english', question_text || ' ' || array_to_string(keywords, ' ')),
                    plainto_tsquery('english', %s)
                ) as rank
            FROM l311_approved_questions
            WHERE
                to_tsvector('english', question_text || ' ' || array_to_string(keywords, ' '))
                @@ plainto_tsquery('english', %s)
                AND is_approved = true
            ORDER BY rank DESC
            LIMIT 1
            """

            cursor.execute(query, (user_question, user_question))
            result = cursor.fetchone()

            query_duration = time.time() - query_start
            log_slow_query("standard_search", query_duration, threshold=0.1)

            # If no result with standard search and context enabled, try enhanced search
            if not result and use_context:
                print(f"   🔍 No standard match, trying enhanced search with context extraction...")

                context = extract_question_context(user_question)

                if context and context.get('category_hints'):
                    categories = context['category_hints']
                    keywords = context.get('keywords', [])
                    all_terms = user_question + ' ' + ' '.join(keywords)

                    print(f"   📋 Enhanced search - categories: {categories}, keywords: {keywords[:5]}")

                    query_start = time.time()
                    # Enhanced query with category boosting
                    # Uses composite index on (category, is_approved) for performance
                    query = """
                    WITH ranked_results AS (
                        SELECT
                            id,
                            question_text,
                            answer_text,
                            service_name,
                            category,
                            typical_urgency,
                            ts_rank(
                                to_tsvector('english', question_text || ' ' || array_to_string(keywords, ' ')),
                                plainto_tsquery('english', %s)
                            ) as search_rank,
                            CASE
                                WHEN category = ANY(%s) THEN 2.0
                                ELSE 1.0
                            END as category_boost
                        FROM l311_approved_questions
                        WHERE
                            is_approved = true
                            AND (
                                to_tsvector('english', question_text || ' ' || array_to_string(keywords, ' '))
                                @@ plainto_tsquery('english', %s)
                                OR category = ANY(%s)
                            )
                    )
                    SELECT id, question_text, answer_text, service_name, category, typical_urgency
                    FROM ranked_results
                    ORDER BY search_rank * category_boost DESC
                    LIMIT 1
                    """

                    cursor.execute(query, (all_terms, categories, all_terms, categories))
                    result = cursor.fetchone()

                    query_duration = time.time() - query_start
                    log_slow_query("enhanced_search", query_duration, threshold=0.2)

            cursor.close()

            # Log total function execution time
            total_duration = time.time() - start_time
            if total_duration > 0.05:  # Log if > 50ms
                print(f"   ⏱️  find_approved_answer took {total_duration:.3f}s")

            if result:
                result_dict = dict(result)
                return result_dict
            else:
                return None

    except Exception as e:
        print(f"⚠️  Error searching approved questions: {e}")
        import traceback
        traceback.print_exc()
        return None


def increment_question_shown(question_id: int):
    """
    Increment times_shown counter for an approved question

    Implements Supabase best practices:
    - Proper connection lifecycle with context manager
    - Performance monitoring

    Args:
        question_id: ID of the question in l311_approved_questions
    """
    if not db_pool:
        return

    start_time = time.time()

    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("""
                UPDATE l311_approved_questions
                SET times_shown = times_shown + 1
                WHERE id = %s
            """, (question_id,))

            conn.commit()
            cursor.close()

            duration = time.time() - start_time
            log_slow_query("increment_question_shown", duration, threshold=0.05)

    except Exception as e:
        print(f"⚠️  Error incrementing question counter: {e}")


def enrich_answer_with_data_insights(approved_answer: dict, user_question: str, context: dict = None):
    """
    Enrich approved answer with insights from historical 311 data
    Uses NER, topics, and sentiment from analyzed requests

    Args:
        approved_answer: The approved answer dict
        user_question: User's original question
        context: Extracted context (topics, entities, etc.)

    Returns:
        Enhanced answer text with data insights (or original if no insights)
    """
    try:
        base_answer = approved_answer['answer_text']
        category = approved_answer.get('category')
        service_name = approved_answer.get('service_name')

        # Check if we have relevant historical data
        if service_name and len(df) > 0:
            # Filter data for this service
            service_data = df[df['service_name'] == service_name]

            if len(service_data) > 0:
                # Calculate insights
                total_requests = len(service_data)
                avg_urgency = service_data['urgency_score'].mean() if 'urgency_score' in service_data.columns else None
                sentiment_dist = service_data['sentiment'].value_counts().to_dict() if 'sentiment' in service_data.columns else {}

                # Build insight footer (subtle, not intrusive)
                insights = []

                if total_requests >= 100:
                    insights.append(f"📊 Based on {total_requests:,} similar requests in our data")

                if avg_urgency and avg_urgency >= 7:
                    insights.append("⚠️ This is typically a high-priority issue")

                # Only add insights if we have meaningful data
                if insights:
                    insight_text = "\n\n" + " • ".join(insights)
                    return base_answer + insight_text

        return base_answer

    except Exception as e:
        print(f"⚠️  Error enriching answer: {e}")
        return approved_answer['answer_text']


def update_question_feedback(question_id: int, is_helpful: bool):
    """
    Update helpful/not helpful counters for an approved question

    Implements Supabase best practices:
    - Proper connection lifecycle with context manager
    - Performance monitoring

    Args:
        question_id: ID of the question in l311_approved_questions
        is_helpful: True for thumbs up, False for thumbs down
    """
    if not db_pool:
        return

    start_time = time.time()

    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()

            if is_helpful:
                cursor.execute("""
                    UPDATE l311_approved_questions
                    SET times_helpful = times_helpful + 1
                    WHERE id = %s
                """, (question_id,))
            else:
                cursor.execute("""
                    UPDATE l311_approved_questions
                    SET times_not_helpful = times_not_helpful + 1
                    WHERE id = %s
                """, (question_id,))

            conn.commit()
            cursor.close()

            duration = time.time() - start_time
            log_slow_query("update_question_feedback", duration, threshold=0.05)

    except Exception as e:
        print(f"⚠️  Error updating feedback counter: {e}")

# ============================================================================
# FASTHTML APP SETUP
# ============================================================================

app, rt = fast_app(
    hdrs=(
        Link(rel='stylesheet', href='https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css'),
        Script(src='https://cdn.plot.ly/plotly-2.27.0.min.js'),
        Style("""
            .chat-container {
                max-width: 900px;
                margin: 2rem auto;
                height: 500px;
                overflow-y: auto;
                border: 1px solid #e5e7eb;
                border-radius: 8px;
                padding: 1.5rem;
                background: white;
                box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            }
            .message {
                margin-bottom: 1rem;
                padding: 0.75rem 1rem;
                border-radius: 8px;
                max-width: 75%;
                line-height: 1.5;
            }
            .user-message {
                background: linear-gradient(135deg, #2193b0 0%, #6dd5ed 100%);
                color: white;
                margin-left: auto;
                text-align: right;
            }
            .assistant-message {
                background: #f3f4f6;
                color: #1f2937;
                border-left: 4px solid #2193b0;
            }
            .chat-input-form {
                max-width: 900px;
                margin: 1rem auto;
                padding: 1.5rem;
                background: white;
                border: 1px solid #e5e7eb;
                border-radius: 8px;
                box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            }
            .timestamp {
                font-size: 0.75rem;
                color: #6b7280;
                margin-top: 0.25rem;
            }
            .quick-questions {
                max-width: 900px;
                margin: 1rem auto;
            }
            .quick-question-btn {
                margin: 0.25rem;
            }
            .chat-welcome {
                max-width: 900px;
                margin: 2rem auto;
                padding: 2rem;
                background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
                border-radius: 8px;
                border: 1px solid #0ea5e9;
            }
            .typing-indicator {
                display: none;
                padding: 0.75rem 1rem;
                margin-bottom: 1rem;
                background: #f3f4f6;
                border-left: 4px solid #2193b0;
                border-radius: 8px;
                max-width: 75%;
                color: #6b7280;
                font-style: italic;
            }
            .typing-indicator.htmx-request {
                display: block;
            }
            .typing-dots {
                display: inline-block;
            }
            .typing-dots::after {
                content: '...';
                animation: dots 1.5s steps(4, end) infinite;
            }
            @keyframes dots {
                0%, 20% { content: '.'; }
                40% { content: '..'; }
                60%, 100% { content: '...'; }
            }
            .feedback-buttons {
                margin-top: 0.5rem;
                display: flex;
                gap: 0.5rem;
            }
            .feedback-btn {
                background: none;
                border: 1px solid #d1d5db;
                border-radius: 4px;
                padding: 0.25rem 0.5rem;
                cursor: pointer;
                font-size: 1rem;
                transition: all 0.2s;
            }
            .feedback-btn:hover {
                background: #f3f4f6;
                border-color: #9ca3af;
            }
            .feedback-btn.selected {
                background: #e0f2fe;
                border-color: #0ea5e9;
            }
            .feedback-message {
                font-size: 0.75rem;
                color: #6b7280;
                font-style: italic;
                margin-top: 0.25rem;
            }
            .follow-up-questions {
                margin-top: 1rem;
                padding: 0.75rem;
                background: #f9fafb;
                border-radius: 6px;
                border: 1px solid #e5e7eb;
                max-width: 75%;
            }
            .follow-up-label {
                font-size: 0.85rem;
                color: #6b7280;
                font-weight: 500;
                margin-bottom: 0.5rem;
            }
            .follow-up-btn {
                display: block;
                width: 100%;
                text-align: left;
                background: white;
                border: 1px solid #d1d5db;
                border-radius: 4px;
                padding: 0.5rem 0.75rem;
                margin-bottom: 0.5rem;
                cursor: pointer;
                font-size: 0.9rem;
                color: #374151;
                transition: all 0.2s;
            }
            .follow-up-btn:hover {
                background: #f3f4f6;
                border-color: #2193b0;
                color: #2193b0;
            }
            .follow-up-btn:last-child {
                margin-bottom: 0;
            }
        """)
    )
)

# ============================================================================
# NAVIGATION
# ============================================================================

def create_nav(current_page=None):
    """Create top navigation bar"""
    nav_style = """
        background: linear-gradient(135deg, #2193b0 0%, #6dd5ed 100%);
        padding: 1.5rem 2rem;
        margin-bottom: 2rem;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    """

    nav_links = [
        {'text': '🏠 Overview', 'href': '/', 'page': 'home'},
        {'text': '📊 Call Center Analysis', 'href': '/call-center', 'page': 'call-center'},
        {'text': '🎯 Topics', 'href': '/topics', 'page': 'topics'},
        {'text': '😊 Sentiment', 'href': '/sentiment', 'page': 'sentiment'},
        {'text': '🚨 Urgency', 'href': '/urgency', 'page': 'urgency'},
        {'text': '💼 Business Opportunities', 'href': '/business', 'page': 'business'},
        {'text': '💬 Ask Questions', 'href': '/chat', 'page': 'chat'},
    ]

    return Div(
        Div(
            Div(
                H2('Louisville Metro 311 NLP Analysis Dashboard',
                   style='color: white; margin: 0; font-weight: 600;'),
                P('169,598 Service Requests • 2024 Analysis',
                  style='color: rgba(255,255,255,0.9); margin: 0.5rem 0 0 0; font-size: 0.9rem;'),
                cls='d-inline-block'
            ),
            Div(
                *[
                    A(
                        link['text'],
                        href=link['href'],
                        cls='btn btn-sm ' + ('btn-light' if link['page'] == current_page else 'btn-outline-light'),
                        style='margin-left: 0.5rem;'
                    )
                    for link in nav_links
                ],
                cls='d-inline-block float-end'
            ),
            cls='clearfix'
        ),
        style=nav_style
    )

# ============================================================================
# DATA CALCULATIONS
# ============================================================================

def get_summary_stats():
    """Calculate summary statistics"""
    total = len(df)

    # Sentiment distribution
    sentiment_counts = df['sentiment'].value_counts()

    # Urgency distribution
    urgency_counts = df['urgency_level'].value_counts()

    # Service type counts
    service_counts = df['service_name'].value_counts().head(10)

    # Agency counts
    agency_counts = df['agency_responsible'].value_counts().head(10)

    return {
        'total': total,
        'sentiment': sentiment_counts.to_dict(),
        'urgency': urgency_counts.to_dict(),
        'services': service_counts.to_dict(),
        'agencies': agency_counts.to_dict()
    }

def create_sentiment_pie():
    """Create sentiment distribution pie chart"""
    sentiment_counts = df['sentiment'].value_counts()

    # Calculate percentages
    total = sentiment_counts.sum()

    fig = go.Figure(data=[go.Pie(
        labels=sentiment_counts.index,
        values=sentiment_counts.values,
        hole=0.4,
        marker=dict(colors=['#22c55e', '#ef4444', '#6b7280']),
        textinfo='label+percent',
        textfont=dict(size=14),
    )])

    fig.update_layout(
        title=dict(
            text='Sentiment Distribution',
            font=dict(size=20, family='Arial', color='#1f2937')
        ),
        height=400,
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5)
    )

    return fig.to_html(include_plotlyjs=False, div_id='sentiment-pie')

def create_urgency_bar():
    """Create urgency distribution bar chart"""
    urgency_counts = df['urgency_level'].value_counts()
    urgency_order = ['low', 'medium', 'high']
    urgency_counts = urgency_counts.reindex(urgency_order, fill_value=0)

    fig = go.Figure(data=[go.Bar(
        x=urgency_counts.index,
        y=urgency_counts.values,
        marker=dict(color=['#22c55e', '#f59e0b', '#ef4444']),
        text=urgency_counts.values,
        textposition='outside',
        texttemplate='%{text:,}',
    )])

    fig.update_layout(
        title=dict(
            text='Urgency Distribution',
            font=dict(size=20, family='Arial', color='#1f2937')
        ),
        xaxis_title='Urgency Level',
        yaxis_title='Number of Requests',
        height=400,
        showlegend=False
    )

    return fig.to_html(include_plotlyjs=False, div_id='urgency-bar')

def create_top_services_bar():
    """Create top 10 service types bar chart"""
    service_counts = df['service_name'].value_counts().head(10)

    fig = go.Figure(data=[go.Bar(
        y=service_counts.index[::-1],
        x=service_counts.values[::-1],
        orientation='h',
        marker=dict(color='#2193b0'),
        text=service_counts.values[::-1],
        textposition='outside',
        texttemplate='%{text:,}',
    )])

    fig.update_layout(
        title=dict(
            text='Top 10 Service Types',
            font=dict(size=20, family='Arial', color='#1f2937')
        ),
        xaxis_title='Number of Requests',
        yaxis_title='',
        height=500,
        margin=dict(l=250),
        showlegend=False
    )

    return fig.to_html(include_plotlyjs=False, div_id='services-bar')

def create_topic_wordcloud():
    """Create topic visualization from LDA results"""
    lda_topics_dict = topic_data.get('topic_modeling', {}).get('lda', {}).get('topics', {})

    if not lda_topics_dict or not isinstance(lda_topics_dict, dict):
        return "<p>No topic modeling data available</p>"

    # Create simple bar chart of top keywords from top 5 topics
    topic_labels = []
    topic_weights = []

    # Get first 5 topics from the dictionary
    for i in range(min(5, len(lda_topics_dict))):
        topic_key = str(i)
        if topic_key not in lda_topics_dict:
            continue

        topic = lda_topics_dict[topic_key]
        keywords = topic.get('keywords', [])[:5]
        weights = topic.get('weights', [])

        # Calculate average weight for this topic
        avg_weight = sum(weights[:5]) / len(weights[:5]) if weights else 0

        label = f"Topic {i+1}: {', '.join(keywords)}"
        topic_labels.append(label)
        topic_weights.append(avg_weight * 100)

    if not topic_labels:
        return "<p>No topics found</p>"

    fig = go.Figure(data=[go.Bar(
        y=topic_labels[::-1],
        x=topic_weights[::-1],
        orientation='h',
        marker=dict(color='#6dd5ed'),
        text=[f"{w:.1f}%" for w in topic_weights[::-1]],
        textposition='outside',
    )])

    fig.update_layout(
        title=dict(
            text='Top 5 Topics (LDA)',
            font=dict(size=20, family='Arial', color='#1f2937')
        ),
        xaxis_title='Topic Weight (%)',
        yaxis_title='',
        height=400,
        margin=dict(l=400),
        showlegend=False
    )

    return fig.to_html(include_plotlyjs=False, div_id='topics-bar')

# ============================================================================
# ROUTES
# ============================================================================

@rt('/')
def get():
    """Homepage with interactive overview and charts"""
    stats = get_summary_stats()

    # Create metric cards
    metric_cards = Div(
        Div(
            # Total requests
            Div(
                H3(f"{stats['total']:,}", style='font-size: 2.5rem; font-weight: 700; color: #2193b0; margin-bottom: 0.5rem;'),
                P('Total Requests', style='color: #6b7280; font-size: 1.1rem; margin: 0;'),
                style='background: white; padding: 2rem; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); text-align: center;',
                cls='col-md-3'
            ),
            # Negative sentiment
            Div(
                H3(f"{stats['sentiment'].get('negative', 0):,}", style='font-size: 2.5rem; font-weight: 700; color: #ef4444; margin-bottom: 0.5rem;'),
                P('Negative Sentiment', style='color: #6b7280; font-size: 1.1rem; margin: 0;'),
                P(f"{stats['sentiment'].get('negative', 0) / stats['total'] * 100:.1f}%", style='color: #ef4444; font-size: 0.9rem; margin-top: 0.5rem;'),
                style='background: white; padding: 2rem; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); text-align: center;',
                cls='col-md-3'
            ),
            # High urgency
            Div(
                H3(f"{stats['urgency'].get('high', 0):,}", style='font-size: 2.5rem; font-weight: 700; color: #f59e0b; margin-bottom: 0.5rem;'),
                P('High Urgency', style='color: #6b7280; font-size: 1.1rem; margin: 0;'),
                P(f"{stats['urgency'].get('high', 0) / stats['total'] * 100:.1f}%", style='color: #f59e0b; font-size: 0.9rem; margin-top: 0.5rem;'),
                style='background: white; padding: 2rem; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); text-align: center;',
                cls='col-md-3'
            ),
            # Top issue
            Div(
                H3(list(stats['services'].keys())[0] if stats['services'] else 'N/A', style='font-size: 1.2rem; font-weight: 700; color: #10b981; margin-bottom: 0.5rem;'),
                P('Top Issue', style='color: #6b7280; font-size: 1.1rem; margin: 0;'),
                P(f"{list(stats['services'].values())[0]:,} requests" if stats['services'] else '', style='color: #10b981; font-size: 0.9rem; margin-top: 0.5rem;'),
                style='background: white; padding: 2rem; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); text-align: center;',
                cls='col-md-3'
            ),
            cls='row g-4 mb-4'
        )
    )

    # Key insights panel
    insights_panel = Div(
        H3('🎯 Key Insights & Actions', style='color: #1f2937; margin-bottom: 1.5rem;'),
        Div(
            Div(
                H5('1. High Negative Sentiment', style='color: #ef4444;'),
                P(f"{stats['sentiment'].get('negative', 0):,} requests ({stats['sentiment'].get('negative', 0) / stats['total'] * 100:.1f}%) are negative"),
                Strong('Action: '), Span('Focus on root causes of dissatisfaction'),
                A('View Details →', href='/sentiment', cls='btn btn-sm btn-outline-danger mt-2'),
                style='background: #fef2f2; padding: 1.5rem; border-radius: 8px; border-left: 4px solid #ef4444;',
                cls='col-md-6 mb-3'
            ),
            Div(
                H5('2. Top Service Request', style='color: #2193b0;'),
                P(f"{list(stats['services'].keys())[0]}: {list(stats['services'].values())[0]:,} requests"),
                Strong('Action: '), Span('Optimize handling of most common request type'),
                A('Explore Topics →', href='/topics', cls='btn btn-sm btn-outline-primary mt-2'),
                style='background: #f0f9ff; padding: 1.5rem; border-radius: 8px; border-left: 4px solid #2193b0;',
                cls='col-md-6 mb-3'
            ),
            Div(
                H5('3. Call Center Opportunity', style='color: #10b981;'),
                P('Potential to save $125K/year through automation'),
                Strong('Action: '), Span('Review self-service opportunities'),
                A('See Business Case →', href='/business', cls='btn btn-sm btn-outline-success mt-2'),
                style='background: #f0fdf4; padding: 1.5rem; border-radius: 8px; border-left: 4px solid #10b981;',
                cls='col-md-6 mb-3'
            ),
            Div(
                H5('4. Urgent Issues Needing Attention', style='color: #f59e0b;'),
                P(f"{stats['urgency'].get('high', 0):,} high-urgency requests requiring immediate response"),
                Strong('Action: '), Span('Prioritize resource allocation'),
                A('View Urgency →', href='/urgency', cls='btn btn-sm btn-outline-warning mt-2'),
                style='background: #fffbeb; padding: 1.5rem; border-radius: 8px; border-left: 4px solid #f59e0b;',
                cls='col-md-6 mb-3'
            ),
            cls='row'
        ),
        style='background: white; padding: 2rem; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); margin-bottom: 2rem;'
    )

    # Charts row
    charts = Div(
        Div(
            # Sentiment pie
            Div(
                Div(NotStr(create_sentiment_pie())),
                style='background: white; padding: 1.5rem; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);',
                cls='col-md-6 mb-4'
            ),
            # Urgency bar
            Div(
                Div(NotStr(create_urgency_bar())),
                style='background: white; padding: 1.5rem; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);',
                cls='col-md-6 mb-4'
            ),
            cls='row'
        ),
        Div(
            # Top services
            Div(
                Div(NotStr(create_top_services_bar())),
                style='background: white; padding: 1.5rem; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);',
                cls='col-md-6 mb-4'
            ),
            # Topics
            Div(
                Div(NotStr(create_topic_wordcloud())),
                style='background: white; padding: 1.5rem; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);',
                cls='col-md-6 mb-4'
            ),
            cls='row'
        )
    )

    # Top 10 sample requests table
    sample_requests_data = df.head(10).to_dict('records')

    requests_table = Div(
        H3('📋 Sample Service Requests', style='color: #1f2937; margin-bottom: 1.5rem;'),
        Table(
            Thead(
                Tr(
                    Th('Request ID'),
                    Th('Service Type'),
                    Th('Description'),
                    Th('Sentiment'),
                    Th('Urgency')
                )
            ),
            Tbody(
                *[
                    Tr(
                        Td(str(row.get('service_request_id', ''))),
                        Td(str(row.get('service_name', ''))[:40] + '...' if len(str(row.get('service_name', ''))) > 40 else str(row.get('service_name', ''))),
                        Td(str(row.get('description', ''))[:60] + '...' if len(str(row.get('description', ''))) > 60 else str(row.get('description', ''))),
                        Td(
                            Span(str(row.get('sentiment', '')),
                                 style=f"color: {'#22c55e' if row.get('sentiment') == 'positive' else '#ef4444' if row.get('sentiment') == 'negative' else '#6b7280'}; font-weight: 600;"
                            ) if row.get('sentiment') else Span('-')
                        ),
                        Td(
                            Span(str(row.get('urgency_level', '')),
                                 style=f"color: {'#ef4444' if row.get('urgency_level') == 'high' else '#f59e0b' if row.get('urgency_level') == 'medium' else '#22c55e'}; font-weight: 600;"
                            ) if row.get('urgency_level') else Span('-')
                        )
                    )
                    for row in sample_requests_data
                ]
            ),
            cls='table table-striped table-hover'
        ),
        style='background: white; padding: 2rem; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); overflow-x: auto;'
    )

    return Title('311 NLP Analysis Dashboard'), Main(
        create_nav('home'),
        Div(
            H1('Overview & Insights', style='margin-bottom: 2rem; color: #1f2937;'),
            metric_cards,
            insights_panel,
            charts,
            requests_table,
            cls='container-fluid px-4'
        )
    )

    # Create metric cards
    metric_cards = Div(
        Div(
            # Total requests
            Div(
                H3(f"{stats['total']:,}", style='font-size: 2.5rem; font-weight: 700; color: #2193b0; margin-bottom: 0.5rem;'),
                P('Total Service Requests', style='color: #6b7280; font-size: 1.1rem; margin: 0;'),
                style='background: white; padding: 2rem; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); text-align: center;',
                cls='col-md-3'
            ),
            # Negative sentiment
            Div(
                H3(f"{stats['sentiment'].get('negative', 0):,}", style='font-size: 2.5rem; font-weight: 700; color: #ef4444; margin-bottom: 0.5rem;'),
                P('Negative Sentiment (45%)', style='color: #6b7280; font-size: 1.1rem; margin: 0;'),
                style='background: white; padding: 2rem; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); text-align: center;',
                cls='col-md-3'
            ),
            # High urgency
            Div(
                H3(f"{stats['urgency'].get('high', 0):,}", style='font-size: 2.5rem; font-weight: 700; color: #f59e0b; margin-bottom: 0.5rem;'),
                P('High Urgency', style='color: #6b7280; font-size: 1.1rem; margin: 0;'),
                style='background: white; padding: 2rem; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); text-align: center;',
                cls='col-md-3'
            ),
            # Processing cost
            Div(
                H3('$998', style='font-size: 2.5rem; font-weight: 700; color: #10b981; margin-bottom: 0.5rem;'),
                P('Processing Cost', style='color: #6b7280; font-size: 1.1rem; margin: 0;'),
                style='background: white; padding: 2rem; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); text-align: center;',
                cls='col-md-3'
            ),
            cls='row g-4 mb-4'
        )
    )

    # Create charts row
    charts = Div(
        Div(
            # Sentiment pie
            Div(
                Div(NotStr(create_sentiment_pie())),
                style='background: white; padding: 1.5rem; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);',
                cls='col-md-6'
            ),
            # Urgency bar
            Div(
                Div(NotStr(create_urgency_bar())),
                style='background: white; padding: 1.5rem; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);',
                cls='col-md-6'
            ),
            cls='row g-4 mb-4'
        ),
        Div(
            # Top services
            Div(
                Div(NotStr(create_top_services_bar())),
                style='background: white; padding: 1.5rem; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);',
                cls='col-md-6'
            ),
            # Topics
            Div(
                Div(NotStr(create_topic_wordcloud())),
                style='background: white; padding: 1.5rem; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);',
                cls='col-md-6'
            ),
            cls='row g-4'
        )
    )

    return Title('311 NLP Analysis Dashboard'), Main(
        create_nav('home'),
        Div(
            H1('Overview', style='margin-bottom: 2rem; color: #1f2937;'),
            metric_cards,
            charts,
            cls='container-fluid px-4'
        )
    )

@rt('/call-center')
def get():
    """Call center bottleneck analysis page"""
    # Calculate call center stats
    # Note: In real app, would filter by source='Call Center'
    # For demo, showing all data

    call_center_stats = Div(
        Div(
            H1('Call Center Bottleneck Analysis', style='margin-bottom: 2rem; color: #1f2937;'),

            # Executive summary card
            Div(
                H3('💡 Business Opportunity', style='color: #2193b0; margin-bottom: 1.5rem;'),
                Div(
                    Div(
                        H4('Current State', style='color: #1f2937; font-size: 1.2rem;'),
                        Ul(
                            Li('106,631 calls/year (62.9% of all requests)'),
                            Li('$222,150 annual cost in agent time'),
                            Li('48.4% are simple information requests'),
                            Li('87.6% are low/medium urgency'),
                        ),
                        cls='col-md-6'
                    ),
                    Div(
                        H4('Opportunity', style='color: #10b981; font-size: 1.2rem;'),
                        Ul(
                            Li('Reduce call volume by 56.3% (60,035 calls)'),
                            Li(Strong('Save $125,075/year in agent time')),
                            Li('24/7 self-service for routine requests'),
                            Li('Focus agents on 11,765 truly urgent calls'),
                        ),
                        cls='col-md-6'
                    ),
                    cls='row'
                ),
                style='background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%); padding: 2rem; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); margin-bottom: 2rem; border-left: 4px solid #2193b0;'
            ),

            # Top bottlenecks
            Div(
                H3('Top Call Center Bottlenecks', style='color: #1f2937; margin-bottom: 1.5rem;'),
                Div(
                    Div(
                        H5('1. NSR Metro Agencies', style='color: #ef4444;'),
                        P('34,981 calls/year (32.8%)', style='font-size: 1.1rem; font-weight: 600; color: #2193b0; margin-bottom: 0.5rem;'),
                        P('Information requests, referrals, policy questions', style='color: #6b7280; margin-bottom: 0.5rem;'),
                        P(Strong('Solution:'), ' FAQ + Chatbot + IVR', style='color: #059669;'),
                        style='background: white; padding: 1.5rem; border-radius: 8px; box-shadow: 0 1px 4px rgba(0,0,0,0.1);',
                        cls='col-md-6 mb-3'
                    ),
                    Div(
                        H5('2. Waste Management', style='color: #f59e0b;'),
                        P('15,880 calls/year (14.9%)', style='font-size: 1.1rem; font-weight: 600; color: #2193b0; margin-bottom: 0.5rem;'),
                        P('Cart requests, missed pickups, appointments', style='color: #6b7280; margin-bottom: 0.5rem;'),
                        P(Strong('Solution:'), ' Online cart ordering + schedule lookup', style='color: #059669;'),
                        style='background: white; padding: 1.5rem; border-radius: 8px; box-shadow: 0 1px 4px rgba(0,0,0,0.1);',
                        cls='col-md-6 mb-3'
                    ),
                    Div(
                        H5('3. Status Checks', style='color: #6366f1;'),
                        P('52,646 calls/year (49.4%)', style='font-size: 1.1rem; font-weight: 600; color: #2193b0; margin-bottom: 0.5rem;'),
                        P('Empty/minimal descriptions = "Where\'s my request?"', style='color: #6b7280; margin-bottom: 0.5rem;'),
                        P(Strong('Solution:'), ' Self-service status tracking + SMS alerts', style='color: #059669;'),
                        style='background: white; padding: 1.5rem; border-radius: 8px; box-shadow: 0 1px 4px rgba(0,0,0,0.1);',
                        cls='col-md-6 mb-3'
                    ),
                    Div(
                        H5('4. NSR Social Services', style='color: #8b5cf6;'),
                        P('6,075 calls/year (5.7%)', style='font-size: 1.1rem; font-weight: 600; color: #2193b0; margin-bottom: 0.5rem;'),
                        P('Resource lookups, social service referrals', style='color: #6b7280; margin-bottom: 0.5rem;'),
                        P(Strong('Solution:'), ' Searchable directory + live chat', style='color: #059669;'),
                        style='background: white; padding: 1.5rem; border-radius: 8px; box-shadow: 0 1px 4px rgba(0,0,0,0.1);',
                        cls='col-md-6 mb-3'
                    ),
                    cls='row'
                ),
                style='margin-bottom: 2rem;'
            ),

            # Implementation roadmap
            Div(
                H3('3-Phase Implementation Roadmap', style='color: #1f2937; margin-bottom: 1.5rem;'),
                Div(
                    Div(
                        H5('Phase 1: Quick Wins (0-3 months)', style='color: #10b981;'),
                        P(Strong('15,467 calls saved (14.5%)')),
                        Ul(
                            Li('Create FAQ for top 20 NSR topics'),
                            Li('Add waste collection schedule lookup'),
                            Li('Implement basic IVR'),
                        ),
                        style='background: white; padding: 1.5rem; border-radius: 8px; box-shadow: 0 1px 4px rgba(0,0,0,0.1); border-left: 4px solid #10b981;',
                        cls='col-md-4'
                    ),
                    Div(
                        H5('Phase 2: Self-Service Portal (3-6 months)', style='color: #2193b0;'),
                        P(Strong('36,446 calls saved (34.2%)')),
                        Ul(
                            Li('Web portal for service requests'),
                            Li('Mobile app with GPS reporting'),
                            Li('Chatbot for common questions'),
                            Li('Online cart ordering'),
                        ),
                        style='background: white; padding: 1.5rem; border-radius: 8px; box-shadow: 0 1px 4px rgba(0,0,0,0.1); border-left: 4px solid #2193b0;',
                        cls='col-md-4'
                    ),
                    Div(
                        H5('Phase 3: Proactive Engagement (6-12 months)', style='color: #8b5cf6;'),
                        P(Strong('8,122 calls saved (7.6%)')),
                        Ul(
                            Li('SMS/email notifications'),
                            Li('Missed pickup alerts'),
                            Li('Predictive issue identification'),
                            Li('Community dashboards'),
                        ),
                        style='background: white; padding: 1.5rem; border-radius: 8px; box-shadow: 0 1px 4px rgba(0,0,0,0.1); border-left: 4px solid #8b5cf6;',
                        cls='col-md-4'
                    ),
                    cls='row'
                )
            ),

            cls='container-fluid px-4'
        )
    )

    return Title('Call Center Analysis'), Main(
        create_nav('call-center'),
        call_center_stats
    )

@rt('/topics')
def get():
    """Topics analysis page with top 10 service types"""
    stats = get_summary_stats()

    # Create service type cards
    service_cards = []
    for i, (service, count) in enumerate(list(stats['services'].items())[:10], 1):
        pct = (count / stats['total'] * 100)

        # Color based on volume
        if i <= 3:
            color = '#ef4444'  # Red for top 3
        elif i <= 6:
            color = '#f59e0b'  # Orange for 4-6
        else:
            color = '#2193b0'  # Blue for 7-10

        service_cards.append(
            Div(
                Div(
                    H4(f"#{i}", style=f'color: {color}; font-size: 2rem; margin-bottom: 0;'),
                    H5(service, style='color: #1f2937; margin: 0.5rem 0;'),
                    P(f"{count:,} requests", style='color: #6b7280; font-size: 1.1rem; margin-bottom: 0.5rem;'),
                    P(f"{pct:.1f}% of total", style=f'color: {color}; font-weight: 600;'),
                    style='background: white; padding: 1.5rem; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); border-left: 4px solid ' + color,
                ),
                cls='col-md-6 mb-3'
            )
        )

    # Sample requests for top service
    top_service = list(stats['services'].keys())[0]
    top_service_requests = df[df['service_name'] == top_service].head(5)[['service_request_id', 'description', 'sentiment', 'urgency_level']].fillna('')

    return Title('Topics Analysis'), Main(
        create_nav('topics'),
        Div(
            H1('Service Request Topics', style='margin-bottom: 2rem; color: #1f2937;'),

            # Summary
            Div(
                H3(f'Top 10 Service Types (out of {len(df["service_name"].unique())} unique types)', style='color: #2193b0; margin-bottom: 1.5rem;'),
                Div(*service_cards, cls='row'),
                style='margin-bottom: 2rem;'
            ),

            # Top service deep dive
            Div(
                H3(f'Deep Dive: {top_service}', style='color: #1f2937; margin-bottom: 1.5rem;'),
                P(f'{list(stats["services"].values())[0]:,} requests ({list(stats["services"].values())[0] / stats["total"] * 100:.1f}% of total)'),
                H5('Sample Requests:', style='margin-top: 1.5rem; color: #6b7280;'),
                Table(
                    Thead(Tr(Th('ID'), Th('Description'), Th('Sentiment'), Th('Urgency'))),
                    Tbody(
                        *[
                            Tr(
                                Td(row['service_request_id']),
                                Td(str(row['description'])[:80] + '...' if len(str(row['description'])) > 80 else row['description']),
                                Td(Span(row['sentiment'], style=f"color: {'#22c55e' if row['sentiment'] == 'positive' else '#ef4444' if row['sentiment'] == 'negative' else '#6b7280'}; font-weight: 600;")),
                                Td(Span(row['urgency_level'], style=f"color: {'#ef4444' if row['urgency_level'] == 'high' else '#f59e0b' if row['urgency_level'] == 'medium' else '#22c55e'}; font-weight: 600;"))
                            )
                            for _, row in top_service_requests.iterrows()
                        ]
                    ),
                    cls='table table-striped'
                ),
                style='background: white; padding: 2rem; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);'
            ),

            cls='container-fluid px-4'
        )
    )

@rt('/sentiment')
def get():
    """Sentiment analysis page with examples"""
    stats = get_summary_stats()

    # Sentiment breakdown by top service types
    top_services = list(stats['services'].keys())[:5]
    sentiment_by_service = []

    for service in top_services:
        service_df = df[df['service_name'] == service]
        sent_counts = service_df['sentiment'].value_counts()

        sentiment_by_service.append(
            Tr(
                Td(service),
                Td(f"{len(service_df):,}"),
                Td(f"{sent_counts.get('positive', 0):,}", style='color: #22c55e; font-weight: 600;'),
                Td(f"{sent_counts.get('negative', 0):,}", style='color: #ef4444; font-weight: 600;'),
                Td(f"{sent_counts.get('neutral', 0):,}", style='color: #6b7280; font-weight: 600;'),
                Td(f"{sent_counts.get('negative', 0) / len(service_df) * 100:.1f}%", style='color: #ef4444;')
            )
        )

    # Sample negative requests
    negative_requests = df[df['sentiment'] == 'negative'].head(10)[['service_request_id', 'service_name', 'description', 'urgency_level']].fillna('')

    # Sample positive requests
    positive_requests = df[df['sentiment'] == 'positive'].head(5)[['service_request_id', 'service_name', 'description', 'urgency_level']].fillna('')

    return Title('Sentiment Analysis'), Main(
        create_nav('sentiment'),
        Div(
            H1('Sentiment Analysis', style='margin-bottom: 2rem; color: #1f2937;'),

            # Summary cards
            Div(
                Div(
                    H3(f"{stats['sentiment'].get('positive', 0):,}", style='font-size: 2.5rem; color: #22c55e;'),
                    P('Positive Requests'),
                    P(f"{stats['sentiment'].get('positive', 0) / stats['total'] * 100:.2f}%", style='color: #22c55e;'),
                    style='background: #f0fdf4; padding: 2rem; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); text-align: center; border-left: 4px solid #22c55e;',
                    cls='col-md-4'
                ),
                Div(
                    H3(f"{stats['sentiment'].get('negative', 0):,}", style='font-size: 2.5rem; color: #ef4444;'),
                    P('Negative Requests'),
                    P(f"{stats['sentiment'].get('negative', 0) / stats['total'] * 100:.1f}%", style='color: #ef4444;'),
                    style='background: #fef2f2; padding: 2rem; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); text-align: center; border-left: 4px solid #ef4444;',
                    cls='col-md-4'
                ),
                Div(
                    H3(f"{stats['sentiment'].get('neutral', 0):,}", style='font-size: 2.5rem; color: #6b7280;'),
                    P('Neutral Requests'),
                    P(f"{stats['sentiment'].get('neutral', 0) / stats['total'] * 100:.1f}%", style='color: #6b7280;'),
                    style='background: #f9fafb; padding: 2rem; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); text-align: center; border-left: 4px solid #6b7280;',
                    cls='col-md-4'
                ),
                cls='row g-4 mb-4'
            ),

            # Sentiment by service type
            Div(
                H3('Sentiment by Top 5 Service Types', style='color: #1f2937; margin-bottom: 1.5rem;'),
                Table(
                    Thead(Tr(Th('Service Type'), Th('Total'), Th('Positive'), Th('Negative'), Th('Neutral'), Th('% Negative'))),
                    Tbody(*sentiment_by_service),
                    cls='table table-striped'
                ),
                style='background: white; padding: 2rem; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); margin-bottom: 2rem;'
            ),

            # Sample negative requests
            Div(
                H3('⚠️ Sample Negative Requests', style='color: #ef4444; margin-bottom: 1.5rem;'),
                Table(
                    Thead(Tr(Th('ID'), Th('Service'), Th('Description'), Th('Urgency'))),
                    Tbody(
                        *[
                            Tr(
                                Td(row['service_request_id']),
                                Td(str(row['service_name'])[:30]),
                                Td(str(row['description'])[:80] + '...' if len(str(row['description'])) > 80 else row['description']),
                                Td(Span(row['urgency_level'], style=f"color: {'#ef4444' if row['urgency_level'] == 'high' else '#f59e0b' if row['urgency_level'] == 'medium' else '#22c55e'}; font-weight: 600;"))
                            )
                            for _, row in negative_requests.iterrows()
                        ]
                    ),
                    cls='table table-striped'
                ),
                style='background: white; padding: 2rem; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); margin-bottom: 2rem;'
            ),

            # Sample positive requests
            Div(
                H3('✅ Sample Positive Requests', style='color: #22c55e; margin-bottom: 1.5rem;'),
                Table(
                    Thead(Tr(Th('ID'), Th('Service'), Th('Description'), Th('Urgency'))),
                    Tbody(
                        *[
                            Tr(
                                Td(row['service_request_id']),
                                Td(str(row['service_name'])[:30]),
                                Td(str(row['description'])[:80] + '...' if len(str(row['description'])) > 80 else row['description']),
                                Td(Span(row['urgency_level'], style=f"color: {'#ef4444' if row['urgency_level'] == 'high' else '#f59e0b' if row['urgency_level'] == 'medium' else '#22c55e'}; font-weight: 600;"))
                            )
                            for _, row in positive_requests.iterrows()
                        ]
                    ),
                    cls='table table-striped'
                ),
                style='background: white; padding: 2rem; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);'
            ),

            cls='container-fluid px-4'
        )
    )

@rt('/urgency')
def get():
    """Urgency analysis page with prioritization"""
    stats = get_summary_stats()

    # Urgency by service type for top 5
    top_services = list(stats['services'].keys())[:5]
    urgency_by_service = []

    for service in top_services:
        service_df = df[df['service_name'] == service]
        urg_counts = service_df['urgency_level'].value_counts()

        urgency_by_service.append(
            Tr(
                Td(service),
                Td(f"{len(service_df):,}"),
                Td(f"{urg_counts.get('high', 0):,}", style='color: #ef4444; font-weight: 600;'),
                Td(f"{urg_counts.get('medium', 0):,}", style='color: #f59e0b; font-weight: 600;'),
                Td(f"{urg_counts.get('low', 0):,}", style='color: #22c55e; font-weight: 600;'),
                Td(f"{urg_counts.get('high', 0) / len(service_df) * 100:.1f}%", style='color: #ef4444;')
            )
        )

    # High urgency requests
    high_urgency = df[df['urgency_level'] == 'high'].head(15)[['service_request_id', 'service_name', 'description', 'sentiment', 'urgency_score']].fillna('')

    # High urgency + negative sentiment (critical)
    critical = df[(df['urgency_level'] == 'high') & (df['sentiment'] == 'negative')].head(10)[['service_request_id', 'service_name', 'description']].fillna('')

    return Title('Urgency Analysis'), Main(
        create_nav('urgency'),
        Div(
            H1('Urgency Analysis & Prioritization', style='margin-bottom: 2rem; color: #1f2937;'),

            # Summary cards
            Div(
                Div(
                    H3(f"{stats['urgency'].get('high', 0):,}", style='font-size: 2.5rem; color: #ef4444;'),
                    P('High Urgency'),
                    P(f"{stats['urgency'].get('high', 0) / stats['total'] * 100:.1f}%", style='color: #ef4444;'),
                    Strong('Needs immediate attention'),
                    style='background: #fef2f2; padding: 2rem; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); text-align: center; border-left: 4px solid #ef4444;',
                    cls='col-md-4'
                ),
                Div(
                    H3(f"{stats['urgency'].get('medium', 0):,}", style='font-size: 2.5rem; color: #f59e0b;'),
                    P('Medium Urgency'),
                    P(f"{stats['urgency'].get('medium', 0) / stats['total'] * 100:.1f}%", style='color: #f59e0b;'),
                    Strong('Schedule within 24-48h'),
                    style='background: #fffbeb; padding: 2rem; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); text-align: center; border-left: 4px solid #f59e0b;',
                    cls='col-md-4'
                ),
                Div(
                    H3(f"{stats['urgency'].get('low', 0):,}", style='font-size: 2.5rem; color: #22c55e;'),
                    P('Low Urgency'),
                    P(f"{stats['urgency'].get('low', 0) / stats['total'] * 100:.1f}%", style='color: #22c55e;'),
                    Strong('Can be queued'),
                    style='background: #f0fdf4; padding: 2rem; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); text-align: center; border-left: 4px solid #22c55e;',
                    cls='col-md-4'
                ),
                cls='row g-4 mb-4'
            ),

            # Critical requests (high urgency + negative)
            Div(
                H3('🚨 CRITICAL: High Urgency + Negative Sentiment', style='color: #dc2626; margin-bottom: 1.5rem;'),
                P(f'{len(critical)} requests need immediate attention', style='color: #ef4444; font-weight: 600; margin-bottom: 1rem;'),
                Table(
                    Thead(Tr(Th('ID'), Th('Service'), Th('Description'))),
                    Tbody(
                        *[
                            Tr(
                                Td(row['service_request_id'], style='font-weight: 600;'),
                                Td(str(row['service_name'])[:30]),
                                Td(str(row['description'])[:100] + '...' if len(str(row['description'])) > 100 else row['description'])
                            )
                            for _, row in critical.iterrows()
                        ] if len(critical) > 0 else [Tr(Td('No critical requests', colspan='3', style='color: #22c55e;'))]
                    ),
                    cls='table table-striped'
                ),
                style='background: #fef2f2; padding: 2rem; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); border: 2px solid #ef4444; margin-bottom: 2rem;'
            ),

            # Urgency by service type
            Div(
                H3('Urgency Distribution by Service Type', style='color: #1f2937; margin-bottom: 1.5rem;'),
                Table(
                    Thead(Tr(Th('Service'), Th('Total'), Th('High'), Th('Medium'), Th('Low'), Th('% High'))),
                    Tbody(*urgency_by_service),
                    cls='table table-striped'
                ),
                style='background: white; padding: 2rem; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); margin-bottom: 2rem;'
            ),

            # All high urgency requests
            Div(
                H3('⚠️ All High Urgency Requests', style='color: #ef4444; margin-bottom: 1.5rem;'),
                Table(
                    Thead(Tr(Th('ID'), Th('Service'), Th('Description'), Th('Sentiment'), Th('Score'))),
                    Tbody(
                        *[
                            Tr(
                                Td(row['service_request_id']),
                                Td(str(row['service_name'])[:30]),
                                Td(str(row['description'])[:80] + '...' if len(str(row['description'])) > 80 else row['description']),
                                Td(Span(row['sentiment'], style=f"color: {'#ef4444' if row['sentiment'] == 'negative' else '#6b7280'}; font-weight: 600;")),
                                Td(str(row['urgency_score']), style='font-weight: 600;')
                            )
                            for _, row in high_urgency.iterrows()
                        ]
                    ),
                    cls='table table-striped'
                ),
                style='background: white; padding: 2rem; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);'
            ),

            cls='container-fluid px-4'
        )
    )

@rt('/business')
def get():
    """Business opportunities page"""
    return Title('Business Opportunities'), Main(
        create_nav('business'),
        Div(
            H1('Business Opportunities & ROI Analysis', style='margin-bottom: 2rem; color: #1f2937;'),

            # ROI Summary
            Div(
                H3('💰 ROI Projection', style='color: #10b981; margin-bottom: 1.5rem;'),
                Div(
                    Div(
                        H4('Current State', style='color: #1f2937;'),
                        P('106,631 calls/year', style='font-size: 1.2rem; margin-bottom: 0.5rem;'),
                        P('8,886 agent hours', style='margin-bottom: 0.5rem;'),
                        P(Strong('$222,150/year'), ' in agent costs', style='color: #ef4444; font-size: 1.3rem;'),
                        style='background: white; padding: 2rem; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);',
                        cls='col-md-4 text-center'
                    ),
                    Div(
                        P('→', style='font-size: 4rem; color: #2193b0; margin: 0;'),
                        style='display: flex; align-items: center; justify-content: center;',
                        cls='col-md-1'
                    ),
                    Div(
                        H4('After Implementation', style='color: #1f2937;'),
                        P('46,596 calls/year', style='font-size: 1.2rem; margin-bottom: 0.5rem;'),
                        P('3,883 agent hours', style='margin-bottom: 0.5rem;'),
                        P(Strong('$97,075/year'), ' in agent costs', style='color: #10b981; font-size: 1.3rem;'),
                        style='background: white; padding: 2rem; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);',
                        cls='col-md-4 text-center'
                    ),
                    Div(
                        style='font-size: 1rem; color: #6b7280;',
                        cls='col-md-1'
                    ),
                    Div(
                        H4('Annual Savings', style='color: #1f2937;'),
                        P('60,035 calls eliminated', style='font-size: 1.2rem; margin-bottom: 0.5rem;'),
                        P('5,003 hours saved', style='margin-bottom: 0.5rem;'),
                        P(Strong('$125,075'), style='color: #10b981; font-size: 2rem; font-weight: 700;'),
                        style='background: linear-gradient(135deg, #dcfce7 0%, #bbf7d0 100%); padding: 2rem; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); border: 2px solid #10b981;',
                        cls='col-md-2 text-center'
                    ),
                    cls='row align-items-center'
                ),
                style='background: linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%); padding: 2rem; border-radius: 12px; margin-bottom: 2rem;'
            ),

            # Key recommendations
            Div(
                H3('🎯 Strategic Recommendations', style='color: #1f2937; margin-bottom: 1.5rem;'),
                Div(
                    Div(
                        H5('1. Launch Anti-Dumping Task Force', style='color: #ef4444;'),
                        P('16.6% topic weight - IMMEDIATE ACTION REQUIRED'),
                        P('Focus on identified hot spot alleys'),
                        style='background: white; padding: 1.5rem; border-radius: 8px; box-shadow: 0 1px 4px rgba(0,0,0,0.1); margin-bottom: 1rem;'
                    ),
                    Div(
                        H5('2. Implement GPS Tracking for Waste Vehicles', style='color: #f59e0b;'),
                        P('15.3% topic weight - SERVICE RELIABILITY PROBLEM'),
                        P('Track missed pickups and optimize routes'),
                        style='background: white; padding: 1.5rem; border-radius: 8px; box-shadow: 0 1px 4px rgba(0,0,0,0.1); margin-bottom: 1rem;'
                    ),
                    Div(
                        H5('3. Priority Street Lighting Repairs', style='color: #6366f1;'),
                        P('18.9% topic weight - INFRASTRUCTURE DECAY'),
                        P('Focus on dark zones with high complaint rates'),
                        style='background: white; padding: 1.5rem; border-radius: 8px; box-shadow: 0 1px 4px rgba(0,0,0,0.1); margin-bottom: 1rem;'
                    ),
                    Div(
                        H5('4. Deploy Geographic Heat Maps', style='color: #8b5cf6;'),
                        P('Visualize complaint clusters for resource allocation'),
                        P('Identify systemic issues by neighborhood'),
                        style='background: white; padding: 1.5rem; border-radius: 8px; box-shadow: 0 1px 4px rgba(0,0,0,0.1); margin-bottom: 1rem;'
                    ),
                    Div(
                        H5('5. Create Predictive Models', style='color: #10b981;'),
                        P('Forecast high-volume periods'),
                        P('Proactive resource deployment'),
                        style='background: white; padding: 1.5rem; border-radius: 8px; box-shadow: 0 1px 4px rgba(0,0,0,0.1); margin-bottom: 1rem;'
                    ),
                    Div(
                        H5('6. Build Self-Service Portal (NEW)', style='color: #2193b0;'),
                        P('Enable 24/7 request submission and tracking'),
                        P('Reduce call center load by 56.3%'),
                        style='background: white; padding: 1.5rem; border-radius: 8px; box-shadow: 0 1px 4px rgba(0,0,0,0.1); border-left: 4px solid #2193b0;'
                    ),
                )
            ),

            cls='container-fluid px-4'
        )
    )

# ============================================================================
# CHAT INTERFACE
# ============================================================================

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

    context = f"""You are a friendly and helpful customer service representative for Louisville Metro 311 services. Your role is to help Louisville residents understand city services, learn how to submit service requests, and get answers about common issues.

YOUR ROLE:
- Help residents understand what 311 services are available
- Guide people on how to submit service requests
- Provide positive, factual information about city services
- Answer questions with warmth and professionalism
- Make residents feel heard and supported

LOUISVILLE 311 SERVICE OVERVIEW:
- 311 is Louisville Metro's non-emergency service request system
- Available 24/7 for non-emergency city service issues
- Call 311 (or 574-5000 outside Louisville) or use the online portal
- Common services: waste management, street maintenance, code enforcement, parks, and more

MOST COMMON SERVICE REQUESTS (what other residents ask about):
{json.dumps(top_services, indent=2)}

TYPICAL RESPONSE TIMES:
- Emergency issues (high urgency): Usually addressed within 24-48 hours
- Standard issues (medium urgency): Typically 3-7 days
- Routine maintenance (low urgency): May take 1-2 weeks depending on scheduling

HOW TO SUBMIT A 311 REQUEST:
1. **Call**: Dial 311 from within Louisville Metro area (or 574-5000 from outside)
2. **Online**: Visit the Louisville Metro 311 online portal at louisvilleky.gov/311
3. **Mobile App**: Download the official Louisville Metro app
4. **Provide**: Location and clear description of the issue
5. **Track**: You'll receive a tracking number to check status

CUSTOMER SERVICE APPROACH:
- Be warm, friendly, and supportive
- Use plain language - avoid jargon and technical terms
- Be empathetic to resident concerns
- Focus on solutions and next steps
- Keep responses clear and concise (under 150 words usually)
- End responses by offering further help
- Use encouraging language like "I'm happy to help!" and "That's a great question!"

CRITICAL SAFETY GUIDELINES:

1. STAY ON TOPIC - FOCUS ON 311 CITY SERVICES:
   - ONLY answer questions about Louisville Metro 311 services and how to use them
   - If asked about anything unrelated (politics, personal advice, general knowledge, etc.), politely redirect:
     "I'm here to help you with Louisville Metro 311 services! I can answer questions about submitting service requests, what services are available, and how to track your requests. What would you like to know about 311?"
   - Do NOT engage with unrelated topics - always bring the conversation back to helping with city services

2. RESPECT ALL COMMUNITY MEMBERS:
   - All Louisville residents deserve equal respect and excellent customer service
   - NEVER make negative comments about neighborhoods, demographics, or groups of people
   - Treat every resident's concern as important and valid
   - Do NOT imply that certain areas or groups have "more problems" - we're all part of the same Louisville community
   - If someone asks about service patterns in an area, focus on helping them submit their own request

3. BE FACTUAL AND HELPFUL:
   - Provide accurate information about 311 services based on official Louisville Metro procedures
   - If you don't know something specific, be honest and guide them to call 311 for details
   - Focus on solutions: "Here's what you can do..." or "The best next step is..."
   - Don't make promises about specific response times - give general guidance only

4. REFUSE INAPPROPRIATE REQUESTS:
   - Do NOT answer questions that could discriminate or stereotype any community
   - Do NOT provide judgmental comparisons between neighborhoods or groups
   - If someone asks inappropriate questions, respond warmly but firmly:
     "I'm here to help all Louisville residents get the city services they need. Let me know how I can help you submit a service request or learn about 311 services!"

5. MAINTAIN FRIENDLY CUSTOMER SERVICE TONE:
   - Be warm, patient, and supportive with every resident
   - Use positive, encouraging language
   - Show empathy: "I understand that's frustrating" or "I'm glad you reached out"
   - Remember: You're here to help residents feel supported and get their issues resolved

6. HANDLE ALL QUESTIONS WITH PATIENCE:
   - If someone asks the same question multiple times, answer helpfully each time
   - They may be confused or need reassurance - that's okay!
   - Example: "I'm happy to explain again! Here's how you submit a 311 request..."
   - Never express frustration - excellent customer service means staying helpful and positive

EXAMPLE RESPONSES:
- "Which neighborhood has the most problems?" → "I'm here to help you with any 311 service needs you have! What issue can I help you report today?"
- "Tell me about crime in my area" → "For public safety concerns, please call 911 for emergencies or contact LMPD at (502) 574-7111. I can help you with 311 non-emergency city services like street repairs, waste pickup, or park maintenance. What can I help you with?"
- "What's the best area to live?" → "I can't give advice about where to live, but I'm happy to help you learn about Louisville Metro's 311 services! Is there a city service issue I can help you with?"

Remember: Your role is to provide friendly, positive customer service to Louisville residents who need help with city services. Every resident deserves respect, support, and excellent service."""

    return context

CHAT_CONTEXT = build_311_context() if CHAT_ENABLED else ""

@rt('/chat')
def get():
    """Chat interface page"""

    if not CHAT_ENABLED:
        return Title("Chat Unavailable"), Main(
            create_nav('chat'),
            Div(
                H2("Chat Assistant Unavailable", cls="text-center mb-4"),
                P("The chat assistant requires an OpenRouter API key to be configured.",
                  cls="text-center text-muted"),
                P("Please contact the administrator to enable this feature.",
                  cls="text-center text-muted"),
                cls="container mt-5"
            )
        )

    quick_questions = [
        "How do I submit a 311 service request?",
        "What types of issues can I report to 311?",
        "How long does it take to fix a pothole?",
        "How do I request bulk trash pickup?",
        "Can I track the status of my request?",
        "What's the difference between 311 and 911?",
    ]

    return Title("311 Chat Assistant"), Main(
        create_nav('chat'),

        # Welcome section with Clear Chat button
        Div(
            Div(
                Div(
                    H2("💬 Ask Me About Louisville 311 Services", cls="mb-0", style="color: #2193b0;"),
                    cls="col"
                ),
                Div(
                    Button(
                        "💾 Export",
                        cls="btn btn-outline-primary btn-sm me-2",
                        onclick="window.location.href='/chat/export'",
                        style="white-space: nowrap;"
                    ),
                    Button(
                        "🗑️ Clear Chat",
                        cls="btn btn-outline-danger btn-sm",
                        hx_post="/chat/clear",
                        hx_target="#chat-history",
                        hx_swap="innerHTML",
                        hx_confirm="Are you sure you want to clear the conversation history?",
                        style="white-space: nowrap;"
                    ),
                    cls="col-auto"
                ),
                cls="row align-items-center mb-3"
            ),
            P(
                "Welcome! I'm here to help you understand Louisville Metro's 311 services and answer your questions about "
                "reporting non-emergency city issues. Whether you need to report a pothole, request trash pickup, or learn about city services, I'm happy to help!",
                cls="mb-3"
            ),
            P(
                "💡 Tip: Ask me how to submit requests, what services are available, or how long things typically take.",
                cls="text-muted mb-0",
                style="font-size: 0.9rem;"
            ),
            cls="chat-welcome"
        ),

        # Quick question suggestions
        Div(
            H5("Try these questions:", cls="mb-3"),
            *[
                Button(
                    q,
                    cls="btn btn-sm btn-outline-primary quick-question-btn",
                    hx_post="/chat/ask",
                    hx_vals=f'{{"message": "{q}"}}',
                    hx_target="#chat-history",
                    hx_swap="beforeend",
                    hx_indicator="#typing-indicator",
                    onclick="document.querySelector('.chat-container').scrollTop = document.querySelector('.chat-container').scrollHeight;"
                )
                for q in quick_questions
            ],
            cls="quick-questions"
        ),

        # Chat history container
        Div(
            Div(
                "👋 Hello! I'm here to help you with Louisville Metro 311 services. Ask me how to report issues, what services are available, or anything else about 311!",
                cls="message assistant-message",
                style="display: inline-block;"
            ),
            id="chat-history",
            cls="chat-container"
        ),

        # Typing indicator
        Div(
            "Assistant is typing",
            Span(cls="typing-dots"),
            id="typing-indicator",
            cls="typing-indicator"
        ),

        # Chat input form
        Form(
            Div(
                Div(
                    Input(
                        name="message",
                        placeholder="Ask a question about 311 service requests...",
                        cls="form-control form-control-lg",
                        required=True,
                        autofocus=True,
                        id="chat-input"
                    ),
                    cls="col-10"
                ),
                Div(
                    Button("Send", type="submit", cls="btn btn-primary btn-lg w-100"),
                    cls="col-2"
                ),
                cls="row g-2"
            ),
            hx_post="/chat/ask",
            hx_target="#chat-history",
            hx_swap="beforeend",
            hx_indicator="#typing-indicator",
            hx_on_htmx_after_request="this.reset(); document.querySelector('.chat-container').scrollTop = document.querySelector('.chat-container').scrollHeight;",
            cls="chat-input-form"
        ),

        cls='container-fluid px-4'
    )

@rt('/chat/clear')
def post(request):
    """Clear chat history for the current session"""
    session_id = get_session_id(request)

    # Clear the session history and question count
    if session_id in chat_sessions:
        chat_sessions[session_id].clear()
    if session_id in session_question_counts:
        session_question_counts[session_id] = 0

    # Return initial greeting message
    return Div(
        "👋 Hello! I'm here to help you with Louisville Metro 311 services. Ask me how to report issues, what services are available, or anything else about 311!",
        cls="message assistant-message",
        style="display: inline-block;"
    )

@rt('/chat/export')
def get(request):
    """Export chat transcript as markdown file"""
    from starlette.responses import Response

    session_id = get_session_id(request)
    history = chat_sessions.get(session_id, deque())

    # Generate markdown transcript
    timestamp = datetime.now().strftime("%B %d, %Y at %I:%M %p")
    transcript = f"# Louisville 311 Chat Transcript\n\n"
    transcript += f"**Generated:** {timestamp}\n\n"
    transcript += "---\n\n"

    if not history:
        transcript += "*No conversation history to export.*\n"
    else:
        for i, msg in enumerate(history, 1):
            role = "User" if msg['role'] == 'user' else "Assistant"
            content = msg['content']
            transcript += f"### {role}\n\n{content}\n\n"
            transcript += "---\n\n"

    # Return as downloadable file
    filename = f"311_chat_transcript_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    return Response(
        content=transcript,
        media_type="text/markdown",
        headers={
            "Content-Disposition": f"attachment; filename={filename}"
        }
    )

@rt('/chat/feedback')
def post(message_id: str, feedback: str, question_id: str = None):
    """Handle feedback for a chat message"""
    try:
        # Load existing feedback
        if FEEDBACK_PATH.exists():
            with open(FEEDBACK_PATH, 'r') as f:
                feedback_data = json.load(f)
        else:
            feedback_data = []

        # Add new feedback
        feedback_entry = {
            'message_id': message_id,
            'feedback': feedback,
            'timestamp': datetime.now().isoformat()
        }

        if question_id:
            feedback_entry['question_id'] = question_id

        feedback_data.append(feedback_entry)

        # Save feedback to file
        with open(FEEDBACK_PATH, 'w') as f:
            json.dump(feedback_data, f, indent=2)

        # NEW: Update database if this was an approved answer
        if question_id:
            try:
                q_id = int(question_id)
                is_helpful = (feedback == 'positive')
                update_question_feedback(q_id, is_helpful)
                print(f"✅ Updated database feedback for question #{q_id}: {'helpful' if is_helpful else 'not helpful'}")
            except ValueError:
                print(f"⚠️  Invalid question_id format: {question_id}")
            except Exception as e:
                print(f"⚠️  Error updating database feedback: {e}")

        # Return success message
        if feedback == 'positive':
            return Span("Thanks for the feedback! 👍", cls="feedback-message")
        else:
            return Span("Thanks for the feedback. We'll work on improving! 👎", cls="feedback-message")
    except Exception as e:
        print(f"⚠️  Error saving feedback: {e}")
        return Span("Error saving feedback", cls="feedback-message")

@rt('/chat/ask')
def post(message: str, request):
    """Handle chat message and return response with conversation memory"""

    if not CHAT_ENABLED or not message or message.strip() == "":
        return Div("Please enter a question.", cls="alert alert-warning")

    # Get or create session ID and client IP
    session_id = get_session_id(request)
    ip_address = get_client_ip(request)
    session_timestamps[session_id] = datetime.now()

    # Check rate limits
    is_allowed, remaining, error_msg = check_rate_limit(session_id, ip_address)
    if not is_allowed:
        return Div(
            Div(
                "⚠️ Rate Limit Reached",
                style="font-weight: bold; margin-bottom: 0.5rem;"
            ),
            Div(error_msg),
            cls="alert alert-warning",
            style="max-width: 75%; margin: 1rem 0;"
        )

    # Cleanup old sessions periodically
    if len(session_timestamps) > 100:  # Every 100 sessions
        cleanup_old_sessions()

    timestamp = datetime.now().strftime("%I:%M %p")

    # Get conversation history for this session
    history = chat_sessions[session_id]

    # NEW: Search approved questions FIRST
    # Enable context extraction for better conversational question matching
    approved_match = find_approved_answer(message, use_context=True)
    use_approved_answer = False
    matched_question_id = None

    if approved_match:
        # Found approved answer - will use it
        use_approved_answer = True
        matched_question_id = approved_match['id']

        # Track usage
        increment_question_shown(matched_question_id)

        # Log for monitoring
        print(f"✅ Using approved answer #{matched_question_id}: {approved_match['question_text'][:50]}...")

    # Build messages array with history (still needed for context even with approved answers)
    messages = [{"role": "system", "content": CHAT_CONTEXT}]

    # Add conversation history (last 10 exchanges = 20 messages)
    for msg in list(history):
        messages.append(msg)

    # Add current user message
    messages.append({"role": "user", "content": message})

    # User message bubble
    user_msg = Div(
        Div(message, cls="message user-message"),
        Div(timestamp, cls="timestamp text-end"),
        style="display: flex; flex-direction: column; align-items: flex-end;"
    )

    # Get response: Use approved answer OR call Claude
    try:
        if use_approved_answer and approved_match:
            # Use approved answer from database, enriched with historical data insights
            assistant_text = enrich_answer_with_data_insights(
                approved_match,
                message,
                context=None  # Could pass extracted context here for even richer insights
            )

            # Store conversation in history
            history.append({"role": "user", "content": message})
            history.append({"role": "assistant", "content": assistant_text})

        else:
            # No approved answer - use Claude as fallback
            print(f"ℹ️  No approved answer found, using Claude fallback for: {message[:50]}...")

            api_response = requests.post(
                url="https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                    "Content-Type": "application/json",
                    "HTTP-Referer": "https://louisville-311-dashboard.onrender.com",
                    "X-Title": "Louisville 311 Dashboard"
                },
                json={
                    "model": "anthropic/claude-sonnet-4.5:beta",
                    "messages": messages,
                    "max_tokens": 1024,
                    "temperature": 0.7
                },
                timeout=30
            )

            if api_response.status_code == 200:
                response_data = api_response.json()
                assistant_text = response_data['choices'][0]['message']['content']

                # Store conversation in history
                history.append({"role": "user", "content": message})
                history.append({"role": "assistant", "content": assistant_text})
            else:
                assistant_text = f"I apologize, but I encountered an error (HTTP {api_response.status_code}). Please try again."

    except requests.exceptions.Timeout:
        assistant_text = "I apologize, but the request timed out. Please try again."
    except Exception as e:
        assistant_text = f"I apologize, but I encountered an error processing your question: {str(e)}"

    # Increment rate limit counters (successful question)
    increment_rate_limit(session_id, ip_address)

    # Calculate remaining questions after increment
    _, remaining, _ = check_rate_limit(session_id, ip_address)

    # Generate unique message ID for feedback tracking
    message_id = str(uuid.uuid4())

    # Generate follow-up questions based on user's question
    follow_ups = generate_follow_up_questions(message)

    # Build feedback values with question_id if approved answer was used
    feedback_vals_positive = {
        "message_id": message_id,
        "feedback": "positive"
    }
    feedback_vals_negative = {
        "message_id": message_id,
        "feedback": "negative"
    }

    if matched_question_id:
        feedback_vals_positive["question_id"] = str(matched_question_id)
        feedback_vals_negative["question_id"] = str(matched_question_id)

    # Assistant message bubble with feedback buttons
    assistant_msg = Div(
        Div(assistant_text, cls="message assistant-message"),
        Div(timestamp, cls="timestamp"),
        Div(
            Button(
                "👍",
                cls="feedback-btn",
                hx_post="/chat/feedback",
                hx_vals=json.dumps(feedback_vals_positive),
                hx_target="closest div",
                hx_swap="afterend",
                title="Helpful response"
            ),
            Button(
                "👎",
                cls="feedback-btn",
                hx_post="/chat/feedback",
                hx_vals=json.dumps(feedback_vals_negative),
                hx_target="closest div",
                hx_swap="afterend",
                title="Not helpful"
            ),
            cls="feedback-buttons"
        ),
        Div(
            f"💬 {remaining} questions remaining",
            cls="text-muted",
            style="font-size: 0.75rem; margin-top: 0.25rem;"
        ),
        style="display: flex; flex-direction: column; align-items: flex-start;"
    )

    # Follow-up questions section
    follow_up_section = Div(
        Div("💡 You might also want to ask:", cls="follow-up-label"),
        *[
            Button(
                q,
                cls="follow-up-btn",
                hx_post="/chat/ask",
                hx_vals=f'{{"message": "{q}"}}',
                hx_target="#chat-history",
                hx_swap="beforeend",
                hx_indicator="#typing-indicator",
                onclick="document.querySelector('.chat-container').scrollTop = document.querySelector('.chat-container').scrollHeight;"
            )
            for q in follow_ups
        ],
        cls="follow-up-questions"
    )

    # Return both messages with session cookie
    response = Div(user_msg, assistant_msg, follow_up_section)
    # Note: FastHTML will handle setting cookies if we return a Response object with set_cookie
    # For now, using simple approach - session persists via server-side storage
    return response

# ============================================================================
# RUN APP
# ============================================================================

if __name__ == '__main__':
    import uvicorn
    port = int(os.environ.get('PORT', 5002))
    print(f"\n🚀 Dashboard starting at http://localhost:{port}")
    print(f"📊 Data: {len(df):,} service requests loaded\n")
    uvicorn.run(app, host='0.0.0.0', port=port)
