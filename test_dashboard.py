"""
Test suite for Louisville 311 NLP Dashboard
Uses pytest to verify all endpoints, data loading, and functionality
"""
import pytest
from pathlib import Path
import json
import pandas as pd
from starlette.testclient import TestClient


@pytest.fixture(scope="module")
def test_client():
    """Create test client for the FastHTML app"""
    # Import the app after setting up the fixture
    import dashboard_app
    return TestClient(dashboard_app.app)


@pytest.fixture(scope="module")
def sample_data():
    """Load sample data for testing"""
    csv_path = Path(__file__).parent / "sample_311_data.csv"
    return pd.read_csv(csv_path)


@pytest.fixture(scope="module")
def topic_data():
    """Load topic modeling data for testing"""
    json_path = Path(__file__).parent / "311_nlp_results.json"
    with open(json_path, 'r') as f:
        return json.load(f)


class TestDataLoading:
    """Test that data files exist and load correctly"""

    def test_csv_file_exists(self):
        """Verify sample_311_data.csv exists"""
        csv_path = Path(__file__).parent / "sample_311_data.csv"
        assert csv_path.exists(), "sample_311_data.csv not found"

    def test_json_file_exists(self):
        """Verify 311_nlp_results.json exists"""
        json_path = Path(__file__).parent / "311_nlp_results.json"
        assert json_path.exists(), "311_nlp_results.json not found"

    def test_csv_loads_successfully(self, sample_data):
        """Verify CSV loads into pandas DataFrame"""
        assert isinstance(sample_data, pd.DataFrame)
        assert len(sample_data) > 0, "CSV has no records"

    def test_csv_has_required_columns(self, sample_data):
        """Verify CSV has all required columns"""
        required_cols = [
            'service_request_id',
            'service_name',
            'description',
            'sentiment',
            'urgency_level',
            'urgency_score'
        ]
        for col in required_cols:
            assert col in sample_data.columns, f"Missing column: {col}"

    def test_json_has_topic_modeling(self, topic_data):
        """Verify JSON has topic modeling structure"""
        assert 'topic_modeling' in topic_data
        assert 'lda' in topic_data['topic_modeling']
        assert 'topics' in topic_data['topic_modeling']['lda']

    def test_data_quality(self, sample_data):
        """Verify data quality checks"""
        # Check for sentiment values
        sentiment_counts = sample_data['sentiment'].value_counts()
        assert 'positive' in sentiment_counts or 'negative' in sentiment_counts or 'neutral' in sentiment_counts

        # Check for urgency levels
        urgency_counts = sample_data['urgency_level'].value_counts()
        assert 'high' in urgency_counts or 'medium' in urgency_counts or 'low' in urgency_counts


class TestEndpoints:
    """Test all dashboard endpoints return 200 OK"""

    def test_home_endpoint(self, test_client):
        """Test homepage (/) returns 200"""
        response = test_client.get("/")
        assert response.status_code == 200, f"Home page failed with {response.status_code}"

    def test_call_center_endpoint(self, test_client):
        """Test call-center page returns 200"""
        response = test_client.get("/call-center")
        assert response.status_code == 200, f"Call center page failed with {response.status_code}"

    def test_topics_endpoint(self, test_client):
        """Test topics page returns 200"""
        response = test_client.get("/topics")
        assert response.status_code == 200, f"Topics page failed with {response.status_code}"

    def test_sentiment_endpoint(self, test_client):
        """Test sentiment page returns 200"""
        response = test_client.get("/sentiment")
        assert response.status_code == 200, f"Sentiment page failed with {response.status_code}"

    def test_urgency_endpoint(self, test_client):
        """Test urgency page returns 200"""
        response = test_client.get("/urgency")
        assert response.status_code == 200, f"Urgency page failed with {response.status_code}"

    def test_business_endpoint(self, test_client):
        """Test business page returns 200"""
        response = test_client.get("/business")
        assert response.status_code == 200, f"Business page failed with {response.status_code}"

    def test_invalid_endpoint_404(self, test_client):
        """Test invalid endpoint returns 404"""
        response = test_client.get("/nonexistent")
        assert response.status_code == 404, "Invalid endpoint should return 404"


