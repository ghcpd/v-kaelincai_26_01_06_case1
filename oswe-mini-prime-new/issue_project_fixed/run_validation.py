import json
import sys

from src.scraper import PriceMonitorScraper, MockResponse
from src.models import Product


def main():
    print("Runtime validation starting...")

    scraper = PriceMonitorScraper()

    # 1) Test scrape_product_listing with default mock
    try:
        urls = scraper.scrape_product_listing('site-a')
        print(f"scrape_product_listing returned: {urls}")
    except Exception as e:
        print(f"scrape_product_listing failed: {e}")
        raise

    # 2) Test scrape_product_details with a valid product response
    valid_product_json = {
        'id': 'RUN001',
        'name': 'Runtime Test Product',
        'url': 'https://site.com/p/run',
        'source': 'site-a',
        'price': {'current': '199.99', 'currency': 'USD'},
        'in_stock': True,
        'specs': {}
    }

    # Monkeypatch the internal _mock_api_call to return our valid product
    scraper._mock_api_call = lambda url: MockResponse(text=json.dumps(valid_product_json), content_type='application/json')

    try:
        product = scraper.scrape_product_details('https://site.com/p/run', 'site-a')
        print(f"scrape_product_details returned Product: id={product.product_id}, name={product.name}")
    except Exception as e:
        print(f"scrape_product_details failed: {e}")
        raise

    # 3) Test behavior when server returns HTML error
    html_error = """
    <!DOCTYPE html>
    <html><body><h1>500 Internal Server Error</h1></body></html>
    """
    scraper._mock_api_call = lambda url: MockResponse(text=html_error, status_code=200, content_type='text/html')

    try:
        scraper.scrape_product_details('https://site.com/p/run', 'site-a')
        print("ERROR: Expected ValueError when HTML returned, but call succeeded unexpectedly")
        sys.exit(2)
    except ValueError as e:
        print(f"Correctly raised ValueError for HTML response: {e}")
    except Exception as e:
        print(f"Unexpected exception type for HTML response: {e}")
        raise

    # 4) Test behavior when server returns plain text
    scraper._mock_api_call = lambda url: MockResponse(text='Service temporarily unavailable', status_code=200, content_type='text/plain')

    try:
        scraper.scrape_product_details('https://site.com/p/run', 'site-a')
        print("ERROR: Expected ValueError when plain text returned, but call succeeded unexpectedly")
        sys.exit(3)
    except ValueError as e:
        print(f"Correctly raised ValueError for plain text response: {e}")
    except Exception as e:
        print(f"Unexpected exception type for plain text response: {e}")
        raise

    print("Runtime validation completed successfully.")


if __name__ == '__main__':
    main()
