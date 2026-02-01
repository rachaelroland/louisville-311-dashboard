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

# ============================================================================
# FASTHTML APP SETUP
# ============================================================================

app, rt = fast_app(
    hdrs=(
        Link(rel='stylesheet', href='https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css'),
        Script(src='https://cdn.plot.ly/plotly-2.27.0.min.js'),
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
    lda_topics = topic_data.get('topic_modeling', {}).get('lda', {}).get('topics', [])

    if not lda_topics:
        return "<p>No topic modeling data available</p>"

    # Create simple bar chart of top keywords from top 5 topics
    topic_labels = []
    topic_weights = []

    for i, topic in enumerate(lda_topics[:5]):
        keywords = topic.get('top_keywords', [])[:5]
        weight = topic.get('weight', 0)
        label = f"Topic {i+1}: {', '.join(keywords)}"
        topic_labels.append(label)
        topic_weights.append(weight * 100)

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
    """Homepage with overview - simplified for testing"""
    return Title('311 NLP Analysis Dashboard'), Main(
        create_nav('home'),
        Div(
            H1('Louisville Metro 311 Dashboard'),
            P(f'Loaded {len(df):,} service requests'),
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
                        Div(
                            style='font-size: 4rem; color: #2193b0;',
                        ).children('→'),
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
# RUN APP
# ============================================================================

if __name__ == '__main__':
    import uvicorn
    port = int(os.environ.get('PORT', 5002))
    print(f"\n🚀 Dashboard starting at http://localhost:{port}")
    print(f"📊 Data: {len(df):,} service requests loaded\n")
    uvicorn.run(app, host='0.0.0.0', port=port)
