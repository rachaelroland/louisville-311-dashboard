# Louisville Metro 311 NLP Analysis Dashboard

Interactive web dashboard built with FastHTML to explore the 311 NLP analysis findings.

## Features

### 📊 Interactive Visualizations
- **Sentiment Distribution** - Pie chart showing neutral (55%), negative (45%), positive (<1%)
- **Urgency Levels** - Bar chart of low/medium/high urgency requests
- **Top Service Types** - Top 10 most requested services
- **Topic Analysis** - LDA topic modeling results with keywords

### 💼 Business Intelligence
- **Call Center Bottleneck Analysis** - Identify automation opportunities
- **ROI Projections** - $125K annual savings potential
- **Implementation Roadmap** - 3-phase plan with concrete deliverables
- **Strategic Recommendations** - Data-driven action items

### 🎯 Key Pages
1. **Overview** - High-level metrics and charts
2. **Call Center Analysis** - Detailed bottleneck breakdown
3. **Topics** - Topic modeling insights
4. **Sentiment** - Sentiment analysis deep dive
5. **Urgency** - Urgency distribution patterns
6. **Business Opportunities** - ROI analysis and recommendations

## Installation

### Prerequisites
```bash
# Install uv (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Or using pip
pip install uv
```

### Setup
```bash
cd /Users/rachael/Downloads/311_nlp_analysis_report

# Install dependencies
uv pip install fasthtml pandas plotly
```

## Running the Dashboard

### Local Development
```bash
# Start the dashboard
uv run python dashboard_app.py

# Or specify a custom port
PORT=5002 uv run python dashboard_app.py
```

The dashboard will be available at **http://localhost:5002**

### Production Deployment

The app is ready for deployment to:
- **Render.com** (recommended - same as Zendesk annotation app)
- **Heroku**
- **Railway**
- **Fly.io**

#### Deploy to Render
1. Create `requirements.txt`:
```bash
fasthtml
pandas
plotly
```

2. Create `render.yaml`:
```yaml
services:
  - type: web
    name: louisville-311-dashboard
    env: python
    buildCommand: "pip install -r requirements.txt"
    startCommand: "python dashboard_app.py"
    envVars:
      - key: PORT
        value: 10000
```

3. Push to GitHub and connect to Render

## Data Sources

The dashboard loads data from:
- **CSV**: `/Users/rachael/Documents/projects/rachaelroland/pipelines/pipelines/311/data/processed/311_processed_with_nlp.csv` (168MB, 169,598 records)
- **JSON**: `311_nlp_results.json` (19KB topic modeling results)

### Data Fields Used
- `sentiment` - positive/negative/neutral classification
- `urgency_level` - low/medium/high urgency
- `urgency_score` - 0-10 urgency score
- `service_name` - type of service requested
- `agency_responsible` - metro agency handling request
- `description` - request text
- `ner_json` - named entities (locations, dates, etc.)
- `topics_json` - extracted topics
- `absa_json` - aspect-based sentiment

## Architecture

### FastHTML Framework
Built using FastHTML - a modern Python web framework for rapid dashboard development:
- **Server-side rendering** - Fast page loads
- **Component-based** - Reusable UI elements
- **Plotly integration** - Interactive charts
- **Bootstrap 5** - Professional styling

### Key Components

#### Navigation
```python
create_nav(current_page)  # Top nav bar with page links
```

#### Data Loading
```python
df = pd.read_csv(CSV_PATH)  # Load full dataset on startup
topic_data = json.load(JSON_PATH)  # Load topic modeling results
```

#### Chart Generation
```python
create_sentiment_pie()  # Sentiment distribution pie chart
create_urgency_bar()    # Urgency bar chart
create_top_services_bar()  # Service types horizontal bar
create_topic_wordcloud()  # Topic keywords visualization
```

## Customization

### Adding New Pages
```python
@rt('/my-page')
def get():
    return Title('My Page'), Main(
        create_nav('my-page'),
        Div(
            H1('My Custom Analysis'),
            # Your content here
            cls='container-fluid px-4'
        )
    )
```

### Adding New Charts
```python
def create_my_chart():
    fig = go.Figure(...)
    fig.update_layout(title='My Chart', height=400)
    return fig.to_html(include_plotlyjs=False, div_id='my-chart')
```

### Styling
The dashboard uses Bootstrap 5 with custom gradient styles:
- Primary color: `#2193b0` (blue)
- Secondary color: `#6dd5ed` (light blue)
- Success: `#10b981` (green)
- Danger: `#ef4444` (red)
- Warning: `#f59e0b` (orange)

## Performance

- **Data loading**: ~2 seconds on startup (168MB CSV)
- **Page rendering**: <100ms after data loaded
- **Charts**: Client-side Plotly rendering
- **Memory**: ~500MB with full dataset loaded

### Optimization Tips
1. **Sample data for development**: Use `df = pd.read_csv(CSV_PATH, nrows=10000)` for faster testing
2. **Cache charts**: Use `@lru_cache` for expensive chart generation
3. **Lazy loading**: Load data on-demand instead of at startup
4. **Pagination**: For large tables, paginate results

## Troubleshooting

### Common Issues

**"No module named 'fasthtml'"**
```bash
uv pip install fasthtml
```

**"File not found" error**
```bash
# Update CSV_PATH in dashboard_app.py to point to your data location
CSV_PATH = Path("/path/to/your/311_processed_with_nlp.csv")
```

**Port already in use**
```bash
# Use a different port
PORT=5003 uv run python dashboard_app.py
```

**Charts not rendering**
```bash
# Check browser console for Plotly errors
# Ensure internet connection (Plotly CDN required)
```

## Next Steps

### Enhancements
1. **User authentication** - Add login/logout (like Zendesk annotation app)
2. **Data filters** - Filter by date range, agency, service type
3. **Export functionality** - Download charts as PNG/PDF
4. **Real-time updates** - WebSocket connection for live data
5. **Geographic maps** - Leaflet/Mapbox integration for heat maps
6. **Drill-down views** - Click charts to see detailed records
7. **Comparison views** - Year-over-year, agency-to-agency comparisons

### Advanced Features
- **API endpoints** - REST API for programmatic access
- **Database integration** - PostgreSQL instead of CSV files
- **Search functionality** - Full-text search across descriptions
- **Alerts/notifications** - Email alerts for critical issues
- **Mobile optimization** - Responsive design for phones/tablets

## Credits

**Data Analysis**: Louisville Metro 311 NLP Analysis (2024)
**Framework**: FastHTML (https://fastht.ml)
**Visualizations**: Plotly (https://plotly.com)
**Styling**: Bootstrap 5 (https://getbootstrap.com)

## License

Data and analysis for Louisville Metro internal use.

## Support

For questions or issues:
- Check this README
- Review dashboard_app.py code comments
- See FastHTML docs: https://docs.fastht.ml
- Contact the data analysis team
