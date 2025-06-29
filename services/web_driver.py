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
        """Start a new Chrome/Chromium WebDriver instance with fallback mechanisms.
        
        Args:
            options: Additional options to override defaults. Can be None, a dictionary,
                    or a list of command-line arguments.
            
        Returns:
            WebDriver: Configured WebDriver instance
            
        Raises:
            RuntimeError: If no WebDriver can be started
        """
        # Close existing driver if any
        if self.driver:
            try:
                self.quit_driver()
            except Exception as e:
                logging.warning(f"Error closing existing driver: {str(e)}")
        
        # Attempt to start WebDriver with different configurations
        attempts = [
            self._try_start_webdriver(options, headless=True),
            self._try_start_webdriver(options, headless=False),
            self._try_start_playwright()
        ]
        
        # Return the first successful attempt
        for attempt in attempts:
            if attempt and attempt.get('success') and attempt.get('driver'):
                self.driver = attempt['driver']
                return self.driver
        
        # If we get here, all attempts failed
        error_msgs = "\n".join(
            f"Attempt {i+1}: {attempt.get('error', 'Unknown error')}"
            for i, attempt in enumerate(attempts)
            if not attempt.get('success')
        )
        raise RuntimeError(f"Failed to start WebDriver after multiple attempts. Errors:\n{error_msgs}")
    
    def _try_start_webdriver(self, options: Optional[Dict[str, Any]], headless: bool = True) -> dict:
        """Attempt to start a WebDriver instance with the given options."""
        try:
            # Get Chrome options with the specified settings
            chrome_options = self._get_chrome_options(options)
            
            # Set headless mode if requested
            if headless and '--headless' not in str(chrome_options.arguments):
                chrome_options.add_argument('--headless=new')
            
            # Try to get a WebDriver instance
            self.driver = webdriver.Chrome(
                service=Service(ChromeDriverManager().install()),
                options=chrome_options
            )
            
            # Set a reasonable window size
            self.driver.set_window_size(1920, 1080)
            
            # Verify the driver is working
            self.driver.get('about:blank')
            
            return {
                'success': True,
                'driver': self.driver,
                'type': 'selenium',
                'headless': headless
            }
            
        except Exception as e:
            error_msg = str(e)
            logging.warning(f"WebDriver start attempt failed (headless={headless}): {error_msg}")
            
            # Clean up if needed
            if hasattr(self, 'driver') and self.driver:
                try:
                    self.driver.quit()
                except:
                    pass
                self.driver = None
                
            return {
                'success': False,
                'error': error_msg,
                'type': 'selenium',
                'headless': headless
            }
    
    def _try_start_playwright(self) -> dict:
        """Attempt to start a Playwright instance as a fallback."""
        try:
            from playwright.sync_api import sync_playwright
            
            playwright = sync_playwright().start()
            browser = playwright.chromium.launch(headless=True)
            context = browser.new_context(viewport={'width': 1920, 'height': 1080})
            page = context.new_page()
            
            # Verify the browser is working
            page.goto('about:blank')
            
            return {
                'success': True,
                'driver': browser,
                'context': context,
                'page': page,
                'type': 'playwright',
                'headless': True
            }
            
        except Exception as e:
            error_msg = str(e)
            logging.warning(f"Playwright start attempt failed: {error_msg}")
            
            # Clean up if needed
            if 'browser' in locals():
                try:
                    browser.close()
                except:
                    pass
                
            return {
                'success': False,
                'error': error_msg,
                'type': 'playwright',
                'headless': True
            }
    
    def _get_chrome_options(self, custom_options: Optional[Dict[str, Any]] = None) -> Options:
        """Get Chrome/Chromium options with default and custom settings
        
        Args:
            custom_options: Custom options to override defaults
            
        Returns:
            Options: Configured Chrome/Chromium options
        """
        try:
            # Initialize Chrome options
            options = Options()
            
            # Common options
            chrome_args = [
                '--no-sandbox',
                '--disable-dev-shm-usage',
                '--disable-gpu',
                '--disable-extensions',
                '--disable-software-rasterizer',
                '--disable-setuid-sandbox',
                '--disable-notifications',
                '--disable-infobars',
                '--disable-web-security',
                '--disable-blink-features=AutomationControlled'
            ]
            
            # Add all common arguments
            for arg in chrome_args:
                options.add_argument(arg)
            
            # Set headless mode for server environments
            if os.environ.get('STREAMLIT_SERVER_RUNNING', '').lower() == 'true':
                options.add_argument('--headless=new')
                options.add_argument('--window-size=1920,1080')
            
            # Default preferences
            prefs = {
                'profile.password_manager_enabled': False,
                'profile.default_content_setting_values.notifications': 2,
                'credentials_enable_service': False,
                'profile.default_content_settings.popups': 0,
                'download_restrictions': 3,
                'safebrowsing.enabled': True
            }
            
            # Update with any custom preferences if provided
            if custom_options and isinstance(custom_options, dict):
                if 'prefs' in custom_options and isinstance(custom_options['prefs'], dict):
                    prefs.update(custom_options['prefs'])
                
                # Handle additional arguments
                for key, value in custom_options.items():
                    if key != 'prefs' and key.startswith('--'):
                        arg = f"{key}={value}" if value and not isinstance(value, bool) else key
                        options.add_argument(arg)
            
            # Apply preferences
            options.add_experimental_option('prefs', prefs)
            
            # Enable performance logging
            options.set_capability('goog:loggingPrefs', {'performance': 'ALL'})
            
            return options
            
        except Exception as e:
            logging.error(f"Error configuring Chrome options: {str(e)}")
            # Return basic options if there was an error
            options = Options()
            options.add_argument('--headless=new')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
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
        """Safely close the WebDriver or Playwright browser instance if it exists"""
        if not self.driver:
            return
            
        try:
            # Check if it's a Playwright browser
            if hasattr(self.driver, 'close'):
                # Try to get the browser type for logging
                browser_type = getattr(self.driver, '_browser_type', 'unknown')
                logging.info(f"Closing Playwright browser ({browser_type})")
                
                # Close all contexts and the browser
                if hasattr(self.driver, 'contexts'):
                    for context in self.driver.contexts:
                        try:
                            context.close()
                        except Exception as e:
                            logging.warning(f"Error closing context: {str(e)}")
                
                try:
                    self.driver.close()
                except Exception as e:
                    logging.warning(f"Error closing browser: {str(e)}")
                
                # Stop Playwright if we can access it
                if hasattr(self.driver, '_playwright') and self.driver._playwright:
                    try:
                        self.driver._playwright.stop()
                    except Exception as e:
                        logging.warning(f"Error stopping Playwright: {str(e)}")
            
            # Handle Selenium WebDriver
            elif hasattr(self.driver, 'quit'):
                logging.info("Closing Selenium WebDriver")
                try:
                    self.driver.quit()
                except Exception as e:
                    logging.warning(f"Error quitting WebDriver: {str(e)}")
                    
        except Exception as e:
            logging.warning(f"Error closing browser/WebDriver: {str(e)}")
            
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
