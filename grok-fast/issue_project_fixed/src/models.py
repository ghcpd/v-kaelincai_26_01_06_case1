"""Data models for product information."""
from dataclasses import dataclass
from typing import Optional, List
from datetime import datetime


@dataclass
class ProductPrice:
    """Product price information."""
    amount: float
    currency: str
    original_price: Optional[float] = None
    discount_percentage: Optional[float] = None


@dataclass
class ProductReview:
    """Product review ratings."""
    average_rating: float
    total_reviews: int
    five_star: int = 0
    four_star: int = 0
    three_star: int = 0
    two_star: int = 0
    one_star: int = 0


@dataclass
class ProductPromotion:
    """Promotion information."""
    title: str
    description: str
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    discount_amount: Optional[float] = None


@dataclass
class Product:
    """Complete product information."""
    product_id: str
    name: str
    url: str
    source: str  # e-commerce site name
    price: ProductPrice
    in_stock: bool
    specifications: dict
    reviews: Optional[ProductReview] = None
    promotions: List[ProductPromotion] = None
    last_updated: datetime = None

    def __post_init__(self):
        if self.last_updated is None:
            self.last_updated = datetime.now()
        if self.promotions is None:
            self.promotions = []