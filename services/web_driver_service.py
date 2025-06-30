"""WebDriver service for Selenium and Playwright browser automation.

This module provides a robust WebDriver service that handles browser initialization,
management, and cleanup for both Selenium and Playwright browsers.
"""
import os
import sys
import time
import logging
import subprocess
from typing import Optional, Dict, Any, Union, List, Tuple

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Add console handler if not already present
if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    logger.addHandler(handler)

# Import browser automation libraries
try:
    from selenium import webdriver
    from selenium.webdriver.remote.webdriver import WebDriver
    from selenium.webdriver.chrome.service import Service as ChromeService
    from selenium.webdriver.chrome.options import Options as ChromeOptions
    from webdriver_manager.chrome import ChromeDriverManager
    from webdriver_manager.core.os_manager import ChromeType
    SELENIUM_AVAILABLE = True
except ImportError:
    logger.warning("Selenium not available. Some features may be limited.")
    SELENIUM_AVAILABLE = False

try:
    from playwright.sync_api import sync_playwright
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    logger.warning("Playwright not available. Some features may be limited.")
    PLAYWRIGHT_AVAILABLE = False

# Default browser options
DEFAULT_BROWSER_OPTIONS = {
    'headless': True,
    'no-sandbox': True,
    'disable-dev-shm-usage': True,
    'disable-gpu': True,
    'disable-extensions': True,
    'disable-infobars': True,
    'disable-notifications': True,
    'disable-browser-side-navigation': True,
    'disable-features': 'VizDisplayCompositor',
    'disable-setuid-sandbox': True,
    'disable-web-security': True,
    'ignore-certificate-errors': True,
    'remote-debugging-port': '9222',
}

class WebDriverService:
    """Service for managing browser automation with Selenium and Playwright.
    
    This class provides methods to start, manage, and clean up browser instances
    with support for both Selenium WebDriver and Playwright.
    """
    
    def __init__(self, headless: bool = True):
        """Initialize the WebDriver service.
        
        Args:
            headless: Whether to run browsers in headless mode by default.
        """
        self.headless = headless
        self.driver = None
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None
        
        # Set up environment variables
        self._setup_environment()
    
    def _setup_environment(self):
        """Set up environment variables for browser automation."""
        # Set display for headless mode
        os.environ['DISPLAY'] = ':99'
        
        # Set Chrome/Chromium paths
        chrome_paths = [
            '/usr/bin/google-chrome',
            '/usr/bin/chromium-browser',
            '/usr/bin/chromium',
            '/usr/local/bin/chromium',
            '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
            'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe'
        ]
        
        # Find Chrome/Chromium executable
        for path in chrome_paths:
            if os.path.isfile(path):
                os.environ['CHROME_BIN'] = path
                os.environ['CHROME_PATH'] = path
                logger.info(f"Using Chrome/Chromium at: {path}")
                break
        else:
            logger.warning("Could not find Chrome/Chromium executable")
        
        # Set Playwright browser path
        os.environ['PLAYWRIGHT_BROWSERS_PATH'] = os.path.expanduser('~/.cache/ms-playwright')
        
        # Create Playwright browsers directory if it doesn't exist
        os.makedirs(os.environ['PLAYWRIGHT_BROWSERS_PATH'], exist_ok=True)
    
    def start_selenium_chrome(self, options: Optional[Dict[str, Any]] = None) -> Optional[WebDriver]:
        """Start a Selenium Chrome WebDriver instance.
        
        Args:
            options: Additional browser options to override defaults.
            
        Returns:
            WebDriver instance if successful, None otherwise.
        """
        if not SELENIUM_AVAILABLE:
            logger.error("Selenium is not available. Please install it with: pip install selenium")
            return None
            
        try:
            # Configure Chrome options
            chrome_options = ChromeOptions()
            
            # Apply default options
            for option, value in DEFAULT_BROWSER_OPTIONS.items():
                if value is True:
                    chrome_options.add_argument(f'--{option}')
                elif isinstance(value, str):
                    chrome_options.add_argument(f'--{option}={value}')
            
            # Apply custom options
            if options:
                for option, value in options.items():
                    if value is True:
                        chrome_options.add_argument(f'--{option}')
                    elif isinstance(value, str):
                        chrome_options.add_argument(f'--{option}={value}')
            
            # Set Chrome binary location if available
            if 'CHROME_BIN' in os.environ:
                chrome_options.binary_location = os.environ['CHROME_BIN']
            
            # Set up ChromeDriver service
            service = ChromeService(ChromeDriverManager().install())
            
            # Start WebDriver
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            self.driver.set_window_size(1920, 1080)
            
            logger.info("Successfully started Selenium Chrome WebDriver")
            return self.driver
            
        except Exception as e:
            logger.error(f"Failed to start Selenium Chrome WebDriver: {e}")
            return None
    
    def start_playwright(self, browser_type: str = 'chromium') -> bool:
        """Start a Playwright browser instance.
        
        Args:
            browser_type: Type of browser to start ('chromium', 'firefox', or 'webkit').
            
        Returns:
            bool: True if successful, False otherwise.
        """
        if not PLAYWRIGHT_AVAILABLE:
            logger.error("Playwright is not available. Please install it with: pip install playwright")
            return False
            
        try:
            self.playwright = sync_playwright().start()
            
            # Select browser type
            if browser_type == 'chromium':
                self.browser = self.playwright.chromium.launch(headless=self.headless)
            elif browser_type == 'firefox':
                self.browser = self.playwright.firefox.launch(headless=self.headless)
            elif browser_type == 'webkit':
                self.browser = self.playwright.webkit.launch(headless=self.headless)
            else:
                logger.error(f"Unsupported browser type: {browser_type}")
                return False
            
            # Create a new browser context and page
            self.context = self.browser.new_context(viewport={'width': 1920, 'height': 1080})
            self.page = self.context.new_page()
            
            logger.info(f"Successfully started Playwright {browser_type} browser")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start Playwright {browser_type} browser: {e}")
            self.cleanup()
            return False
    
    def get_webdriver(self) -> Optional[WebDriver]:
        """Get the current WebDriver instance.
        
        Returns:
            WebDriver instance if available, None otherwise.
        """
        return self.driver
    
    def get_playwright_page(self):
        """Get the current Playwright page.
        
        Returns:
            Playwright page if available, None otherwise.
        """
        return self.page
    
    def cleanup(self):
        """Clean up all browser resources."""
        # Close Selenium WebDriver if it exists
        if self.driver:
            try:
                self.driver.quit()
                logger.info("Closed Selenium WebDriver")
            except Exception as e:
                logger.error(f"Error closing Selenium WebDriver: {e}")
            finally:
                self.driver = None
        
        # Close Playwright resources if they exist
        if self.context:
            try:
                self.context.close()
                logger.info("Closed Playwright context")
            except Exception as e:
                logger.error(f"Error closing Playwright context: {e}")
            finally:
                self.context = None
        
        if self.browser:
            try:
                self.browser.close()
                logger.info("Closed Playwright browser")
            except Exception as e:
                logger.error(f"Error closing Playwright browser: {e}")
            finally:
                self.browser = None
        
        # Stop Playwright if it's running
        if self.playwright:
            try:
                self.playwright.stop()
                logger.info("Stopped Playwright")
            except Exception as e:
                logger.error(f"Error stopping Playwright: {e}")
            finally:
                self.playwright = None
    
    def __enter__(self):
        """Context manager entry point."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit point."""
        self.cleanup()

# Create a singleton instance
web_driver_service = WebDriverService()
