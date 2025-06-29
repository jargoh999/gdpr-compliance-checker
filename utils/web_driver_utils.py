import os
import sys
import logging
from typing import Optional, Union, Any
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.remote.webdriver import WebDriver
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.core.utils import ChromeType
from selenium.webdriver.remote.remote_connection import LOGGER
import subprocess

# Set logger level to WARNING to reduce noise
LOGGER.setLevel(logging.WARNING)

# Set logger level to WARNING to reduce noise
LOGGER.setLevel(logging.WARNING)

def is_chrome_installed() -> bool:
    """Check if Chrome or Chromium is installed."""
    try:
        # Try to get Chrome version
        chrome_version = subprocess.check_output(
            ["google-chrome", "--version"],
            stderr=subprocess.STDOUT
        )
        logging.info(f"Chrome is installed: {chrome_version.decode().strip()}")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        try:
            # Try chromium as fallback
            chromium_version = subprocess.check_output(
                ["chromium-browser", "--version"],
                stderr=subprocess.STDOUT
            )
            logging.info(f"Chromium is installed: {chromium_version.decode().strip()}")
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            logging.warning("Neither Chrome nor Chromium is installed")
            return False

def get_chrome_options() -> Options:
    """Configure Chrome/Chromium options for both local and cloud environments."""
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

def get_webdriver() -> WebDriver:
    """Initialize and return a Chrome/Chromium WebDriver instance.
    
    Returns:
        WebDriver: Configured WebDriver instance
    """
    options = get_chrome_options()
    
    # Set headless mode for server environments
    if os.environ.get('STREAMLIT_SERVER_RUNNING', '').lower() == 'true':
        options.add_argument('--headless=new')
        options.add_argument('--window-size=1920,1080')
    
    try:
        # Try to use the installed Chrome/Chromium driver
        if is_chrome_installed():
            chrome_type = ChromeType.GOOGLE
        else:
            # Fall back to Chromium if Chrome is not installed
            chrome_type = ChromeType.CHROMIUM
            logging.info("Chrome not found, falling back to Chromium")
            
        service = Service(ChromeDriverManager(chrome_type=chrome_type).install())
        driver = webdriver.Chrome(service=service, options=options)
        
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
