"""Main scraper module for multi-source product data collection."""
import time
from typing import List, Dict, Any, Optional
from src.parser import ResponseParser
from src.models import Product


class MockResponse:
    """Mock HTTP response object for testing."""
    
    def __init__(self, text: str, status_code: int = 200, content_type: str = 'application/json'):
        self.text = text
        self.status_code = status_code
        self.headers = {'Content-Type': content_type}


class PriceMonitorScraper:
    """Multi-source price monitoring scraper.
    
    Implements a 5-stage data extraction workflow:
    1. Scrape product listing pages → extract product URLs
    2. Visit product detail pages → extract price, stock, specs
    3. Visit review pages → extract ratings
    4. Visit promotion pages → extract discount info
    5. Cross-site matching → identify same products
    """

    def __init__(self):
        self.parser = ResponseParser()
        self.session_active = True

    def scrape_product_listing(self, source: str) -> List[str]:
        """Stage 1: Scrape product listing page.
        
        Args:
            source: E-commerce site identifier
            
        Returns:
            List of product URLs
        """
        # Simulate HTTP request (in real scenario, would use requests.get)
        response = self._mock_api_call(f'{source}/api/products/list')
        
        # Parse response and extract product URLs
        json_data = self.parser.parse_response(response)
        return self.parser.extract_product_listing(json_data)

    def scrape_product_details(self, product_url: str, source: str) -> Product:
        """Stage 2-4: Scrape product details, reviews, and promotions.
        
        Args:
            product_url: URL of the product detail page
            source: E-commerce site identifier
            
        Returns:
            Complete Product object with all extracted data
        """
        # Simulate HTTP request to product detail API
        response = self._mock_api_call(product_url)
        
        # 🐛 BUG: If server returns HTML error page or session expired page,
        # parser.parse_response() will crash with JSONDecodeError
        json_data = self.parser.parse_response(response)
        
        # Extract complete product information
        product = self.parser.extract_product_details(json_data)
        return product

    def match_cross_site_products(self, products: List[Product]) -> Dict[str, List[Product]]:
        """Stage 5: Match same products across different sites.
        
        Args:
            products: List of products from different sources
            
        Returns:
            Dictionary mapping product names to list of matching products
        """
        matched = {}
        for product in products:
            # Simple matching by normalized name
            key = self._normalize_product_name(product.name)
            if key not in matched:
                matched[key] = []
            matched[key].append(product)
        
        return {k: v for k, v in matched.items() if len(v) > 1}

    def _normalize_product_name(self, name: str) -> str:
        """Normalize product name for cross-site matching."""
        return name.lower().strip()

    def _mock_api_call(self, url: str) -> MockResponse:
        """Mock API call for testing.
        
        In production, this would use:
            session = requests.Session()
            session.headers.update({
                'User-Agent': '...',
                'Referer': '...',
                'Cookie': '...'
            })
            response = session.get(url)
        """
        # Simulate network delay
        time.sleep(0.01)
        
        # Return mock successful JSON response
        return MockResponse(
            text='{"products": [], "status": "ok"}',
            status_code=200,
            content_type='application/json'
        )

    def check_session_status(self) -> bool:
        """Check if session/cookies are still valid.
        
        Returns:
            True if session is active, False otherwise
        """
        return self.session_active
