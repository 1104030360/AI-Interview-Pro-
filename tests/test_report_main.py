"""
Test suite for report_main.py Flask application
Tests all routes, API endpoints, and data integrity
"""

import pytest
import json
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from report_main import app, data_store


@pytest.fixture
def client():
    """Create test client for Flask app"""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


@pytest.fixture
def sample_data():
    """Sample data for testing"""
    return {
        "title": "TEST_ADAM",
        "name": "Test_Service_1",
        "time": "From 2025-11-16 19:00 TO 2025-11-16 20:00",
        "person_name": "TestUser",
        "organization": "Test Org",
        "total_score": 85.0,
        "audio_score": 80.0,
        "text_score": 90.0,
        "facial_score": 85.0,
        "ai_text1": "Test analysis 1",
        "ai_text2": "Test analysis 2",
        "ai_text3": "Test analysis 3",
        "charts": ["test_chart1.jpg", "test_chart2.jpg"]
    }


class TestMainRoute:
    """Test main page route"""
    
    def test_index_renders_successfully(self, client):
        """Test that main page renders with 200 status"""
        response = client.get('/')
        assert response.status_code == 200
        assert b'<!DOCTYPE html>' in response.data
    
    def test_index_contains_adam_title(self, client):
        """Test that ADAM title appears in page"""
        response = client.get('/')
        assert b'ADAM' in response.data
    
    def test_index_contains_scores(self, client):
        """Test that score elements are present"""
        response = client.get('/')
        assert b'totalScore' in response.data
        assert b'audioScore' in response.data
        assert b'textScore' in response.data
        assert b'facialScore' in response.data
    
    def test_index_contains_tabs(self, client):
        """Test that tab navigation exists"""
        response = client.get('/')
        assert b'data-tab="overview"' in response.data
        assert b'data-tab="customer"' in response.data
        assert b'data-tab="server"' in response.data


class TestAPIEndpoints:
    """Test API endpoints"""
    
    def test_api_report_returns_json(self, client):
        """Test /api/report returns valid JSON"""
        response = client.get('/api/report')
        assert response.status_code == 200
        assert response.content_type == 'application/json'
    
    def test_api_report_contains_required_fields(self, client):
        """Test API response has all required fields"""
        response = client.get('/api/report')
        data = json.loads(response.data)
        
        required_fields = [
            'title', 'name', 'time', 'person_name', 'organization',
            'total_score', 'audio_score', 'text_score', 'facial_score',
            'ai_text1', 'ai_text2', 'ai_text3', 'charts'
        ]
        
        for field in required_fields:
            assert field in data, f"Missing required field: {field}"
    
    def test_api_report_scores_are_numbers(self, client):
        """Test that scores are numeric types"""
        response = client.get('/api/report')
        data = json.loads(response.data)
        
        assert isinstance(data['total_score'], (int, float))
        assert isinstance(data['audio_score'], (int, float))
        assert isinstance(data['text_score'], (int, float))
        assert isinstance(data['facial_score'], (int, float))
    
    def test_api_charts_returns_json(self, client):
        """Test /api/charts returns valid JSON"""
        response = client.get('/api/charts')
        assert response.status_code == 200
        assert response.content_type == 'application/json'
    
    def test_api_charts_structure(self, client):
        """Test charts API returns correct structure"""
        response = client.get('/api/charts')
        data = json.loads(response.data)
        
        assert 'charts' in data
        assert isinstance(data['charts'], list)
        
        if len(data['charts']) > 0:
            chart = data['charts'][0]
            assert 'filename' in chart
            assert 'url' in chart
            assert 'exists' in chart
            assert 'size' in chart
    
    def test_api_charts_url_format(self, client):
        """Test that chart URLs are properly formatted"""
        response = client.get('/api/charts')
        data = json.loads(response.data)
        
        for chart in data['charts']:
            assert chart['url'].startswith('/static/')
            assert chart['filename'] in chart['url']


