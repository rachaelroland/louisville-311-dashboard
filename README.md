# Louisville 311 Dashboard

Interactive web dashboard for Louisville Metro 311 service request data.

## Directory Structure

```
dashboard/
├── dashboard_app.py           # Main FastHTML web application
├── sample_311_data.csv        # Sample dataset (9,337 requests)
├── 311_nlp_results.json       # NLP analysis results
├── requirements.txt           # Python dependencies
├── render.yaml                # Render.com deployment config
├── start_dashboard.sh         # Local startup script
├── test_dashboard.py          # Comprehensive test suite
├── test_simple.py             # Simple tests
├── docs/                      # Documentation
│   ├── CHAT_*.md             # Chat feature documentation
│   ├── DEPLOY.md             # Deployment guide
│   ├── TEST_RESULTS.md       # Test results
│   └── *.md                  # Other documentation
└── .git/                      # Git repository

Analysis Scripts:
├── call_center_bottleneck_analysis.py
├── generate_summary_stats.py
├── nsr_deep_dive.py
└── chat_prototype.py
```

## Quick Start

### Local Development

```bash
# From this directory
./start_dashboard.sh

# Or manually:
source .venv/bin/activate
python dashboard_app.py
```

Visit: http://localhost:5002

### Running Tests

```bash
pytest test_dashboard.py -v
```

## Features

- **7 Interactive Tabs:**
  1. Overview - Key metrics and summary
  2. Call Center Analysis - Bottleneck identification
  3. Topics - Service request type breakdown
  4. Sentiment - Sentiment analysis with charts
  5. Urgency - Urgency level distribution
  6. Business Opportunities - Cost savings and improvements
  7. **Ask Questions** - AI-powered chat assistant

- **Chat Assistant Features:**
  - Conversation memory (20 messages)
  - Rate limiting (20 questions/session, 50/hour)
  - Export transcripts
  - Feedback buttons
  - Suggested follow-up questions
  - Safety guardrails

## Deployment

Deployed on Render.com: https://louisville-311-dashboard.onrender.com

See `docs/DEPLOY.md` for deployment instructions.

## Documentation

All documentation is in the `docs/` directory:
- Chat features and enhancements
- Deployment guides
- Test results
- Safety guidelines
- And more

## Git Repository

This directory contains the full git history for the dashboard project.

```bash
# Check status
git status

# View recent commits
git log --oneline -10

# Push changes
git add .
git commit -m "Your message"
git push origin main
```

## Data

- **sample_311_data.csv**: 9,337 service requests from Louisville Metro 311
- **311_nlp_results.json**: Pre-computed NLP analysis results

## Tech Stack

- **Framework**: FastHTML (Python web framework)
- **UI**: Bootstrap 5
- **Charts**: Plotly
- **Data**: Pandas
- **AI**: Claude Sonnet 4.5 via OpenRouter
- **Deployment**: Render.com

## Environment Variables

Required for chat feature:
- `OPENROUTER_API_KEY` - OpenRouter API key for Claude access

See `.env.example` or `docs/DEPLOY.md` for setup instructions.