class TestHomePageContent:
    """Test homepage contains expected content"""

    def test_page_title(self, test_client):
        """Test homepage has correct title"""
        response = test_client.get("/")
        assert "Louisville Metro 311 NLP Analysis Dashboard" in response.text

    def test_metric_cards_present(self, test_client):
        """Test homepage has metric cards"""
        response = test_client.get("/")
        assert "Total Requests" in response.text
        assert "Negative Sentiment" in response.text
        assert "High Urgency" in response.text
        assert "Top Issue" in response.text

    def test_key_insights_section(self, test_client):
        """Test homepage has Key Insights section"""
        response = test_client.get("/")
        assert "Key Insights" in response.text
        assert "High Negative Sentiment" in response.text

    def test_navigation_links(self, test_client):
        """Test homepage has all navigation links"""
        response = test_client.get("/")
        assert 'href="/"' in response.text
        assert 'href="/call-center"' in response.text
        assert 'href="/topics"' in response.text
        assert 'href="/sentiment"' in response.text
        assert 'href="/urgency"' in response.text
        assert 'href="/business"' in response.text


class TestTopicsPageContent:
    """Test topics page contains expected content"""

    def test_page_title(self, test_client):
        """Test topics page has correct title"""
        response = test_client.get("/topics")
        assert "Topics Analysis" in response.text or "Service Request Topics" in response.text

    def test_top_10_section(self, test_client):
        """Test topics page shows Top 10 service types"""
        response = test_client.get("/topics")
        assert "Top 10 Service Types" in response.text

    def test_deep_dive_section(self, test_client):
        """Test topics page has deep dive section"""
        response = test_client.get("/topics")
        assert "Deep Dive" in response.text


class TestSentimentPageContent:
    """Test sentiment page contains expected content"""

    def test_page_title(self, test_client):
        """Test sentiment page has correct title"""
        response = test_client.get("/sentiment")
        assert "Sentiment Analysis" in response.text

    def test_sentiment_counts(self, test_client):
        """Test sentiment page shows counts"""
        response = test_client.get("/sentiment")
        assert "Positive" in response.text
        assert "Negative" in response.text
        assert "Neutral" in response.text

    def test_sample_requests(self, test_client):
        """Test sentiment page shows sample requests"""
        response = test_client.get("/sentiment")
        assert "Sample Negative Requests" in response.text or "Sample Positive Requests" in response.text


class TestUrgencyPageContent:
    """Test urgency page contains expected content"""

    def test_page_title(self, test_client):
        """Test urgency page has correct title"""
        response = test_client.get("/urgency")
        assert "Urgency Distribution" in response.text

    def test_urgency_levels(self, test_client):
        """Test urgency page shows urgency levels"""
        response = test_client.get("/urgency")
        assert "High" in response.text
        assert "Medium" in response.text
        assert "Low" in response.text

    def test_critical_section(self, test_client):
        """Test urgency page has CRITICAL section"""
        response = test_client.get("/urgency")
        assert "CRITICAL" in response.text


class TestCallCenterPageContent:
    """Test call center page contains expected content"""

    def test_page_title(self, test_client):
        """Test call center page has correct title"""
        response = test_client.get("/call-center")
        assert "Call Center Bottleneck Analysis" in response.text

    def test_business_opportunity(self, test_client):
        """Test call center page shows business opportunity"""
        response = test_client.get("/call-center")
        assert "Business Opportunity" in response.text


class TestBusinessPageContent:
    """Test business page contains expected content"""

    def test_page_title(self, test_client):
        """Test business page has correct title"""
        response = test_client.get("/business")
        assert "Business Opportunities" in response.text

    def test_roi_projection(self, test_client):
        """Test business page shows ROI projection"""
        response = test_client.get("/business")
        assert "ROI Projection" in response.text or "$125,075" in response.text

    def test_strategic_recommendations(self, test_client):
        """Test business page has recommendations"""
        response = test_client.get("/business")
        assert "Strategic Recommendations" in response.text or "Recommendation" in response.text


