"""Download and fetch images from URLs"""

import requests
from pathlib import Path
from io import BytesIO
from PIL import Image
from typing import Optional
from bs4 import BeautifulSoup
import re

from ..utils.logger import get_logger
from ..utils.constants import TEMP_DIR, ZOONIVERSE_API_BASE, ZOONIVERSE_TIMEOUT

logger = get_logger(__name__)

class Downloader:
    """
    Handle downloading images from URLs and scraping Zooniverse.
    """
    
    @staticmethod
    def download_image(url: str, timeout: int = 10) -> Optional[Image.Image]:
        """
        Download image from URL.
        
        Args:
            url: Image URL
            timeout: Request timeout in seconds
            
        Returns:
            PIL Image or None if failed
        """
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(url, timeout=timeout, headers=headers)
            response.raise_for_status()
            
            image = Image.open(BytesIO(response.content))
            logger.info(f"Downloaded image from {url}")
            return image
        
        except requests.RequestException as e:
            logger.error(f"Error downloading image: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Error processing image: {str(e)}")
            return None
    
    @staticmethod
    def extract_zooniverse_image(zooniverse_url: str) -> Optional[str]:
        """
        Extract light curve image URL from Zooniverse subject page.
        
        Args:
            zooniverse_url: Zooniverse subject page URL
            
        Returns:
            Image URL or None if not found
        """
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(zooniverse_url, timeout=ZOONIVERSE_TIMEOUT, headers=headers)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Look for image tags in the page
            img_tags = soup.find_all('img')
            
            # Filter for likely light curve images
            light_curve_images = []
            for img in img_tags:
                src = img.get('src', '')
                alt = img.get('alt', '').lower()
                
                # Look for light curve indicators
                if any(keyword in alt for keyword in ['light curve', 'flux', 'transit', 'lightcurve']):
                    light_curve_images.append(src)
                # Also check src for common patterns
                elif any(pattern in src.lower() for pattern in ['light', 'curve', 'flux', 'transit', 'subject']):
                    light_curve_images.append(src)
            
            if light_curve_images:
                image_url = light_curve_images[0]
                # Handle relative URLs
                if not image_url.startswith('http'):
                    base_url = '/'.join(zooniverse_url.split('/')[:3])
                    image_url = base_url + (image_url if image_url.startswith('/') else '/' + image_url)
                
                logger.info(f"Extracted image URL from Zooniverse: {image_url}")
                return image_url
            
            logger.warning("No light curve image found in Zooniverse page")
            return None
        
        except requests.RequestException as e:
            logger.error(f"Error accessing Zooniverse page: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Error extracting image from Zooniverse: {str(e)}")
            return None
    
    @staticmethod
    def save_image_temp(image: Image.Image, filename: str = "temp_image.png") -> Optional[Path]:
        """
        Save image to temporary directory.
        
        Args:
            image: PIL Image object
            filename: Filename to save as
            
        Returns:
            Path to saved file or None if failed
        """
        try:
            temp_path = TEMP_DIR / filename
            image.save(temp_path)
            logger.info(f"Saved image to {temp_path}")
            return temp_path
        except Exception as e:
            logger.error(f"Error saving image: {str(e)}")
            return None
    
    @staticmethod
    def validate_url(url: str) -> bool:
        """
        Validate if URL is accessible.
        
        Args:
            url: URL to validate
            
        Returns:
            bool: True if URL is accessible
        """
        try:
            response = requests.head(url, timeout=5)
            return response.status_code < 400
        except Exception as e:
            logger.warning(f"URL validation failed: {str(e)}")
            return False