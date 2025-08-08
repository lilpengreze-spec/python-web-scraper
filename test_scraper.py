"""
Test Script for Review Scraper

This script demonstrates how to use the web scraper API and provides
examples of how to interact with the endpoints.
"""

import requests
import json
import time
from typing import Dict, Any


def test_health_endpoint(base_url: str = "http://localhost:5000") -> Dict[str, Any]:
    """Test the health check endpoint."""
    try:
        response = requests.get(f"{base_url}/health", timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return {"error": str(e)}


def test_scrape_endpoint(base_url: str = "http://localhost:5000") -> Dict[str, Any]:
    """Test the scrape endpoint with example data."""
    
    # Example data - replace with real Yelp business ID and Amazon ASIN
    test_data = {
        "yelp_business_id": "garaje-san-francisco",  # Example Yelp business ID
        "amazon_asin": "B08N5WRWNW",  # Example Amazon ASIN (Echo Dot)
        "refresh_interval": 300  # Optional: refresh every 5 minutes
    }
    
    try:
        response = requests.post(
            f"{base_url}/scrape",
            json=test_data,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return {"error": str(e)}


def test_latest_endpoint(base_url: str = "http://localhost:5000") -> Dict[str, Any]:
    """Test the latest data endpoint."""
    try:
        response = requests.get(f"{base_url}/latest", timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return {"error": str(e)}


def run_basic_tests():
    """Run basic tests of the scraper API."""
    base_url = "http://localhost:5000"
    
    print("🧪 Testing Review Scraper API")
    print("=" * 50)
    
    # Test 1: Health Check
    print("\n1. Testing Health Check...")
    health_result = test_health_endpoint(base_url)
    if "error" in health_result:
        print(f"❌ Health check failed: {health_result['error']}")
        print("Make sure the server is running with: python app.py")
        return
    else:
        print(f"✅ Health check passed: {health_result.get('status', 'unknown')}")
    
    # Test 2: Scrape Reviews
    print("\n2. Testing Review Scraping...")
    scrape_result = test_scrape_endpoint(base_url)
    if "error" in scrape_result:
        print(f"❌ Scraping failed: {scrape_result['error']}")
    else:
        print(f"✅ Scraping completed: {scrape_result.get('status', 'unknown')}")
        stats = scrape_result.get('statistics', {})
        print(f"   📊 Total reviews: {stats.get('total_reviews', 0)}")
        print(f"   🔄 Yelp reviews: {stats.get('yelp_review_count', 0)}")
        print(f"   🛍️  Amazon reviews: {stats.get('amazon_review_count', 0)}")
        
        if scrape_result.get('errors'):
            print(f"   ⚠️  Errors: {len(scrape_result['errors'])}")
            for error in scrape_result['errors'][:2]:  # Show first 2 errors
                print(f"      - {error}")
    
    # Test 3: Get Latest Data
    print("\n3. Testing Latest Data Retrieval...")
    latest_result = test_latest_endpoint(base_url)
    if "error" in latest_result:
        print(f"❌ Latest data retrieval failed: {latest_result['error']}")
    else:
        print(f"✅ Latest data retrieved: {latest_result.get('status', 'unknown')}")
        timestamp = latest_result.get('timestamp', 'unknown')
        print(f"   🕒 Last updated: {timestamp}")
    
    print("\n" + "=" * 50)
    print("🎉 Test completed!")


def demonstrate_api_usage():
    """Demonstrate how to use the API with real examples."""
    print("\n📖 API Usage Examples")
    print("=" * 50)
    
    print("\n1. Health Check:")
    print("   GET http://localhost:5000/health")
    
    print("\n2. Start Scraping:")
    print("   POST http://localhost:5000/scrape")
    print("   Content-Type: application/json")
    print("""
   {
     "yelp_business_id": "garaje-san-francisco",
     "amazon_asin": "B08N5WRWNW",
     "refresh_interval": 300
   }
   """)
    
    print("\n3. Get Latest Data:")
    print("   GET http://localhost:5000/latest")
    
    print("\n4. Stop Background Scraping:")
    print("   POST http://localhost:5000/stop")
    
    print("\n🔗 Example Inputs:")
    print("   Yelp Business ID: garaje-san-francisco")
    print("   Yelp URL: https://www.yelp.com/biz/garaje-san-francisco")
    print("   Amazon ASIN: B08N5WRWNW")
    print("   Amazon URL: https://www.amazon.com/dp/B08N5WRWNW")


if __name__ == "__main__":
    print("🚀 Review Scraper Test Suite")
    
    # Show API usage examples
    demonstrate_api_usage()
    
    # Ask user if they want to run tests
    user_input = input("\nWould you like to run the tests? (y/n): ").strip().lower()
    
    if user_input in ['y', 'yes']:
        run_basic_tests()
    else:
        print("Tests skipped. Start the server with 'python app.py' and run this script again.")