class TestDataAnalytics:
    """Test data analytics and calculations"""

    def test_sentiment_distribution(self, sample_data):
        """Test sentiment distribution calculations"""
        sentiment_counts = sample_data['sentiment'].value_counts()
        total = len(sample_data)

        # Calculate percentages
        for sentiment in sentiment_counts.index:
            percentage = (sentiment_counts[sentiment] / total) * 100
            assert 0 <= percentage <= 100, f"Invalid percentage for {sentiment}"

    def test_urgency_distribution(self, sample_data):
        """Test urgency distribution calculations"""
        urgency_counts = sample_data['urgency_level'].value_counts()
        total = len(sample_data)

        # Calculate percentages
        for urgency in urgency_counts.index:
            percentage = (urgency_counts[urgency] / total) * 100
            assert 0 <= percentage <= 100, f"Invalid percentage for {urgency}"

    def test_top_services_calculation(self, sample_data):
        """Test top services by volume"""
        top_services = sample_data['service_name'].value_counts().head(10)
        assert len(top_services) > 0, "No top services found"
        assert len(top_services) <= 10, "Should return at most 10 services"

    def test_critical_requests_filter(self, sample_data):
        """Test filtering for critical requests (high urgency + negative sentiment)"""
        critical = sample_data[
            (sample_data['urgency_level'] == 'high') &
            (sample_data['sentiment'] == 'negative')
        ]
        # Critical requests may or may not exist, just verify filter works
        assert isinstance(critical, pd.DataFrame)


class TestRequirements:
    """Test that requirements.txt has all dependencies"""

    def test_requirements_file_exists(self):
        """Verify requirements.txt exists"""
        req_path = Path(__file__).parent / "requirements.txt"
        assert req_path.exists(), "requirements.txt not found"

    def test_requirements_has_fasthtml(self):
        """Verify requirements.txt has python-fasthtml"""
        req_path = Path(__file__).parent / "requirements.txt"
        with open(req_path, 'r') as f:
            content = f.read()
        assert "python-fasthtml" in content, "Missing python-fasthtml in requirements.txt"

    def test_requirements_has_pandas(self):
        """Verify requirements.txt has pandas"""
        req_path = Path(__file__).parent / "requirements.txt"
        with open(req_path, 'r') as f:
            content = f.read()
        assert "pandas" in content, "Missing pandas in requirements.txt"

    def test_requirements_has_plotly(self):
        """Verify requirements.txt has plotly"""
        req_path = Path(__file__).parent / "requirements.txt"
        with open(req_path, 'r') as f:
            content = f.read()
        assert "plotly" in content, "Missing plotly in requirements.txt"


class TestDeploymentConfig:
    """Test deployment configuration files"""

    def test_render_yaml_exists(self):
        """Verify render.yaml exists"""
        yaml_path = Path(__file__).parent / "render.yaml"
        assert yaml_path.exists(), "render.yaml not found"

    def test_render_yaml_has_starter_plan(self):
        """Verify render.yaml has starter plan configured"""
        yaml_path = Path(__file__).parent / "render.yaml"
        with open(yaml_path, 'r') as f:
            content = f.read()
        assert "starter" in content, "render.yaml should specify starter plan"

    def test_render_yaml_has_build_command(self):
        """Verify render.yaml has build command"""
        yaml_path = Path(__file__).parent / "render.yaml"
        with open(yaml_path, 'r') as f:
            content = f.read()
        assert "pip install -r requirements.txt" in content, "Missing build command"

    def test_render_yaml_has_start_command(self):
        """Verify render.yaml has start command"""
        yaml_path = Path(__file__).parent / "render.yaml"
        with open(yaml_path, 'r') as f:
            content = f.read()
        assert "python dashboard_app.py" in content, "Missing start command"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