class TestUpdateEndpoint:
    """Test data update endpoint"""
    
    def test_update_accepts_post(self, client):
        """Test that /update accepts POST requests"""
        response = client.post('/update', 
            json={'total_score': 90.0},
            content_type='application/json')
        assert response.status_code == 200
    
    def test_update_returns_success_status(self, client):
        """Test update returns success status"""
        response = client.post('/update',
            json={'total_score': 95.0},
            content_type='application/json')
        data = json.loads(response.data)
        assert data['status'] == 'success'
    
    def test_update_modifies_data_store(self, client, sample_data):
        """Test that update actually modifies data"""
        original_score = data_store['total_score']
        new_score = 92.5
        
        client.post('/update',
            json={'total_score': new_score},
            content_type='application/json')
        
        # Verify via API
        response = client.get('/api/report')
        data = json.loads(response.data)
        assert data['total_score'] == new_score
        
        # Restore original
        data_store['total_score'] = original_score


class TestDataValidation:
    """Test data validation and constraints"""
    
    def test_scores_are_in_valid_range(self, client):
        """Test that all scores are between 0 and 100"""
        response = client.get('/api/report')
        data = json.loads(response.data)
        
        scores = [
            data['total_score'],
            data['audio_score'],
            data['text_score'],
            data['facial_score']
        ]
        
        for score in scores:
            assert 0 <= score <= 100, f"Score {score} out of valid range"
    
    def test_charts_list_is_not_empty(self, client):
        """Test that charts list contains items"""
        response = client.get('/api/report')
        data = json.loads(response.data)
        
        assert isinstance(data['charts'], list)
        assert len(data['charts']) > 0, "Charts list should not be empty"
    
    def test_text_fields_are_not_empty(self, client):
        """Test that text fields contain data"""
        response = client.get('/api/report')
        data = json.loads(response.data)
        
        text_fields = ['title', 'name', 'person_name', 'organization']
        for field in text_fields:
            assert len(data[field]) > 0, f"Field {field} should not be empty"


class TestStaticFiles:
    """Test static file serving"""
    
    def test_static_images_accessible(self, client):
        """Test that static images can be accessed"""
        # Test timmy1.jpeg
        response = client.get('/static/timmy1.jpeg')
        assert response.status_code == 200
    
    def test_combined_chart_accessible(self, client):
        """Test combined emotion wave chart"""
        response = client.get('/static/Customer_Emotion_Wave & Server_Emotion_Wave.jpg')
        assert response.status_code == 200


class TestIntegration:
    """Integration tests for full workflow"""
    
    def test_full_update_and_retrieve_workflow(self, client):
        """Test complete workflow: update data → retrieve → verify"""
        # Store original values
        original_data = {
            'total_score': data_store['total_score'],
            'person_name': data_store['person_name']
        }
        
        # Update data
        new_data = {
            'total_score': 88.8,
            'person_name': 'Integration Test User'
        }
        
        response = client.post('/update',
            json=new_data,
            content_type='application/json')
        assert response.status_code == 200
        
        # Retrieve via API
        response = client.get('/api/report')
        data = json.loads(response.data)
        
        # Verify updates
        assert data['total_score'] == new_data['total_score']
        assert data['person_name'] == new_data['person_name']
        
        # Restore original data
        client.post('/update',
            json=original_data,
            content_type='application/json')
    
    def test_page_reflects_data_store(self, client):
        """Test that rendered page contains current data_store values"""
        response = client.get('/')
        html = response.data.decode('utf-8')
        
        # Check that data_store values appear in HTML
        assert data_store['title'] in html
        assert data_store['person_name'] in html
        assert data_store['organization'] in html


class TestErrorHandling:
    """Test error handling"""
    
    def test_invalid_route_returns_404(self, client):
        """Test that invalid routes return 404"""
        response = client.get('/invalid/route')
        assert response.status_code == 404
    
    def test_update_without_json_body(self, client):
        """Test update endpoint without JSON body"""
        response = client.post('/update')
        # Should handle gracefully (might return 400 or 500)
        assert response.status_code in [400, 500]


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
