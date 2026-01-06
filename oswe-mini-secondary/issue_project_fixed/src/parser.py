"""Response parser for extracting product data from API responses.

This module fixes the JSON parsing bug by validating response content type
and handling non-JSON responses (HTML / plain text) gracefully.
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

        This implementation validates the response content type before
        attempting to parse JSON. For non-JSON content (e.g., HTML error
        pages or plain text error messages) it raises ValueError with a
        helpful message. Malformed JSON with an appropriate JSON content
        type will still raise json.JSONDecodeError.
        """
        # Determine content type from common response attributes
        content_type = ''
        if hasattr(response_data, 'headers') and isinstance(response_data.headers, dict):
            content_type = response_data.headers.get('Content-Type', '')
        if not content_type and hasattr(response_data, 'content_type'):
            content_type = getattr(response_data, 'content_type', '')

        ct = content_type.lower() if content_type else ''
        text = response_data.text if hasattr(response_data, 'text') else str(response_data)

        # If content type is present but not JSON -> fail fast with helpful message
        if ct and 'json' not in ct:
            raise ValueError(f"Expected JSON response, got {content_type} (status={getattr(response_data, 'status_code', 'unknown')})")

        # If content type missing, do simple heuristics to detect HTML or plain text
        if not ct:
            # Detect HTML content by presence of tags or doctype
            if re.search(r'<\/?\w+[^>]*>', text) or text.strip().lower().startswith('<!doctype') or text.strip().lower().startswith('<html'):
                raise ValueError("Expected JSON response, got HTML content")

            # If it doesn't look like JSON (doesn't start with { or [), treat as non-JSON text
            if not text.strip().startswith('{') and not text.strip().startswith('['):
                raise ValueError("Expected JSON response, got non-JSON text content")

        # At this point we expect JSON content; attempt to parse and let JSONDecodeError bubble up for malformed JSON
        return json.loads(text)

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
