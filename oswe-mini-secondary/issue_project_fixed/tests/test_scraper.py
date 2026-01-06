"""Integration tests for PriceMonitorScraper.

These tests demonstrate how the parsing bug affects the scraper workflow.
"""
import pytest
import json
from unittest.mock import patch
from src.scraper import PriceMonitorScraper, MockResponse
from src.models import Product


class TestScraperIntegration:
    """Integration tests for the complete scraper workflow."""

    def setup_method(self):
        """Set up test fixtures."""
        self.scraper = PriceMonitorScraper()

    def test_scrape_product_listing_success(self):
        """Test successful product listing scrape."""
        # Mock the API call to return valid product listing
        valid_response = MockResponse(
            text='{"products": [{"id": "1", "url": "https://site.com/p/1"}, {"id": "2", "url": "https://site.com/p/2"}]}',
            content_type='application/json'
        )
        
        with patch.object(self.scraper, '_mock_api_call', return_value=valid_response):
            urls = self.scraper.scrape_product_listing('site-a')
            assert len(urls) == 2
            assert 'https://site.com/p/1' in urls

    def test_scrape_product_details_success(self):
        """Test successful product detail scrape."""
        valid_product_json = {
            'id': 'P001',
            'name': 'Test Product',
            'url': 'https://site.com/p/1',
            'source': 'site-a',
            'price': {'current': '99.99', 'currency': 'USD'},
            'in_stock': True,
            'specs': {}
        }
        
        response = MockResponse(
            text=json.dumps(valid_product_json),
            content_type='application/json'
        )
        
        with patch.object(self.scraper, '_mock_api_call', return_value=response):
            product = self.scraper.scrape_product_details('https://site.com/p/1', 'site-a')
            assert isinstance(product, Product)
            assert product.product_id == 'P001'
            assert product.name == 'Test Product'

    def test_scrape_fails_when_server_returns_html_error(self):
        """🐛 BUG TEST: Scraper should handle HTML error pages gracefully.
        
        Scenario: During scrape_product_details, server returns HTML error
        instead of JSON product data (e.g., due to internal server error).
        
        Expected: Should raise ValueError with clear error message
        Actual: Currently crashes with JSONDecodeError
        
        File: src/parser.py
        Function: parse_response()
        Line: ~28 (json.loads call)
        """
        html_error = """
        <!DOCTYPE html>
        <html><body>
        <h1>500 Internal Server Error</h1>
        </body></html>
        """
        
        error_response = MockResponse(
            text=html_error,
            status_code=200,  # Server still returns 200!
            content_type='text/html'
        )
        
        with patch.object(self.scraper, '_mock_api_call', return_value=error_response):
            # Should raise ValueError, not JSONDecodeError
            with pytest.raises(ValueError) as exc_info:
                self.scraper.scrape_product_details('https://site.com/p/1', 'site-a')
            
            assert "json" in str(exc_info.value).lower()

    def test_scrape_fails_when_session_expired(self):
        """🐛 BUG TEST: Scraper should handle session expiration gracefully.
        
        Scenario: Session expired, server returns login redirect page HTML
        instead of expected JSON data. This is Scenario B from requirements.
        
        Expected: Should raise ValueError indicating wrong content type
        Actual: Currently crashes with JSONDecodeError
        
        File: src/parser.py
        Function: parse_response()
        Line: ~28
        """
        session_expired_html = """
        <html>
        <head><title>Login Required</title></head>
        <body>
        <form action="/login" method="post">
            <input type="text" name="username">
            <input type="password" name="password">
            <button type="submit">Login</button>
        </form>
        </body>
        </html>
        """
        
        login_response = MockResponse(
            text=session_expired_html,
            status_code=200,
            content_type='text/html'
        )
        
        with patch.object(self.scraper, '_mock_api_call', return_value=login_response):
            # Should raise ValueError with helpful message
            with pytest.raises(ValueError) as exc_info:
                self.scraper.scrape_product_details('https://site.com/p/1', 'site-a')
            
            # Error message should mention JSON expectation
            assert "json" in str(exc_info.value).lower()

    def test_match_cross_site_products(self):
        """Test cross-site product matching (should pass)."""
        from src.models import ProductPrice
        
        products = [
            Product(
                product_id='A1',
                name='iPhone 15 Pro',
                url='https://site-a.com/iphone',
                source='site-a',
                price=ProductPrice(amount=999.0, currency='USD'),
                in_stock=True,
                specifications={}
            ),
            Product(
                product_id='B1',
                name='iPhone 15 Pro',
                url='https://site-b.com/iphone',
                source='site-b',
                price=ProductPrice(amount=989.0, currency='USD'),
                in_stock=True,
                specifications={}
            ),
            Product(
                product_id='C1',
                name='Samsung Galaxy S24',
                url='https://site-a.com/galaxy',
                source='site-a',
                price=ProductPrice(amount=899.0, currency='USD'),
                in_stock=True,
                specifications={}
            )
        ]
        
        matched = self.scraper.match_cross_site_products(products)
        
        # Should find iPhone 15 Pro matched across two sites
        assert 'iphone 15 pro' in matched
        assert len(matched['iphone 15 pro']) == 2
        
        # Samsung has no match, should not appear
        assert 'samsung galaxy s24' not in matched


class TestScraperSessionManagement:
    """Tests for session and authentication handling."""

    def test_check_session_status(self):
        """Test session status checking."""
        scraper = PriceMonitorScraper()
        assert scraper.check_session_status() is True
        
        scraper.session_active = False
        assert scraper.check_session_status() is False