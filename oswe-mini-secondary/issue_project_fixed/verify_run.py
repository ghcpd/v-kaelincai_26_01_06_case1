"""Runtime verification script for manual checks.

This runs a few sample flows to ensure the scraper and parser behave as expected
outside of pytest, printing outputs and any error traces encountered.
"""
import json
import traceback
from unittest.mock import patch
from src.scraper import PriceMonitorScraper, MockResponse
from src.parser import ResponseParser


def run_checks():
    print('== Runtime verification started ==')
    parser = ResponseParser()

    # 1) Valid JSON parsing
    valid = MockResponse(text='{"status": "ok", "data": {"id": "123"}}', content_type='application/json')
    try:
        parsed = parser.parse_response(valid)
        print('Valid JSON parsed:', parsed)
    except Exception:
        print('ERROR parsing valid JSON:')
        traceback.print_exc()

    # 2) Scraper listing flow
    scraper = PriceMonitorScraper()
    valid_listing = MockResponse(text='{"products": [{"id": "1", "url": "https://site.com/p/1"}]}', content_type='application/json')
    with patch.object(scraper, '_mock_api_call', return_value=valid_listing):
        try:
            urls = scraper.scrape_product_listing('site-a')
            print('Listing URLs:', urls)
        except Exception:
            print('ERROR during scrape_product_listing:')
            traceback.print_exc()

    # 3) Scraper detail flow (success)
    valid_product_json = {
        'id': 'P001', 'name': 'Test Product', 'url': 'https://site.com/p/1', 'source': 'site-a', 'price': {'current': '99.99', 'currency': 'USD'}, 'in_stock': True, 'specs': {}
    }
    success_response = MockResponse(text=json.dumps(valid_product_json), content_type='application/json')
    with patch.object(scraper, '_mock_api_call', return_value=success_response):
        try:
            product = scraper.scrape_product_details('https://site.com/p/1', 'site-a')
            print('Scraped product:', product)
        except Exception:
            print('ERROR during scrape_product_details (success case):')
            traceback.print_exc()

    # 4) HTML error handling
    html_error = """
    <!DOCTYPE html>
    <html><body>
    <h1>500 Internal Server Error</h1>
    </body></html>
    """
    error_response = MockResponse(text=html_error, status_code=200, content_type='text/html')
    with patch.object(scraper, '_mock_api_call', return_value=error_response):
        try:
            scraper.scrape_product_details('https://site.com/p/1', 'site-a')
            print('ERROR: expected ValueError for HTML error but call succeeded')
        except ValueError as ve:
            print('Caught expected ValueError for HTML content:', ve)
        except Exception:
            print('Unexpected exception type for HTML error:')
            traceback.print_exc()

    # 5) Plain text error handling
    text_error_response = MockResponse(text='Service temporarily unavailable.', status_code=200, content_type='text/plain')
    with patch.object(scraper, '_mock_api_call', return_value=text_error_response):
        try:
            scraper.scrape_product_details('https://site.com/p/1', 'site-a')
            print('ERROR: expected ValueError for text error but call succeeded')
        except ValueError as ve:
            print('Caught expected ValueError for text content:', ve)
        except Exception:
            print('Unexpected exception type for text error:')
            traceback.print_exc()

    print('== Runtime verification finished ==')


if __name__ == '__main__':
    run_checks()
