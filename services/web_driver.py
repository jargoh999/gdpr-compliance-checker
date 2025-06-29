"""WebDriver service for Selenium browser automation"""
import os
import sys
from typing import Optional, Dict, Any
from selenium import webdriver
from selenium.common.exceptions import WebDriverException

# Import our utility functions
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.web_driver_utils import get_webdriver, close_webdriver, get_chrome_options

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
    
    def start_driver(self, options: Optional[Dict[str, Any]] = None) -> webdriver.Chrome:
        """Start a new Chrome WebDriver instance
        
        Args:
            options: Additional options to override defaults (not used in this implementation)
            
        Returns:
            webdriver.Chrome: Configured Chrome WebDriver instance
        """
        if self.driver:
            self.quit_driver()
        
        try:
            # Use our utility function to get a properly configured WebDriver
            self.driver = get_webdriver()
            return self.driver
        except Exception as e:
            raise RuntimeError(f"Failed to start WebDriver: {str(e)}")
    
    def _get_chrome_options(self, custom_options: Optional[Dict[str, Any]] = None):
        """Get Chrome options with default and custom settings
        
        Args:
            custom_options: Custom options to override defaults
            
        Returns:
            Options: Configured Chrome options
        """
        # Use our utility function to get base options
        options = get_chrome_options()
        
        # Set Chrome preferences
        prefs = {
            'profile.password_manager_enabled': False,
            'profile.default_content_setting_values.notifications': 2
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
