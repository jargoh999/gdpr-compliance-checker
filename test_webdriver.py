"""Test script to verify WebDriver functionality."""
import sys
import os
import logging
from typing import Optional

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('webdriver_test.log')
    ]
)

logger = logging.getLogger(__name__)

def test_webdriver():
    """Test the WebDriver initialization and basic functionality."""
    from services.web_driver import WebDriverService
    
    logger.info("Starting WebDriver test...")
    
    # Initialize the WebDriver service
    web_driver_service = WebDriverService()
    
    try:
        # Start the WebDriver
        logger.info("Starting WebDriver...")
        driver = web_driver_service.start_driver()
        
        # Test basic navigation
        logger.info("Navigating to example.com...")
        driver.get("https://example.com")
        
        # Verify page title
        title = driver.title
        logger.info(f"Page title: {title}")
        assert "Example Domain" in title, f"Unexpected page title: {title}"
        
        logger.info("WebDriver test completed successfully!")
        return True
        
    except Exception as e:
        logger.error(f"WebDriver test failed: {str(e)}", exc_info=True)
        return False
    finally:
        # Clean up
        logger.info("Quitting WebDriver...")
        web_driver_service.quit_driver()

if __name__ == "__main__":
    success = test_webdriver()
    sys.exit(0 if success else 1)
