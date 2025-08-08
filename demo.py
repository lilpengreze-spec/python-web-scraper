"""
Demo Script for Review Scraper

This script demonstrates the review scraper functionality with mock data
when actual scraping is blocked by anti-bot measures.
"""

import json
from datetime import datetime


def create_mock_yelp_reviews():
    """Create mock Yelp reviews for demonstration."""
    return [
        {
            "reviewer_name": "John D.",
            "rating": 5,
            "review_text": "Amazing food and great service! The ambiance is perfect for a date night. Highly recommend the salmon dish.",
            "date": "2025-08-01",
            "review_url": "https://www.yelp.com/biz/garaje-san-francisco",
            "source": "yelp_scraping"
        },
        {
            "reviewer_name": "Sarah M.",
            "rating": 4,
            "review_text": "Really good food, though it can get quite busy during peak hours. The wait staff was very attentive.",
            "date": "2025-07-28",
            "review_url": "https://www.yelp.com/biz/garaje-san-francisco",
            "source": "yelp_scraping"
        },
        {
            "reviewer_name": "Mike R.",
            "rating": 5,
            "review_text": "Best restaurant in the neighborhood! The chef really knows how to combine flavors. Will definitely be back.",
            "date": "2025-07-25",
            "review_url": "https://www.yelp.com/biz/garaje-san-francisco",
            "source": "yelp_scraping"
        }
    ]


def create_mock_amazon_reviews():
    """Create mock Amazon reviews for demonstration."""
    return [
        {
            "reviewer_name": "TechLover123",
            "rating": 4.0,
            "review_text": "Great sound quality for the price. Setup was easy and Alexa responds quickly. Only downside is the bass could be stronger.",
            "date": "August 3, 2025",
            "review_url": "https://www.amazon.com/dp/B08N5WRWNW",
            "helpful_votes": "15 people found this helpful",
            "source": "amazon_scraping"
        },
        {
            "reviewer_name": "MusicFan",
            "rating": 5.0,
            "review_text": "Perfect for my smart home setup. The voice recognition works great even with background noise. Highly recommended!",
            "date": "July 30, 2025",
            "review_url": "https://www.amazon.com/dp/B08N5WRWNW",
            "helpful_votes": "23 people found this helpful",
            "source": "amazon_scraping"
        },
        {
            "reviewer_name": "SmartHomePro",
            "rating": 4.0,
            "review_text": "Good value for money. Integrates well with other smart devices. The compact size is perfect for smaller spaces.",
            "date": "July 27, 2025",
            "review_url": "https://www.amazon.com/dp/B08N5WRWNW",
            "helpful_votes": "8 people found this helpful",
            "source": "amazon_scraping"
        }
    ]


def create_demo_response():
    """Create a complete demo response."""
    return {
        "timestamp": datetime.utcnow().isoformat() + 'Z',
        "status": "success",
        "yelp_reviews": create_mock_yelp_reviews(),
        "amazon_reviews": create_mock_amazon_reviews(),
        "errors": [],
        "statistics": {
            "total_reviews": 6,
            "yelp_review_count": 3,
            "amazon_review_count": 3,
            "has_errors": False
        }
    }


def demonstrate_api_response_format():
    """Show what a successful API response looks like."""
    print("🎯 Demo: Review Scraper API Response Format")
    print("=" * 60)
    
    demo_data = create_demo_response()
    
    print("\n📊 Response Statistics:")
    stats = demo_data['statistics']
    print(f"   Total Reviews: {stats['total_reviews']}")
    print(f"   Yelp Reviews: {stats['yelp_review_count']}")
    print(f"   Amazon Reviews: {stats['amazon_review_count']}")
    print(f"   Status: {demo_data['status']}")
    print(f"   Timestamp: {demo_data['timestamp']}")
    
    print("\n🔄 Sample Yelp Reviews:")
    for i, review in enumerate(demo_data['yelp_reviews'][:2]):
        print(f"   Review {i+1}:")
        print(f"      Reviewer: {review['reviewer_name']}")
        print(f"      Rating: {review['rating']}/5 stars")
        print(f"      Date: {review['date']}")
        print(f"      Text: {review['review_text'][:100]}...")
        print()
    
    print("🛍️  Sample Amazon Reviews:")
    for i, review in enumerate(demo_data['amazon_reviews'][:2]):
        print(f"   Review {i+1}:")
        print(f"      Reviewer: {review['reviewer_name']}")
        print(f"      Rating: {review['rating']}/5 stars")
        print(f"      Date: {review['date']}")
        print(f"      Helpful: {review['helpful_votes']}")
        print(f"      Text: {review['review_text'][:100]}...")
        print()
    
    print("📄 Complete JSON Response:")
    print(json.dumps(demo_data, indent=2))


def show_api_usage_examples():
    """Show how to use the API."""
    print("\n🚀 API Usage Examples")
    print("=" * 60)
    
    print("\n1. Health Check:")
    print("   curl http://localhost:5000/health")
    
    print("\n2. Scrape Reviews:")
    print("""   curl -X POST http://localhost:5000/scrape \\
        -H "Content-Type: application/json" \\
        -d '{
          "yelp_business_id": "garaje-san-francisco",
          "amazon_asin": "B08N5WRWNW",
          "refresh_interval": 300
        }'""")
    
    print("\n3. Get Latest Data:")
    print("   curl http://localhost:5000/latest")
    
    print("\n4. Stop Background Scraping:")
    print("   curl -X POST http://localhost:5000/stop")
    
    print("\n📝 Input Examples:")
    print("   Yelp Business ID: 'garaje-san-francisco'")
    print("   Yelp URL: 'https://www.yelp.com/biz/garaje-san-francisco'")
    print("   Amazon ASIN: 'B08N5WRWNW'")
    print("   Amazon URL: 'https://www.amazon.com/dp/B08N5WRWNW'")


def show_deployment_info():
    """Show deployment information."""
    print("\n🚀 Deployment Information")
    print("=" * 60)
    
    print("\n🔧 Local Development:")
    print("   1. Install dependencies: pip install -r requirements.txt")
    print("   2. Set up .env file with your API keys (optional)")
    print("   3. Start server: python app.py")
    print("   4. Server runs on: http://localhost:5000")
    
    print("\n☁️  Railway Deployment:")
    print("   1. Connect GitHub repository to Railway")
    print("   2. Set environment variables in Railway dashboard:")
    print("      - YELP_API_KEY (optional)")
    print("      - AMAZON_ACCESS_KEY (optional)")
    print("      - AMAZON_SECRET_KEY (optional)")
    print("      - AMAZON_PARTNER_TAG (optional)")
    print("   3. Deploy automatically with git push")
    
    print("\n⚙️  Environment Variables (.env file):")
    print("""   YELP_API_KEY=your_yelp_api_key
   AMAZON_ACCESS_KEY=your_amazon_access_key
   AMAZON_SECRET_KEY=your_amazon_secret_key
   AMAZON_PARTNER_TAG=your_amazon_partner_tag
   FLASK_ENV=production
   LOG_LEVEL=INFO""")


if __name__ == "__main__":
    print("🎉 Review Scraper Demo")
    print("This demo shows the expected API response format and usage examples.")
    print("Real scraping may be limited by anti-bot measures on Yelp and Amazon.")
    
    demonstrate_api_response_format()
    show_api_usage_examples()
    show_deployment_info()
    
    print("\n" + "=" * 60)
    print("🎯 Demo completed! Start the server with 'python app.py' to test the API.")
