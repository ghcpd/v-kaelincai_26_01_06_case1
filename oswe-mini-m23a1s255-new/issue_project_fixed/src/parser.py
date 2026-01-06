"""Response parser for extracting product data from API responses.

This module fixes the previous behaviour that attempted to parse every
response as JSON. The `parse_response` method now validates the
Content-Type header, applies lightweight heuristics when the header is
missing, and raises ValueError for non-JSON responses (with clear
messages). Malformed JSON returned with an explicit JSON content-type
continues to raise json.JSONDecodeError so callers can distinguish the
cases.
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

        Robust behavior:
        - If Content-Type explicitly indicates JSON -> attempt json.loads() and
          allow json.JSONDecodeError to propagate for malformed payloads.
        - If Content-Type explicitly indicates non-JSON (text/html, text/plain,
          etc.) -> raise ValueError with a clear message (do NOT attempt to
          parse).
        - If Content-Type is missing/ambiguous, perform a small heuristic:
          try to detect HTML (look for '<html' / '<!doctype') or a JSON-like
          body (starts with '{' or '['). If body looks like JSON, attempt to
          parse; otherwise raise ValueError.

        Raises:
            ValueError: when response is not JSON (or header/body indicate HTML)
            json.JSONDecodeError: when Content-Type is JSON but body is malformed
        """
        # Read headers/content safely
        headers = getattr(response_data, "headers", {}) or {}
        content_type = str(headers.get("Content-Type", "")).lower()
        text = getattr(response_data, "text", "") or ""
        status = getattr(response_data, "status_code", "unknown")

        # If server explicitly declares JSON, parse and let JSON errors bubble up
        if "application/json" in content_type:
            return json.loads(text)

        # If server explicitly declares a non-JSON type, fail fast with useful error
        if content_type and "application/json" not in content_type:
            raise ValueError(
                f"Expected JSON response, got {content_type} (status {status})"
            )

        # No or ambiguous content-type: use heuristics on the body
        body = text.strip()

        # Detect obvious HTML pages (error pages, login redirects, maintenance)
        lowered = body.lower()
        if lowered.startswith("<!doctype") or lowered.startswith("<html") or "<html" in lowered:
            raise ValueError(f"Expected JSON response, got text/html (status {status})")

        # If body *looks like* JSON, try to parse it. If parsing fails, treat as malformed JSON
        if body.startswith("{") or body.startswith("["):
            try:
                return json.loads(body)
            except json.JSONDecodeError:
                # Header absent but body looks like JSON and is malformed — surface as ValueError
                # (caller cannot rely on Content-Type in this case)
                raise ValueError(
                    f"Expected JSON response but body is malformed JSON (status {status})"
                )

        # Fallback: not JSON
        raise ValueError(f"Expected JSON response, got {content_type or 'text/plain'} (status {status})")

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
