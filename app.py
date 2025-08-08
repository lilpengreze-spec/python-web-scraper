"""
Main Flask Application for Yelp and Amazon Review Scraper

This application provides REST API endpoints to scrape reviews from Yelp and Amazon
in real-time, with support for both API access and HTML parsing fallback.
"""

import os
import sys
import json
import logging
import threading
import time
from datetime import datetime
from typing import Dict, List, Optional, Any

from flask import Flask, request, jsonify
from dotenv import load_dotenv

# Add the current directory to Python path to help with imports
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)
sys.path.insert(0, '/app')  # Railway deployment path

# Debug: Print current directory and check if scrapers exists
print(f"Current directory: {current_dir}")
print(f"Files in current directory: {os.listdir(current_dir) if os.path.exists(current_dir) else 'Directory not found'}")
scrapers_path = os.path.join(current_dir, 'scrapers')
print(f"Scrapers directory exists: {os.path.exists(scrapers_path)}")
if os.path.exists(scrapers_path):
    print(f"Files in scrapers: {os.listdir(scrapers_path)}")

# Additional sanity checks (as suggested by expert)
print(">> sys.path:", sys.path)
print(">> /app contents:", os.listdir("/app") if os.path.exists("/app") else "/app does not exist")
print(">> /app/scrapers exists:", os.path.isdir("/app/scrapers"))
print(">> Working directory:", os.getcwd())

from scrapers.yelp_scraper import YelpScraper
from scrapers.amazon_scraper import AmazonScraper
from utils.validators import validate_input
from utils.helpers import setup_logging, format_response

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

# Global storage for latest scraped data
latest_data = {
    'timestamp': None,
    'yelp_reviews': [],
    'amazon_reviews': [],
    'status': 'no_data',
    'errors': []
}

# Initialize scrapers
yelp_scraper = YelpScraper()
amazon_scraper = AmazonScraper()

# Global variables for background scraping
scraping_thread = None
stop_scraping = threading.Event()


def scrape_reviews(yelp_input: str, amazon_input: str, refresh_interval: Optional[int] = None) -> Dict[str, Any]:
    """
    Scrape reviews from both Yelp and Amazon sources.
    
    Args:
        yelp_input: Yelp business ID or URL
        amazon_input: Amazon ASIN or product URL
        refresh_interval: Optional interval in seconds for repeated scraping
    
    Returns:
        Dictionary containing scraped reviews and metadata
    """
    global latest_data
    
    try:
        logger.info(f"Starting scrape for Yelp: {yelp_input}, Amazon: {amazon_input}")
        
        # Initialize result structure
        result = {
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'yelp_reviews': [],
            'amazon_reviews': [],
            'status': 'success',
            'errors': []
        }
        
        # Scrape Yelp reviews
        if yelp_input:
            try:
                yelp_reviews = yelp_scraper.get_reviews(yelp_input)
                result['yelp_reviews'] = yelp_reviews
                logger.info(f"Successfully scraped {len(yelp_reviews)} Yelp reviews")
            except Exception as e:
                error_msg = f"Yelp scraping failed: {str(e)}"
                logger.error(error_msg)
                result['errors'].append(error_msg)
        
        # Scrape Amazon reviews
        if amazon_input:
            try:
                amazon_reviews = amazon_scraper.get_reviews(amazon_input)
                result['amazon_reviews'] = amazon_reviews
                logger.info(f"Successfully scraped {len(amazon_reviews)} Amazon reviews")
            except Exception as e:
                error_msg = f"Amazon scraping failed: {str(e)}"
                logger.error(error_msg)
                result['errors'].append(error_msg)
        
        # Update status based on results
        if result['errors'] and not result['yelp_reviews'] and not result['amazon_reviews']:
            result['status'] = 'failed'
        elif result['errors']:
            result['status'] = 'partial_success'
        
        # Update global data
        latest_data = result
        
        return result
        
    except Exception as e:
        error_msg = f"General scraping error: {str(e)}"
        logger.error(error_msg)
        
        result = {
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'yelp_reviews': [],
            'amazon_reviews': [],
            'status': 'failed',
            'errors': [error_msg]
        }
        
        latest_data = result
        return result


