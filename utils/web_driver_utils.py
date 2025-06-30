"""WebDriver utility functions for browser automation."""
import os
import sys
import logging
import platform
import subprocess
from typing import Optional, Dict, Any, Union

# Selenium imports
from selenium import webdriver
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.core.os_manager import ChromeType

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('webdriver.log')
    ]
)

LOGGER = logging.getLogger(__name__)

# Set logger level to WARNING to reduce noise
LOGGER.setLevel(logging.WARNING)

def is_chrome_installed() -> bool:
    """Check if Chrome or Chromium is installed on the system.
    
    Returns:
        bool: True if Chrome or Chromium is installed, False otherwise
    """
    # Determine the correct command based on the platform
    commands = []
    if platform.system() == 'Windows':
        commands = [
            ['reg', 'query', 'HKEY_CURRENT_USER\\Software\\Google\\Chrome\\BLBeacon', '/v', 'version'],
            ['reg', 'query', 'HKEY_LOCAL_MACHINE\\SOFTWARE\\Wow6432Node\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\Google Chrome', '/v', 'DisplayVersion']
        ]
    else:
        commands = [
            ['google-chrome', '--version'],
            ['chromium-browser', '--version'],
            ['chromium', '--version'],
            ['/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome', '--version']
        ]
    
    for cmd in commands:
        try:
            result = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=True,
                shell=platform.system() == 'Windows'
            )
            version = result.stdout.strip()
            if version:
                LOGGER.info(f"Found browser: {version}")
                return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            continue
    
    LOGGER.warning("No Chrome/Chromium installation found")
    return False

def get_chrome_options(headless: bool = None) -> Options:
    """Get Chrome/Chromium options with common settings.
    
    Args:
        headless: Whether to run in headless mode. If None, auto-detect based on environment.
    
    Returns:
        Options: Configured Chrome options
    """
    options = Options()
    
    # Common Chrome options
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
        '--disable-blink-features=AutomationControlled',
        '--disable-browser-side-navigation',
        '--disable-features=IsolateOrigins,site-per-process',
        '--disable-web-security',
        '--disable-features=site-per-process',
        '--disable-features=VizDisplayCompositor',
        '--disable-background-networking',
        '--disable-default-apps',
        '--disable-hang-monitor',
        '--disable-prompt-on-repost',
        '--disable-sync',
        '--metrics-recording-only',
        '--no-first-run',
        '--safebrowsing-disable-auto-update',
        '--disable-client-side-phishing-detection',
        '--disable-component-update',
        '--disable-default-apps',
        '--use-fake-ui-for-media-stream',
        '--use-fake-device-for-media-stream',
        '--disable-webgl',
        '--disable-threaded-animation',
        '--disable-threaded-scrolling',
        '--disable-in-process-stack-traces',
        '--disable-logging',
        '--disable-dev-tools',
        '--log-level=3',
        '--output=/dev/null'
    ]
    
    # Add all common arguments
    for arg in chrome_args:
        options.add_argument(arg)
    
    # Set preferences
    prefs = {
        'profile.default_content_setting_values.notifications': 2,
        'credentials_enable_service': False,
        'profile.password_manager_enabled': False,
        'profile.default_content_settings.popups': 0,
        'download_restrictions': 3,
        'safebrowsing.enabled': True,
        'profile.managed_default_content_settings.images': 2,  # Disable images
        'profile.managed_default_content_settings.javascript': 1,  # Enable JS
        'profile.managed_default_content_settings.cookies': 1,  # Enable cookies
        'profile.managed_default_content_settings.plugins': 1,  # Enable plugins
        'profile.managed_default_content_settings.popups': 0,  # Disable popups
        'profile.managed_default_content_settings.geolocation': 0,  # Disable geolocation
        'profile.managed_default_content_settings.media_stream': 0,  # Disable media stream
    }
    
    options.add_experimental_option('prefs', prefs)
    
    # Set headless mode if specified or in server environment
    if headless or (headless is None and os.environ.get('STREAMLIT_SERVER_RUNNING', '').lower() == 'true'):
        options.add_argument('--headless=new')
        options.add_argument('--window-size=1920,1080')
    
    # Set binary location if available
    if platform.system() == 'Linux':
        chrome_paths = [
            '/usr/bin/google-chrome',
            '/usr/bin/chromium-browser',
            '/usr/bin/chromium',
            '/usr/local/bin/chrome',
            '/snap/bin/chromium'
        ]
        for path in chrome_paths:
            if os.path.exists(path):
                options.binary_location = path
                break
    
    return options

