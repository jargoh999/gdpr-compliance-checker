import os
import sys
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.remote.remote_connection import LOGGER
import logging

# Set logger level to WARNING to reduce noise
LOGGER.setLevel(logging.WARNING)

def get_chrome_options():
    """Configure Chrome options for both local and cloud environments."""
    chrome_options = Options()
    
    # Common options
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--disable-extensions')
    chrome_options.add_argument('--disable-software-rasterizer')
    chrome_options.add_argument('--disable-setuid-sandbox')
    chrome_options.add_argument('--disable-notifications')
    chrome_options.add_argument('--disable-infobars')
    chrome_options.add_argument('--disable-web-security')
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    
    # Headless mode for server environments
    if os.environ.get('STREAMLIT_SERVER_RUNNING', '').lower() == 'true':
        chrome_options.add_argument('--headless=new')
        chrome_options.add_argument('--window-size=1920,1080')
    
    # Additional options for Linux environments
    if sys.platform == 'linux':
        chrome_options.add_argument('--disable-dev-shm-using')
        chrome_options.add_argument('--disable-extensions')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--disable-application-cache')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-setuid-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
    
    return chrome_options

def get_webdriver():
    """Initialize and return a Chrome WebDriver instance."""
    try:
        # Try to use the installed Chrome driver first
        options = get_chrome_options()
        
        # In Streamlit Cloud or similar environments, use the installed Chrome
        if os.environ.get('STREAMLIT_SERVER_RUNNING', '').lower() == 'true':
            options.binary_location = '/usr/bin/google-chrome-stable'
            service = Service(executable_path='/usr/local/bin/chromedriver')
            return webdriver.Chrome(service=service, options=options)
        
        # For local development, use webdriver-manager
        return webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=options
        )
    except Exception as e:
        print(f"Error initializing WebDriver: {str(e)}")
        raise

def close_webdriver(driver):
    """Safely close the WebDriver instance."""
    if driver:
        try:
            driver.quit()
        except Exception as e:
            print(f"Error closing WebDriver: {str(e)}")
