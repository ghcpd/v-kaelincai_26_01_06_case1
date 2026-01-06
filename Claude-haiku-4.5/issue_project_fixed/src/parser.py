"""Response parser for extracting product data from API responses.

FIXED VERSION: This module now properly validates response content type
before attempting JSON parsing, preventing crashes on non-JSON responses.
"""
import json
import re
from typing import Dict, Any, Optional
from datetime import datetime
from src.models import Product, ProductPrice, ProductReview, ProductPromotion


class ResponseParser:
    """Parser for e-commerce API responses."""

    def parse_response(self, response_data: Any) -> Dict[str, Any]:
        """Parse HTTP response and extract JSON data.
        
        ✅ FIXED: This function now validates content type before parsing.
        When the server returns HTML error pages or plain text,
        this will raise ValueError with a clear message.
        
        Args:
            response_data: Mock response object with .text attribute and .headers dict
            
        Returns:
            Parsed JSON data as dictionary
            
        Raises:
            ValueError: When response content-type is not JSON
            json.JSONDecodeError: When response is malformed JSON
        """
        # ✅ FIX: Check content type before attempting JSON parsing
        content_type = response_data.headers.get('Content-Type', '').lower()
        
        # Validate that content type is JSON
        if 'application/json' not in content_type:
            raise ValueError(
                f"Expected JSON response (application/json), "
                f"but received {response_data.headers.get('Content-Type', 'unknown')}. "
                f"Response content: {response_data.text[:100]}"
            )
        
        # Now safe to parse JSON
        return json.loads(response_data.text)

    def extract_product_listing(self, json_data: Dict[str, Any]) -> list:
        """Extract product URLs from listing page response.
        
        Args:
            json_data: Parsed JSON response from listing page
            
        Returns:
            List of product URLs
        """
        products = json_data.get('products', [])
        return [p.get('url') for p in products if 'url' in p]

    def extract_product_details(self, json_data: Dict[str, Any]) -> Product:
        """Extract product details from detail page response.
        
        Args:
            json_data: Parsed JSON response from product detail page
            
        Returns:
            Product object with extracted information
        """
        # Extract price information
        price_data = json_data.get('price', {})
        price = ProductPrice(
            amount=self._parse_price(price_data.get('current', '0')),
            currency=price_data.get('currency', 'USD'),
            original_price=self._parse_price(price_data.get('original')) if price_data.get('original') else None,
            discount_percentage=price_data.get('discount_percent')
        )

        # Extract review information
        review_data = json_data.get('reviews', {})
        reviews = None
        if review_data:
            reviews = ProductReview(
                average_rating=review_data.get('average', 0.0),
                total_reviews=review_data.get('total', 0),
                five_star=review_data.get('5star', 0),
                four_star=review_data.get('4star', 0),
                three_star=review_data.get('3star', 0),
                two_star=review_data.get('2star', 0),
                one_star=review_data.get('1star', 0)
            )

        # Extract promotions
        promotions = []
        for promo in json_data.get('promotions', []):
            promotions.append(ProductPromotion(
                title=promo.get('title', ''),
                description=promo.get('description', ''),
                discount_amount=promo.get('discount')
            ))

        # Create product object
        product = Product(
            product_id=json_data.get('id', ''),
            name=json_data.get('name', ''),
            url=json_data.get('url', ''),
            source=json_data.get('source', 'unknown'),
            price=price,
            in_stock=json_data.get('in_stock', False),
            specifications=json_data.get('specs', {}),
            reviews=reviews,
            promotions=promotions
        )

        return product

    def _parse_price(self, price_str: Optional[str]) -> float:
        """Parse price string to float, handling various formats.
        
        Handles formats like: ¥1,299.00, $199.99, 1299元
        
        Args:
            price_str: Price string in various formats
            
        Returns:
            Price as float value
        """
        if not price_str:
            return 0.0
        
        # Remove currency symbols and non-numeric characters except decimal point
        cleaned = re.sub(r'[^\d.]', '', str(price_str))
        
        try:
            return float(cleaned)
        except ValueError:
            return 0.0

    def _parse_date(self, date_str: str) -> Optional[datetime]:
        """Parse date string to datetime, handling multiple formats.
        
        Handles: 2024-01-01, 01/01/2024, relative dates
        
        Args:
            date_str: Date string in various formats
            
        Returns:
            datetime object or None if parsing fails
        """
        if not date_str:
            return None
        
        # Try common formats
        formats = [
            '%Y-%m-%d',
            '%m/%d/%Y',
            '%d/%m/%Y',
            '%Y-%m-%d %H:%M:%S'
        ]
        
        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue
        
        return None