def get_webdriver(headless: bool = None, options: Optional[Options] = None) -> WebDriver:
    """Initialize and return a Chrome/Chromium WebDriver instance with fallbacks.
    
    Args:
        headless: Whether to run in headless mode. If None, auto-detect.
        options: Optional pre-configured Chrome options.
    
    Returns:
        WebDriver: Configured WebDriver instance
        
    Raises:
        RuntimeError: If WebDriver cannot be initialized
    """
    if options is None:
        options = get_chrome_options(headless)
    
    # Configure service
    service_kwargs = {}
    
    # Try different Chrome/Chromium types
    chrome_types = [ChromeType.GOOGLE, ChromeType.CHROMIUM]
    
    for chrome_type in chrome_types:
        try:
            LOGGER.info(f"Attempting to initialize WebDriver with {chrome_type.name}")
            
            # Get the appropriate ChromeDriver
            chrome_driver_manager = ChromeDriverManager(chrome_type=chrome_type)
            service = Service(chrome_driver_manager.install())
            
            # Set binary location if not set
            if not options.binary_location:
                if chrome_type == ChromeType.GOOGLE:
                    if platform.system() == 'Linux':
                        options.binary_location = '/usr/bin/google-chrome-stable'\
                            if os.path.exists('/usr/bin/google-chrome-stable') else '/usr/bin/google-chrome'
                    elif platform.system() == 'Darwin':
                        options.binary_location = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
                elif chrome_type == ChromeType.CHROMIUM:
                    if platform.system() == 'Linux':
                        options.binary_location = '/usr/bin/chromium-browser'\
                            if os.path.exists('/usr/bin/chromium-browser') else '/usr/bin/chromium'
            
            LOGGER.info(f"Using Chrome binary: {options.binary_location or 'default'}")
            
            # Initialize WebDriver
            driver = webdriver.Chrome(service=service, options=options)
            
            # Set a reasonable window size if not headless
            if not (headless or (headless is None and os.environ.get('STREAMLIT_SERVER_RUNNING', '').lower() == 'true')):
                driver.set_window_size(1920, 1080)
            
            LOGGER.info("WebDriver initialized successfully")
            return driver
            
        except Exception as e:
            LOGGER.warning(f"Failed to initialize WebDriver with {chrome_type.name}: {str(e)}")
            continue
    
    # If we get here, all attempts failed
    error_msg = "Failed to initialize WebDriver with any Chrome/Chromium version"
    LOGGER.error(error_msg)
    raise RuntimeError(error_msg)

def close_webdriver(driver: WebDriver) -> None:
    """Safely close the WebDriver instance.
    
    Args:
        driver: WebDriver instance to close
    """
    if not driver:
        return
        
    try:
        # Try to close all windows and quit
        if hasattr(driver, 'window_handles'):
            for handle in driver.window_handles:
                try:
                    driver.switch_to.window(handle)
                    driver.close()
                except Exception as e:
                    LOGGER.warning(f"Error closing window {handle}: {str(e)}")
        
        # Try to quit the driver
        if hasattr(driver, 'quit'):
            driver.quit()
            
    except Exception as e:
        LOGGER.warning(f"Error closing WebDriver: {str(e)}")
        
    finally:
        try:
            # Try to kill any remaining Chrome/Chromium processes
            if platform.system() == 'Windows':
                os.system('taskkill /f /im chrome.exe /t >nul 2>&1')
                os.system('taskkill /f /im chromedriver.exe /t >nul 2>&1')
            else:
                os.system('pkill -f "(chrome|chromium|chromedriver)" >/dev/null 2>&1')
        except Exception as e:
            LOGGER.debug(f"Error cleaning up processes: {str(e)}")
