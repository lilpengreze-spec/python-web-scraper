"""
Amazon Reviews Scraper

This module handles scraping reviews from Amazon using both the Amazon Product
Advertising API and HTML parsing fallback methods.
"""

import os
import re
import logging
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from typing import List, Dict, Optional, Any
from urllib.parse import urlparse, parse_qs
import time
import random

# Amazon Product Advertising API doesn't provide review data anyway
# We'll focus on web scraping which is more effective for reviews
AMAZON_API_AVAILABLE = False

logger = logging.getLogger(__name__)


class AmazonScraper:
    """
    Scraper for Amazon product reviews with API and HTML parsing support.
    """
    
    def __init__(self):
        """Initialize the Amazon scraper with API credentials if available."""
        self.access_key = os.getenv('AMAZON_ACCESS_KEY')
        self.secret_key = os.getenv('AMAZON_SECRET_KEY')
        self.partner_tag = os.getenv('AMAZON_PARTNER_TAG')
        self.amazon_api = None
        
        # Note: Amazon Product Advertising API doesn't provide review data
        # We primarily use web scraping for review collection
        logger.info("Amazon API not available - using web scraping only (API doesn't provide review data anyway)")
        
        # Setup session for web requests with rotating user agents
        self.session = requests.Session()
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:89.0) Gecko/20100101 Firefox/89.0'
        ]
        self._update_headers()
    
    def _update_headers(self):
        """Update session headers with a random user agent."""
        user_agent = random.choice(self.user_agents)
        self.session.headers.update({
            'User-Agent': user_agent,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
    
    def extract_asin(self, input_str: str) -> str:
        """
        Extract ASIN from Amazon URL or return the input if it's already an ASIN.
        
        Args:
            input_str: Amazon ASIN or product URL
            
        Returns:
            ASIN string
        """
        if not input_str:
            return ""
        
        # If it looks like an ASIN (10 alphanumeric characters), return as is
        if re.match(r'^[A-Z0-9]{10}$', input_str.upper()):
            return input_str.upper()
        
        try:
            # Extract ASIN from various Amazon URL formats
            asin_patterns = [
                r'/dp/([A-Z0-9]{10})',
                r'/product/([A-Z0-9]{10})',
                r'/ASIN/([A-Z0-9]{10})',
                r'asin=([A-Z0-9]{10})',
                r'/([A-Z0-9]{10})(?:/|$|\?)'
            ]
            
            for pattern in asin_patterns:
                match = re.search(pattern, input_str, re.IGNORECASE)
                if match:
                    return match.group(1).upper()
            
            return ""
            
        except Exception as e:
            logger.error(f"Error extracting ASIN from URL: {str(e)}")
            return ""
    
    def get_reviews_via_api(self, asin: str) -> List[Dict[str, Any]]:
        """
        Get reviews using the Amazon Product Advertising API.
        
        Note: The Amazon Product Advertising API does NOT provide review data.
        This method exists for completeness but will always fall back to scraping.
        
        Args:
            asin: Amazon ASIN
            
        Returns:
            List of review dictionaries
            
        Raises:
            Exception: Always raises since API doesn't support reviews
        """
        logger.warning("Amazon Product Advertising API doesn't provide review data")
        raise Exception("Amazon API doesn't support review retrieval - using web scraping instead")
    
    def get_reviews_via_scraping(self, asin: str) -> List[Dict[str, Any]]:
        """
        Get reviews using HTML parsing/web scraping.
        
        Args:
            asin: Amazon ASIN
            
        Returns:
            List of review dictionaries
        """
        try:
            # Update headers to avoid detection
            self._update_headers()
            
            # Try multiple URL formats for better success rate
            urls_to_try = [
                f"https://www.amazon.com/product-reviews/{asin}/ref=cm_cr_dp_d_show_all_btm",
                f"https://www.amazon.com/dp/{asin}/ref=cm_cr_dp_d_show_all_btm",
                f"https://www.amazon.com/product-reviews/{asin}"
            ]
            
            soup = None
            successful_url = None
            
            # Try each URL until one works
            for url in urls_to_try:
                try:
                    logger.info(f"Attempting to scrape Amazon reviews from: {url}")
                    
                    # Add random delay to avoid rate limiting
                    time.sleep(random.uniform(2, 5))
                    
                    # Make request with additional headers to appear more legitimate
                    headers = self.session.headers.copy()
                    headers.update({
                        'Referer': f'https://www.amazon.com/dp/{asin}',
                        'Sec-Fetch-Dest': 'document',
                        'Sec-Fetch-Mode': 'navigate',
                        'Sec-Fetch-Site': 'same-origin',
                        'Cache-Control': 'max-age=0'
                    })
                    
                    response = self.session.get(url, headers=headers, timeout=20)
                    
                    if response.status_code == 200:
                        soup = BeautifulSoup(response.content, 'html.parser')
                        successful_url = url
                        logger.info(f"Successfully retrieved page content from: {url}")
                        break
                    else:
                        logger.warning(f"HTTP {response.status_code} for URL: {url}")
                        
                except requests.RequestException as e:
                    logger.warning(f"Request failed for {url}: {str(e)}")
                    continue
            
            if not soup:
                raise Exception("Failed to retrieve any Amazon review pages")
            
            reviews = []
            
            # Multiple strategies to find review containers
            review_selectors = [
                {'selector': 'div', 'attrs': {'data-hook': 'review'}},
                {'selector': 'div', 'attrs': {'class': re.compile(r'.*review.*container.*')}},
                {'selector': 'div', 'attrs': {'id': re.compile(r'customer_review')}},
                {'selector': 'div', 'attrs': {'class': 'cr-original-review-content'}},
                {'selector': 'div', 'attrs': {'class': 'review-item'}}
            ]
            
            review_containers = []
            for selector in review_selectors:
                containers = soup.find_all(selector['selector'], selector['attrs'])
                if containers:
                    review_containers = containers
                    logger.info(f"Found {len(containers)} review containers using selector: {selector}")
                    break
            
            if not review_containers:
                # Fallback: look for any div containing review-like content
                review_containers = soup.find_all('div', string=re.compile(r'(review|rating|star)', re.I))
                logger.info(f"Fallback: Found {len(review_containers)} potential review containers")
            
            for i, container in enumerate(review_containers[:10]):  # Limit to 10 reviews
                try:
                    logger.debug(f"Processing review container {i+1}")
                    
                    # Extract reviewer name with multiple strategies
                    reviewer_name = self._extract_reviewer_name(container)
                    
                    # Extract rating with multiple strategies
                    rating = self._extract_rating(container)
                    
                    # Extract review title and text
                    review_title, review_text = self._extract_review_content(container)
                    
                    # Extract date
                    date = self._extract_review_date(container)
                    
                    # Extract helpful votes
                    helpful_votes = self._extract_helpful_votes(container)
                    
                    # Combine title and text
                    full_text = f"{review_title} {review_text}".strip()
                    
                    # Skip if no meaningful content
                    if not full_text and rating == 0:
                        continue
                    
                    review_data = {
                        'reviewer_name': reviewer_name or 'Anonymous',
                        'rating': rating,
                        'review_text': full_text,
                        'date': date,
                        'review_url': f"https://www.amazon.com/dp/{asin}",
                        'helpful_votes': helpful_votes,
                        'source': 'amazon_scraping'
                    }
                    reviews.append(review_data)
                    logger.debug(f"Successfully extracted review {i+1}: {len(full_text)} chars")
                    
                except Exception as e:
                    logger.warning(f"Error parsing individual Amazon review {i+1}: {str(e)}")
                    continue
            
            logger.info(f"Retrieved {len(reviews)} reviews via Amazon scraping from {successful_url}")
            return reviews
            
        except requests.RequestException as e:
            logger.error(f"Network error during Amazon scraping: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Amazon scraping error: {str(e)}")
            raise
    
    def _extract_reviewer_name(self, container) -> str:
        """Extract reviewer name from review container."""
        name_selectors = [
            ('span', {'class': 'a-profile-name'}),
            ('div', {'class': 'a-profile-content'}),
            ('a', {'class': 'a-profile'}),
            ('span', {'class': re.compile(r'.*profile.*name.*')}),
            ('div', {'class': re.compile(r'.*reviewer.*name.*')})
        ]
        
        for selector, attrs in name_selectors:
            elem = container.find(selector, attrs)
            if elem:
                name = elem.get_text(strip=True)
                if name and len(name) > 0:
                    return name
        return 'Anonymous'
    
    def _extract_rating(self, container) -> float:
        """Extract rating from review container."""
        rating_selectors = [
            ('i', {'data-hook': 'review-star-rating'}),
            ('span', {'class': 'a-icon-alt'}),
            ('i', {'class': re.compile(r'.*star.*')}),
            ('div', {'class': re.compile(r'.*rating.*')}),
            ('span', {'class': re.compile(r'.*star.*')})
        ]
        
        for selector, attrs in rating_selectors:
            elem = container.find(selector, attrs)
            if elem:
                # Try to extract rating from various text formats
                rating_text = elem.get('aria-label', '') or elem.get_text() or str(elem.get('class', []))
                rating_match = re.search(r'(\d+(?:\.\d+)?)', rating_text)
                if rating_match:
                    try:
                        return float(rating_match.group(1))
                    except ValueError:
                        continue
        return 0
    
    def _extract_review_content(self, container) -> tuple:
        """Extract review title and text from review container."""
        # Extract title
        title_selectors = [
            ('a', {'data-hook': 'review-title'}),
            ('span', {'data-hook': 'review-title'}),
            ('h4', {'class': 'review-title'}),
            ('h5', {'class': re.compile(r'.*title.*')}),
            ('div', {'class': re.compile(r'.*title.*')})
        ]
        
        review_title = ''
        for selector, attrs in title_selectors:
            elem = container.find(selector, attrs)
            if elem:
                title = elem.get_text(strip=True)
                if title and len(title) > 0:
                    review_title = title
                    break
        
        # Extract text
        text_selectors = [
            ('span', {'data-hook': 'review-body'}),
            ('div', {'data-hook': 'review-body'}),
            ('div', {'class': 'review-text'}),
            ('span', {'class': re.compile(r'.*review.*text.*')}),
            ('div', {'class': re.compile(r'.*review.*content.*')})
        ]
        
        review_text = ''
        for selector, attrs in text_selectors:
            elem = container.find(selector, attrs)
            if elem:
                text = elem.get_text(strip=True)
                if text and len(text) > 0:
                    review_text = text
                    break
        
        return review_title, review_text
    
    def _extract_review_date(self, container) -> str:
        """Extract review date from review container."""
        date_selectors = [
            ('span', {'data-hook': 'review-date'}),
            ('span', {'class': 'review-date'}),
            ('span', {'class': 'a-size-base'}),
            ('div', {'class': re.compile(r'.*date.*')}),
            ('time', {})
        ]
        
        for selector, attrs in date_selectors:
            elem = container.find(selector, attrs)
            if elem:
                date_text = elem.get_text(strip=True) or elem.get('datetime', '')
                if date_text:
                    # Extract date from "Reviewed in [Country] on [Date]" format
                    date_match = re.search(r'on (.+?)(?:\s*$)', date_text)
                    if date_match:
                        return date_match.group(1).strip()
                    else:
                        return date_text
        return ''
    
    def _extract_helpful_votes(self, container) -> str:
        """Extract helpful votes from review container."""
        helpful_selectors = [
            ('span', {'data-hook': 'helpful-vote-statement'}),
            ('span', {'class': 'review-votes'}),
            ('div', {'class': re.compile(r'.*helpful.*')}),
            ('span', {'class': re.compile(r'.*vote.*')})
        ]
        
        for selector, attrs in helpful_selectors:
            elem = container.find(selector, attrs)
            if elem:
                helpful_text = elem.get_text(strip=True)
                if helpful_text and len(helpful_text) > 0:
                    return helpful_text
        return ''
    
    def get_reviews(self, input_str: str) -> List[Dict[str, Any]]:
        """
        Get reviews from Amazon using API or scraping fallback.
        
        Args:
            input_str: Amazon ASIN or product URL
            
        Returns:
            List of review dictionaries
        """
        if not input_str:
            return []
        
        # Extract ASIN from input
        asin = self.extract_asin(input_str)
        if not asin:
            raise Exception("Invalid Amazon ASIN or URL")
        
        # Use web scraping (API doesn't support reviews anyway)
        return self.get_reviews_via_scraping(asin)
