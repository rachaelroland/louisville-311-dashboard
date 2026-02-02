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
- Use bullet points for lists when appropriate"""

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
        "What are the top 5 service request types?",
        "How many requests are high urgency?",
        "What is the sentiment breakdown?",
        "Tell me about the call center bottlenecks",
        "How much money can we save?",
        "What are the critical issues right now?",
    ]

    return Title("311 Chat Assistant"), Main(
        create_nav('chat'),

        # Welcome section
        Div(
            H2("💬 Ask Me Anything About 311 Data", cls="mb-3", style="color: #2193b0;"),
            P(
                f"I have information about {len(df):,} service requests from 2024. "
                "Ask questions in plain English and I'll provide insights based on the data.",
                cls="mb-3"
            ),
            P(
                "💡 Tip: Try asking about sentiment, urgency levels, top issues, or business opportunities.",
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
                    onclick="document.querySelector('.chat-container').scrollTop = document.querySelector('.chat-container').scrollHeight;"
                )
                for q in quick_questions
            ],
            cls="quick-questions"
        ),

        # Chat history container
        Div(
            Div(
                "👋 Hello! I'm your 311 data assistant. Ask me anything about the service requests!",
                cls="message assistant-message",
                style="display: inline-block;"
            ),
            id="chat-history",
            cls="chat-container"
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
            hx_on_htmx_after_request="this.reset(); document.querySelector('.chat-container').scrollTop = document.querySelector('.chat-container').scrollHeight;",
            cls="chat-input-form"
        ),

        cls='container-fluid px-4'
    )

@rt('/chat/ask')
def post(message: str):
    """Handle chat message and return response"""

    if not CHAT_ENABLED or not message or message.strip() == "":
        return Div("Please enter a question.", cls="alert alert-warning")

    timestamp = datetime.now().strftime("%I:%M %p")

    # User message bubble
    user_msg = Div(
        Div(message, cls="message user-message"),
        Div(timestamp, cls="timestamp text-end"),
        style="display: flex; flex-direction: column; align-items: flex-end;"
    )

    # Call OpenRouter API (Claude Sonnet 4.5 via OpenRouter)
    try:
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://louisville-311-dashboard.onrender.com",
                "X-Title": "Louisville 311 Dashboard"
            },
            json={
                "model": "anthropic/claude-sonnet-4.5:beta",
                "messages": [
                    {"role": "system", "content": CHAT_CONTEXT},
                    {"role": "user", "content": message}
                ],
                "max_tokens": 1024,
                "temperature": 0.7
            },
            timeout=30
        )

        if response.status_code == 200:
            response_data = response.json()
            assistant_text = response_data['choices'][0]['message']['content']
        else:
            assistant_text = f"I apologize, but I encountered an error (HTTP {response.status_code}). Please try again."

    except requests.exceptions.Timeout:
        assistant_text = "I apologize, but the request timed out. Please try again."
    except Exception as e:
        assistant_text = f"I apologize, but I encountered an error processing your question: {str(e)}"

    # Assistant message bubble
    assistant_msg = Div(
        Div(assistant_text, cls="message assistant-message"),
        Div(timestamp, cls="timestamp"),
        style="display: flex; flex-direction: column; align-items: flex-start;"
    )

    # Return both messages
    return Div(user_msg, assistant_msg)

# ============================================================================
# RUN APP
# ============================================================================

if __name__ == '__main__':
    import uvicorn
    port = int(os.environ.get('PORT', 5002))
    print(f"\n🚀 Dashboard starting at http://localhost:{port}")
    print(f"📊 Data: {len(df):,} service requests loaded\n")
    uvicorn.run(app, host='0.0.0.0', port=port)
