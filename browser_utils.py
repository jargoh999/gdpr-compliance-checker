"""Utility functions for browser initialization and management."""
import os
import logging
import subprocess
from typing import Optional, Dict, Any
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager

logger = logging.getLogger(__name__)

def setup_chrome_options(headless: bool = True) -> ChromeOptions:
    """Configure Chrome options for Selenium.
    
    Args:
        headless: Whether to run in headless mode
        
    Returns:
        Configured ChromeOptions instance
    """
    options = ChromeOptions()
    
    # Set Chrome binary location
    chrome_bin = os.environ.get('CHROME_BIN', '/usr/bin/google-chrome')
    options.binary_location = chrome_bin
    
    # Common Chrome arguments
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument('--disable-software-rasterizer')
    options.add_argument('--disable-extensions')
    options.add_argument('--disable-infobars')
    options.add_argument('--disable-notifications')
    options.add_argument('--disable-browser-side-navigation')
    options.add_argument('--disable-features=VizDisplayCompositor')
    options.add_argument('--disable-setuid-sandbox')
    options.add_argument('--disable-web-security')
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--remote-debugging-port=9222')
    
    if headless:
        options.add_argument('--headless')
    
    # Additional options for better stability
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    options.add_experimental_option('useAutomationExtension', False)
    
    return options

def get_chrome_driver(headless: bool = True) -> Optional[webdriver.Chrome]:
    """Get a Chrome WebDriver instance with retry logic.
    
    Args:
        headless: Whether to run in headless mode
        
    Returns:
        Configured WebDriver instance or None if failed
    """
    max_retries = 3
    for attempt in range(max_retries):
        try:
            # Set up Chrome options
            options = setup_chrome_options(headless)
            
            # Configure ChromeDriver
            service = ChromeService(ChromeDriverManager().install())
            
            # Initialize WebDriver
            driver = webdriver.Chrome(service=service, options=options)
            driver.set_page_load_timeout(30)
            
            logger.info("Successfully initialized Chrome WebDriver")
            return driver
            
        except Exception as e:
            logger.warning(f"Attempt {attempt + 1} failed to initialize Chrome WebDriver: {e}")
            if attempt == max_retries - 1:
                logger.error("Max retries reached, giving up on Chrome WebDriver")
                return None
            
            # Wait before retry
            import time
            time.sleep(2 ** attempt)  # Exponential backoff
    
    return None

def setup_playwright() -> bool:
    """Set up Playwright browsers.
    
    Returns:
        bool: True if setup was successful, False otherwise
    """
    try:
        # Ensure Playwright browsers are installed
        os.environ['PLAYWRIGHT_BROWSERS_PATH'] = os.path.expanduser('~/.cache/ms-playwright')
        os.makedirs(os.environ['PLAYWRIGHT_BROWSERS_PATH'], exist_ok=True)
        
        # Install browsers if not present
        from playwright.sync_api import sync_playwright
        
        with sync_playwright() as p:
            for browser_type in [p.chromium, p.firefox, p.webkit]:
                try:
                    browser = browser_type.launch(headless=True)
                    browser.close()
                    logger.info(f"Successfully initialized {browser_type.name} browser")
                except Exception as e:
                    logger.warning(f"Failed to initialize {browser_type.name} browser: {e}")
                    return False
        
        return True
    except Exception as e:
        logger.error(f"Failed to set up Playwright: {e}")
        return False

def ensure_browser_setup() -> bool:
    """Ensure all required browsers are set up.
    
    Returns:
        bool: True if all browsers are set up, False otherwise
    """
    # Test Chrome WebDriver
    chrome_ok = False
    try:
        driver = get_chrome_driver()
        if driver:
            driver.quit()
            chrome_ok = True
            logger.info("Chrome WebDriver test passed")
    except Exception as e:
        logger.error(f"Chrome WebDriver test failed: {e}")
    
    # Test Playwright
    playwright_ok = setup_playwright()
    
    return chrome_ok or playwright_ok  # At least one should work
