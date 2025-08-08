"""
Yelp Reviews Scraper

This module handles scraping reviews from Yelp using both the Yelp Fusion API
and HTML parsing fallback methods.
"""

import os
import re
import logging
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from typing import List, Dict, Optional, Any
from urllib.parse import urlparse, parse_qs

try:
    from yelpapi import YelpAPI
    YELP_API_AVAILABLE = True
except ImportError:
    YELP_API_AVAILABLE = False

logger = logging.getLogger(__name__)


class YelpScraper:
    """
    Scraper for Yelp business reviews with API and HTML parsing support.
    """
    
    def __init__(self):
        """Initialize the Yelp scraper with API key if available."""
        self.api_key = os.getenv('YELP_API_KEY')
        self.yelp_api = None
        
        # Initialize Yelp API if available and key is provided
        if YELP_API_AVAILABLE and self.api_key:
            try:
                self.yelp_api = YelpAPI(self.api_key)
                logger.info("Yelp API initialized successfully")
            except Exception as e:
                logger.warning(f"Failed to initialize Yelp API: {str(e)}")
                self.yelp_api = None
        else:
            logger.info("Yelp API not available, will use HTML parsing")
        
        # Setup session for web requests
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
    
    def extract_business_id(self, input_str: str) -> str:
        """
        Extract business ID from Yelp URL or return the input if it's already an ID.
        
        Args:
            input_str: Yelp business ID or URL
            
        Returns:
            Business ID string
        """
        if not input_str:
            return ""
        
        # If it's already a business ID (no URL structure), return as is
        if not input_str.startswith('http'):
            return input_str
        
        try:
            # Parse URL to extract business ID
            parsed_url = urlparse(input_str)
            
            # Extract from path (e.g., /biz/business-name -> business-name)
            if '/biz/' in parsed_url.path:
                business_id = parsed_url.path.split('/biz/')[-1]
                # Remove any additional path segments
                business_id = business_id.split('/')[0].split('?')[0]
                return business_id
            
            return ""
            
        except Exception as e:
            logger.error(f"Error extracting business ID from URL: {str(e)}")
            return ""
    
    def get_reviews_via_api(self, business_id: str) -> List[Dict[str, Any]]:
        """
        Get reviews using the Yelp Fusion API.
        
        Args:
            business_id: Yelp business ID
            
        Returns:
            List of review dictionaries
        """
        if not self.yelp_api:
            raise Exception("Yelp API not available")
        
        try:
            # Get business reviews
            reviews_response = self.yelp_api.reviews_query(id=business_id)
            
            reviews = []
            for review in reviews_response.get('reviews', [])[:10]:  # Limit to 10 reviews
                review_data = {
                    'reviewer_name': review.get('user', {}).get('name', 'Anonymous'),
                    'rating': review.get('rating', 0),
                    'review_text': review.get('text', ''),
                    'date': review.get('time_created', ''),
                    'review_url': review.get('url', ''),
                    'source': 'yelp_api'
                }
                reviews.append(review_data)
            
            logger.info(f"Retrieved {len(reviews)} reviews via Yelp API")
            return reviews
            
        except Exception as e:
            logger.error(f"Yelp API error: {str(e)}")
            raise
    
    def get_reviews_via_scraping(self, business_id: str) -> List[Dict[str, Any]]:
        """
        Get reviews using HTML parsing/web scraping.
        
        Args:
            business_id: Yelp business ID
            
        Returns:
            List of review dictionaries
        """
        try:
            # Construct Yelp URL
            url = f"https://www.yelp.com/biz/{business_id}"
            
            # Make request
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            # Parse HTML
            soup = BeautifulSoup(response.content, 'html.parser')
            
            reviews = []
            
            # Find review containers (Yelp's structure may change)
            review_containers = soup.find_all('div', {'data-testid': 'serp-ia-card'}) or \
                               soup.find_all('div', class_=re.compile(r'review.*')) or \
                               soup.find_all('li', class_=re.compile(r'review.*'))
            
            if not review_containers:
                # Try alternative selectors
                review_containers = soup.find_all('div', class_='review-content') or \
                                   soup.find_all('div', class_='review-wrapper')
            
            for container in review_containers[:10]:  # Limit to 10 reviews
                try:
                    # Extract reviewer name
                    name_elem = container.find('span', class_=re.compile(r'user.*name')) or \
                               container.find('a', class_=re.compile(r'user.*link')) or \
                               container.find('div', class_=re.compile(r'user.*info'))
                    
                    reviewer_name = 'Anonymous'
                    if name_elem:
                        reviewer_name = name_elem.get_text(strip=True)
                    
                    # Extract rating
                    rating_elem = container.find('div', {'aria-label': re.compile(r'\d+ star')}) or \
                                 container.find('div', class_=re.compile(r'rating')) or \
                                 container.find('span', class_=re.compile(r'star'))
                    
                    rating = 0
                    if rating_elem:
                        rating_text = rating_elem.get('aria-label', '') or rating_elem.get_text()
                        rating_match = re.search(r'(\d+)', rating_text)
                        if rating_match:
                            rating = int(rating_match.group(1))
                    
                    # Extract review text
                    text_elem = container.find('span', class_=re.compile(r'raw__')) or \
                               container.find('p', class_=re.compile(r'comment')) or \
                               container.find('div', class_=re.compile(r'review.*text'))
                    
                    review_text = ''
                    if text_elem:
                        review_text = text_elem.get_text(strip=True)
                    
                    # Extract date
                    date_elem = container.find('span', class_=re.compile(r'date')) or \
                               container.find('time') or \
                               container.find('div', class_=re.compile(r'date'))
                    
                    date = ''
                    if date_elem:
                        date = date_elem.get_text(strip=True) or date_elem.get('datetime', '')
                    
                    # Skip if no meaningful content
                    if not review_text and rating == 0:
                        continue
                    
                    review_data = {
                        'reviewer_name': reviewer_name,
                        'rating': rating,
                        'review_text': review_text,
                        'date': date,
                        'review_url': url,
                        'source': 'yelp_scraping'
                    }
                    reviews.append(review_data)
                    
                except Exception as e:
                    logger.warning(f"Error parsing individual review: {str(e)}")
                    continue
            
            logger.info(f"Retrieved {len(reviews)} reviews via Yelp scraping")
            return reviews
            
        except requests.RequestException as e:
            logger.error(f"Network error during Yelp scraping: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Yelp scraping error: {str(e)}")
            raise
    
    def get_reviews(self, input_str: str) -> List[Dict[str, Any]]:
        """
        Get reviews from Yelp using API or scraping fallback.
        
        Args:
            input_str: Yelp business ID or URL
            
        Returns:
            List of review dictionaries
        """
        if not input_str:
            return []
        
        # Extract business ID from input
        business_id = self.extract_business_id(input_str)
        if not business_id:
            raise Exception("Invalid Yelp business ID or URL")
        
        # Try API first if available
        if self.yelp_api:
            try:
                return self.get_reviews_via_api(business_id)
            except Exception as e:
                logger.warning(f"Yelp API failed, falling back to scraping: {str(e)}")
        
        # Fallback to scraping
        return self.get_reviews_via_scraping(business_id)
