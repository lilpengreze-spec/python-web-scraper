"""
Helper Utilities

This module provides various utility functions for logging, formatting,
and other common operations.
"""

import os
import logging
import json
from datetime import datetime
from typing import Dict, Any, List, Optional


def setup_logging() -> None:
    """
    Setup logging configuration for the application.
    """
    # Create logs directory if it doesn't exist
    os.makedirs('logs', exist_ok=True)
    
    # Configure logging format
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    date_format = '%Y-%m-%d %H:%M:%S'
    
    # Set log level based on environment
    log_level = os.getenv('LOG_LEVEL', 'INFO').upper()
    
    # Configure root logger
    logging.basicConfig(
        level=getattr(logging, log_level, logging.INFO),
        format=log_format,
        datefmt=date_format,
        handlers=[
            # Console handler
            logging.StreamHandler(),
            # File handler
            logging.FileHandler(
                'logs/scraper.log',
                mode='a',
                encoding='utf-8'
            )
        ]
    )
    
    # Set third-party library log levels
    logging.getLogger('requests').setLevel(logging.WARNING)
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('bs4').setLevel(logging.WARNING)


def format_response(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Format API response data for consistent output.
    
    Args:
        data: Raw response data
        
    Returns:
        Formatted response dictionary
    """
    if not isinstance(data, dict):
        return {
            'error': 'Invalid response data format',
            'timestamp': datetime.utcnow().isoformat() + 'Z'
        }
    
    # Ensure required fields exist
    formatted_data = {
        'timestamp': data.get('timestamp', datetime.utcnow().isoformat() + 'Z'),
        'status': data.get('status', 'unknown'),
        'yelp_reviews': data.get('yelp_reviews', []),
        'amazon_reviews': data.get('amazon_reviews', []),
        'errors': data.get('errors', [])
    }
    
    # Add statistics
    formatted_data['statistics'] = {
        'total_reviews': len(formatted_data['yelp_reviews']) + len(formatted_data['amazon_reviews']),
        'yelp_review_count': len(formatted_data['yelp_reviews']),
        'amazon_review_count': len(formatted_data['amazon_reviews']),
        'has_errors': len(formatted_data['errors']) > 0
    }
    
    # Add metadata if available
    if 'background_scraping' in data:
        formatted_data['background_scraping'] = data['background_scraping']
    
    if 'refresh_interval' in data:
        formatted_data['refresh_interval'] = data['refresh_interval']
    
    return formatted_data


def sanitize_text(text: str) -> str:
    """
    Sanitize text content for safe output.
    
    Args:
        text: Text to sanitize
        
    Returns:
        Sanitized text
    """
    if not isinstance(text, str):
        return ""
    
    # Remove excessive whitespace
    text = ' '.join(text.split())
    
    # Remove potentially dangerous characters
    dangerous_chars = ['<', '>', '"', "'", '&']
    for char in dangerous_chars:
        text = text.replace(char, '')
    
    # Limit length
    max_length = 5000
    if len(text) > max_length:
        text = text[:max_length] + '...'
    
    return text.strip()


def clean_review_data(reviews: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Clean and normalize review data.
    
    Args:
        reviews: List of review dictionaries
        
    Returns:
        Cleaned review list
    """
    cleaned_reviews = []
    
    for review in reviews:
        if not isinstance(review, dict):
            continue
        
        cleaned_review = {
            'reviewer_name': sanitize_text(str(review.get('reviewer_name', 'Anonymous'))),
            'rating': max(0, min(5, float(review.get('rating', 0)))),  # Ensure rating is 0-5
            'review_text': sanitize_text(str(review.get('review_text', ''))),
            'date': sanitize_text(str(review.get('date', ''))),
            'review_url': str(review.get('review_url', '')),
            'source': str(review.get('source', 'unknown'))
        }
        
        # Add additional fields if they exist
        if 'helpful_votes' in review:
            cleaned_review['helpful_votes'] = sanitize_text(str(review['helpful_votes']))
        
        # Only add reviews with meaningful content
        if cleaned_review['review_text'] or cleaned_review['rating'] > 0:
            cleaned_reviews.append(cleaned_review)
    
    return cleaned_reviews


def get_user_agent() -> str:
    """
    Get a random user agent string for web requests.
    
    Returns:
        User agent string
    """
    import random
    
    user_agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:89.0) Gecko/20100101 Firefox/89.0'
    ]
    
    return random.choice(user_agents)


def rate_limit_delay(min_delay: float = 1.0, max_delay: float = 3.0) -> None:
    """
    Add a random delay to avoid rate limiting.
    
    Args:
        min_delay: Minimum delay in seconds
        max_delay: Maximum delay in seconds
    """
    import time
    import random
    
    delay = random.uniform(min_delay, max_delay)
    time.sleep(delay)


def is_valid_json(json_str: str) -> bool:
    """
    Check if a string is valid JSON.
    
    Args:
        json_str: JSON string to validate
        
    Returns:
        True if valid JSON, False otherwise
    """
    try:
        json.loads(json_str)
        return True
    except (json.JSONDecodeError, TypeError):
        return False


def parse_date_string(date_str: str) -> Optional[str]:
    """
    Parse various date string formats and return ISO format.
    
    Args:
        date_str: Date string to parse
        
    Returns:
        ISO formatted date string or None if parsing fails
    """
    if not date_str:
        return None
    
    # Common date formats to try
    date_formats = [
        '%Y-%m-%d',
        '%m/%d/%Y',
        '%d/%m/%Y',
        '%B %d, %Y',
        '%b %d, %Y',
        '%Y-%m-%d %H:%M:%S',
        '%m/%d/%Y %H:%M:%S'
    ]
    
    for date_format in date_formats:
        try:
            parsed_date = datetime.strptime(date_str, date_format)
            return parsed_date.isoformat() + 'Z'
        except ValueError:
            continue
    
    # If no format matches, return the original string cleaned
    return sanitize_text(date_str)
