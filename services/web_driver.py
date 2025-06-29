"""WebDriver service for Selenium browser automation"""
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import WebDriverException
from typing import Optional, Dict, Any

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
            options: Additional options to override defaults
            
        Returns:
            webdriver.Chrome: Configured Chrome WebDriver instance
        """
        if self.driver:
            self.quit_driver()
            
        chrome_options = self._get_chrome_options(options)
        
        try:
            # Use webdriver-manager to handle ChromeDriver
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            return self.driver
        except WebDriverException as e:
            raise RuntimeError(f"Failed to start WebDriver: {str(e)}")
    
    def _get_chrome_options(self, custom_options: Optional[Dict[str, Any]] = None) -> Options:
        """Get Chrome options with default and custom settings
        
        Args:
            custom_options: Custom options to override defaults
            
        Returns:
            Options: Configured Chrome options
        """
        options = Options()
        
        # Set default options
        for option, value in BROWSER_OPTIONS.items():
            options.add_argument(f"--{option}={value}")
        
        # Apply headless mode if specified
        if self.headless:
            options.add_argument('--headless')
        
        # Apply custom options
        if custom_options:
            for option, value in custom_options.items():
                if option.startswith('--'):
                    options.add_argument(f"{option}={value}")
                else:
                    options.add_argument(f"--{option}={value}")
        
        # Disable automation flags
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        # Disable password manager and infobars
        prefs = {
            'credentials_enable_service': False,
            'profile.password_manager_enabled': False,
            'profile.default_content_setting_values.notifications': 2
        }
        options.add_experimental_option('prefs', prefs)
        
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
                self.driver.quit()
            except Exception:
                pass  # Ignore errors when quitting
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
