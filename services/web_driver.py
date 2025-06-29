"""WebDriver service for Selenium browser automation"""
import os
import sys
import logging
from typing import Optional, Dict, Any, Union
from selenium import webdriver
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.core.utils import ChromeType

# Import our utility functions
from utils.web_driver_utils import get_webdriver, close_webdriver, is_chrome_installed

# Set logger level to WARNING to reduce noise
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.WARNING)

from config.constants import BROWSER_OPTIONS

class WebDriverService:
    """Service for managing Selenium WebDriver instances"""
    
    def __init__(self, headless: bool = True):
        """Initialize the WebDriver service
        
        Args:
            headless: Whether to run browser in headless mode
        """
        self.headless = headless
        self.driver: Optional[webdriver.Chrome] = None
    
    def start_driver(self, options: Optional[Dict[str, Any]] = None) -> WebDriver:
        """Start a new Chrome/Chromium WebDriver instance
        
        Args:
            options: Additional options to override defaults
            
        Returns:
            WebDriver: Configured WebDriver instance
        """
        try:
            # Use our utility function to get a WebDriver instance
            self.driver = get_webdriver()
            
            # Apply additional options if provided
            if options:
                for key, value in (options.items() if options else {}):
                    if key.startswith('--'):
                        self.driver.add_argument(f"{key}={value}" if value else key)
            
            # Set window size for consistency
            self.driver.set_window_size(1920, 1080)
            
            return self.driver
            
        except Exception as e:
            logging.error(f"Failed to start WebDriver: {str(e)}")
            # Try to use Playwright as a last resort
            logging.warning("Attempting to use Playwright as fallback...")
            try:
                from playwright.sync_api import sync_playwright
                playwright = sync_playwright().start()
                browser = playwright.chromium.launch(headless=True)
                self.driver = browser
                return self.driver
            except Exception as play_err:
                logging.error(f"Failed to start Playwright: {str(play_err)}")
                raise RuntimeError(f"Failed to start any browser: {str(e)}") from e
    
    def _get_chrome_options(self, custom_options: Optional[Dict[str, Any]] = None) -> Options:
        """Get Chrome/Chromium options with default and custom settings
        
        Args:
            custom_options: Custom options to override defaults
            
        Returns:
            Options: Configured Chrome/Chromium options
        """
        # Use our utility function to get base options
        options = Options()
        
        # Common options
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--disable-extensions')
        options.add_argument('--disable-software-rasterizer')
        options.add_argument('--disable-setuid-sandbox')
        options.add_argument('--disable-notifications')
        options.add_argument('--disable-infobars')
        options.add_argument('--disable-web-security')
        options.add_argument('--disable-blink-features=AutomationControlled')
        
        # Headless mode for server environments
        if os.environ.get('STREAMLIT_SERVER_RUNNING', '').lower() == 'true':
            options.add_argument('--headless=new')
            options.add_argument('--window-size=1920,1080')
        
        # Set Chrome preferences
        prefs = {
            'profile.password_manager_enabled': False,
            'profile.default_content_setting_values.notifications': 2,
            'credentials_enable_service': False,
            'profile.password_manager_enabled': False
        }
        
        # Add any custom preferences if provided
        if custom_options and 'prefs' in custom_options:
            prefs.update(custom_options['prefs'])
            
        options.add_experimental_option('prefs', prefs)
        
        # Apply any custom options if provided
        if custom_options:
            for key, value in custom_options.items():
                if key.startswith('--'):
                    options.add_argument(f"{key}={value}" if value else key)
        
        # Enable performance logging
        options.set_capability('goog:loggingPrefs', {'performance': 'ALL'})
        
        return options
    
    def get_driver(self) -> webdriver.Chrome:
        """Get the current WebDriver instance, starting one if needed
        
        Returns:
            webdriver.Chrome: The current WebDriver instance
        """
        if not self.driver:
            return self.start_driver()
        return self.driver
    
    def quit_driver(self) -> None:
        """Quit the current WebDriver instance if it exists"""
        if self.driver:
            try:
                close_webdriver(self.driver)
            except Exception as e:
                print(f"Error closing WebDriver: {str(e)}")
            finally:
                self.driver = None
    
    def __enter__(self):
        """Context manager entry"""
        return self.get_driver()
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.quit_driver()

# Singleton instance
web_driver_service = WebDriverService()
