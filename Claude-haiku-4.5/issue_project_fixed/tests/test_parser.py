"""Unit tests for ResponseParser.

These tests expose the JSON parsing bug when responses are not valid JSON.
"""
import pytest
import json
from src.parser import ResponseParser
from src.scraper import MockResponse


class TestResponseParserBug:
    """Test cases that expose the JSON parsing vulnerability."""

    def setup_method(self):
        """Set up test fixtures."""
        self.parser = ResponseParser()

    def test_parse_valid_json_response(self):
        """Baseline test: Parser works correctly with valid JSON."""
        response = MockResponse(
            text='{"status": "ok", "data": {"id": "123"}}',
            content_type='application/json'
        )
        
        result = self.parser.parse_response(response)
        assert result['status'] == 'ok'
        assert result['data']['id'] == '123'

    def test_parse_html_error_page_should_fail(self):
        """🐛 BUG TEST: Parser should handle HTML error pages gracefully.
        
        Scenario: Server returns 200 OK with HTML error page instead of JSON.
        This commonly happens when:
        - Internal server error wrapped in custom error page
        - Maintenance page
        - Rate limiting page
        
        Expected: Should raise ValueError with clear message about content type
        Actual: Currently raises json.JSONDecodeError (crashes ungracefully)
        """
        # Simulate server returning HTML error page with 200 status
        html_error = """
        <!DOCTYPE html>
        <html>
        <head><title>Error</title></head>
        <body>
            <h1>Internal Server Error</h1>
            <p>Sorry, something went wrong.</p>
        </body>
        </html>
        """
        
        response = MockResponse(
            text=html_error,
            status_code=200,
            content_type='text/html'  # Wrong content type!
        )
        
        # Should raise ValueError with helpful message, not JSONDecodeError
        with pytest.raises(ValueError) as exc_info:
            self.parser.parse_response(response)
        
        # Should have clear error message about content type
        assert "json" in str(exc_info.value).lower()
        assert "html" in str(exc_info.value).lower()

    def test_parse_session_expired_redirect_page_should_fail(self):
        """🐛 BUG TEST: Parser should detect session expiration.
        
        Scenario: Cookies/session expired, server returns login page HTML.
        This is the Cookie/Session异常 scenario from requirements.
        
        Expected: Should raise ValueError indicating invalid content type
        Actual: Currently crashes with JSONDecodeError
        """
        # Simulate login redirect page
        login_redirect_html = """
        <!DOCTYPE html>
        <html>
        <head>
            <meta http-equiv="refresh" content="0;url=/login">
            <title>Session Expired</title>
        </head>
        <body>
            <p>Your session has expired. Redirecting to login...</p>
        </body>
        </html>
        """
        
        response = MockResponse(
            text=login_redirect_html,
            status_code=200,
            content_type='text/html'
        )
        
        # Should raise ValueError, not JSONDecodeError
        with pytest.raises(ValueError) as exc_info:
            self.parser.parse_response(response)
        
        assert "json" in str(exc_info.value).lower()

    def test_parse_plain_text_error_should_fail(self):
        """🐛 BUG TEST: Parser should handle plain text responses gracefully.
        
        Scenario: API returns plain text error message.
        
        Expected: Should raise ValueError for non-JSON content
        Actual: Currently raises json.JSONDecodeError
        """
        response = MockResponse(
            text="Service temporarily unavailable. Please try again later.",
            status_code=200,
            content_type='text/plain'
        )
        
        # Should raise ValueError with clear message
        with pytest.raises(ValueError) as exc_info:
            self.parser.parse_response(response)
        
        assert "json" in str(exc_info.value).lower()

    def test_parse_malformed_json_should_fail(self):
        """🐛 BUG TEST: Parser crashes with malformed JSON.
        
        Scenario: Server returns truncated or corrupted JSON.
        """
        response = MockResponse(
            text='{"status": "ok", "data": {incomplete',
            content_type='application/json'
        )
        
        with pytest.raises(json.JSONDecodeError):
            self.parser.parse_response(response)


class TestProductDataExtraction:
    """Tests for product data extraction (these should pass)."""

    def setup_method(self):
        """Set up test fixtures."""
        self.parser = ResponseParser()

    def test_extract_product_listing(self):
        """Test extracting product URLs from listing response."""
        json_data = {
            'products': [
                {'id': '1', 'name': 'Product A', 'url': 'https://site.com/product/1'},
                {'id': '2', 'name': 'Product B', 'url': 'https://site.com/product/2'},
            ]
        }
        
        urls = self.parser.extract_product_listing(json_data)
        assert len(urls) == 2
        assert 'https://site.com/product/1' in urls

    def test_extract_product_details(self):
        """Test extracting complete product information."""
        json_data = {
            'id': 'PROD123',
            'name': 'Smartphone XYZ',
            'url': 'https://site.com/product/123',
            'source': 'site-a',
            'price': {
                'current': '¥1,299.00',
                'original': '¥1,599.00',
                'currency': 'CNY',
                'discount_percent': 18.76
            },
            'in_stock': True,
            'specs': {
                'brand': 'TechCorp',
                'color': 'Black',
                'storage': '128GB'
            },
            'reviews': {
                'average': 4.5,
                'total': 1523,
                '5star': 800,
                '4star': 500,
                '3star': 150,
                '2star': 50,
                '1star': 23
            },
            'promotions': [
                {
                    'title': 'Flash Sale',
                    'description': 'Limited time offer',
                    'discount': 300.0
                }
            ]
        }
        
        product = self.parser.extract_product_details(json_data)
        
        assert product.product_id == 'PROD123'
        assert product.name == 'Smartphone XYZ'
        assert product.price.amount == 1299.00
        assert product.price.original_price == 1599.00
        assert product.price.discount_percentage == 18.76
        assert product.in_stock is True
        assert product.reviews.average_rating == 4.5
        assert product.reviews.total_reviews == 1523
        assert len(product.promotions) == 1
        assert product.promotions[0].title == 'Flash Sale'

    def test_parse_price_various_formats(self):
        """Test price parsing with different formats."""
        parser = ResponseParser()
        
        assert parser._parse_price('¥1,299.00') == 1299.00
        assert parser._parse_price('$199.99') == 199.99
        assert parser._parse_price('1299元') == 1299.00
        assert parser._parse_price('1,999') == 1999.00
        assert parser._parse_price(None) == 0.0
        assert parser._parse_price('') == 0.0