def background_scraper(yelp_input: str, amazon_input: str, refresh_interval: int):
    """
    Background thread function for continuous scraping.
    
    Args:
        yelp_input: Yelp business ID or URL
        amazon_input: Amazon ASIN or product URL
        refresh_interval: Interval in seconds between scraping attempts
    """
    logger.info(f"Starting background scraper with {refresh_interval}s interval")
    
    while not stop_scraping.is_set():
        scrape_reviews(yelp_input, amazon_input)
        
        # Wait for the specified interval or until stop event is set
        if stop_scraping.wait(refresh_interval):
            break
    
    logger.info("Background scraper stopped")


@app.route('/', methods=['GET'])
def home():
    """Root endpoint with API information."""
    return jsonify({
        'service': 'Python Web Scraper API',
        'version': '1.0.0',
        'description': 'Production-ready web scraper for Yelp and Amazon reviews',
        'endpoints': {
            'health': '/health - GET - Health check',
            'scrape': '/scrape - GET - Scrape reviews (supports URL parameters)',
            'latest': '/latest - GET - Get latest scraped data',
            'stop': '/stop - POST - Stop background scraping'
        },
        'usage': {
            'yelp_example': '/scrape?yelp_url=https://www.yelp.com/biz/restaurant-name',
            'amazon_example': '/scrape?amazon_url=https://www.amazon.com/dp/B08N5WRWNW',
            'both_example': '/scrape?yelp_url=...&amazon_url=...'
        }
    })


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for monitoring."""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat() + 'Z',
        'service': 'python-web-scraper'
    })


@app.route('/scrape', methods=['GET'])
def scrape_endpoint():
    """
    GET endpoint to scrape reviews from Yelp and/or Amazon.
    
    Query Parameters:
    - yelp_url: Yelp business URL or ID
    - amazon_url: Amazon product URL or ASIN
    - refresh_interval: Optional interval in seconds for continuous scraping
    """
    global scraping_thread, stop_scraping
    
    try:
        # Get URL parameters
        yelp_input = request.args.get('yelp_url', '')
        amazon_input = request.args.get('amazon_url', '')
        refresh_interval = request.args.get('refresh_interval', type=int)
        
        # Validate that at least one URL is provided
        if not yelp_input and not amazon_input:
            return jsonify({
                'error': 'Please provide at least one URL parameter: yelp_url or amazon_url',
                'example': '/scrape?yelp_url=https://www.yelp.com/biz/restaurant-name'
            }), 400
        
        # Stop any existing background scraping
        if scraping_thread and scraping_thread.is_alive():
            stop_scraping.set()
            scraping_thread.join(timeout=5)
            stop_scraping.clear()
        
        # Perform immediate scraping
        result = scrape_reviews(yelp_input, amazon_input)
        
        # Start background scraping if refresh interval is specified
        if refresh_interval and refresh_interval > 0:
            scraping_thread = threading.Thread(
                target=background_scraper,
                args=(yelp_input, amazon_input, refresh_interval),
                daemon=True
            )
            scraping_thread.start()
            result['background_scraping'] = True
            result['refresh_interval'] = refresh_interval
        
        return jsonify(format_response(result))
        
    except Exception as e:
        logger.error(f"Error in scrape endpoint: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@app.route('/latest', methods=['GET'])
def get_latest():
    """
    GET endpoint to retrieve the latest scraped data.
    """
    try:
        return jsonify(format_response(latest_data))
    except Exception as e:
        logger.error(f"Error in latest endpoint: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@app.route('/stop', methods=['POST'])
def stop_scraping_endpoint():
    """
    POST endpoint to stop background scraping.
    """
    global scraping_thread, stop_scraping
    
    try:
        if scraping_thread and scraping_thread.is_alive():
            stop_scraping.set()
            scraping_thread.join(timeout=5)
            stop_scraping.clear()
            return jsonify({'message': 'Background scraping stopped', 'status': 'success'})
        else:
            return jsonify({'message': 'No background scraping active', 'status': 'info'})
    except Exception as e:
        logger.error(f"Error stopping scraping: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return jsonify({'error': 'Endpoint not found'}), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    logger.error(f"Internal server error: {str(error)}")
    return jsonify({'error': 'Internal server error'}), 500


if __name__ == '__main__':
    # Initialize logging
    logger.info("Starting Python Web Scraper API")
    
    # Get configuration from environment
    debug = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    port = int(os.getenv('PORT', 5000))
    host = os.getenv('HOST', '0.0.0.0')
    
    logger.info(f"Server starting on {host}:{port}")
    
    # Start the Flask application
    app.run(
        host=host,
        port=port,
        debug=debug,
        threaded=True
    )

