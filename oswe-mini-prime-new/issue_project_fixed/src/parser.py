"""Response parser for extracting product data from API responses.

⚠️ BUG ALERT: This module contains a deliberate JSON parsing bug.
The parse_response() function does not validate response content type
and blindly attempts JSON parsing even when receiving HTML error pages.
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
        
        This function validates the response content before attempting to
        parse JSON. If the response is HTML or plain text it raises
        a ValueError with a clear message. Malformed JSON (when content
        type indicates JSON) will still raise json.JSONDecodeError.
        
        Args:
            response_data: Mock response object with .text attribute or .headers
            
        Returns:
            Parsed JSON data as dictionary
            
        Raises:
            ValueError: When response is not JSON (e.g., HTML or text/plain)
            json.JSONDecodeError: When content-type is JSON but payload is malformed
        """
        # Retrieve Content-Type from common locations
        content_type = ''
        if hasattr(response_data, 'headers') and isinstance(response_data.headers, dict):
            content_type = response_data.headers.get('Content-Type', '')
        elif hasattr(response_data, 'content_type'):
            content_type = getattr(response_data, 'content_type') or ''

        content_type = (content_type or '').lower()
        text = getattr(response_data, 'text', '') or ''

        # Detect obvious HTML payloads regardless of content-type header
        if '<html' in text.lower() or '<!doctype' in text.lower():
            raise ValueError(f"Expected JSON response but got HTML content (content-type={content_type or 'unknown'})")

        # If header explicitly declares JSON, attempt parsing (let JSONDecodeError bubble up)
        if 'application/json' in content_type:
            return json.loads(text)

        # If no content-type header, try a best-effort detection: if it looks like JSON, parse it
        if not content_type:
            stripped = text.strip()
            if stripped.startswith('{') or stripped.startswith('['):
                return json.loads(text)
            raise ValueError("Expected JSON response but got non-JSON content (no content-type header)")

        # For other content types (e.g., text/html, text/plain), raise ValueError
        raise ValueError(f"Expected JSON response (application/json) but got {content_type}")

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
