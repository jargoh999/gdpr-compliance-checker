"""Streamlit Cloud entry point for GDPR Compliance Checker."""
import os
import sys
import subprocess
import logging
import time
from pathlib import Path

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('app.log')
    ]
)
logger = logging.getLogger(__name__)

# Add project root to path
project_root = str(Path(__file__).parent.absolute())
if project_root not in sys.path:
    sys.path.append(project_root)

# Set environment variables for headless browser
os.environ['DISPLAY'] = ':99'
os.environ['PYTHONUNBUFFERED'] = '1'
os.environ['PYTHONIOENCODING'] = 'utf-8'
os.environ['PLAYWRIGHT_BROWSERS_PATH'] = os.path.expanduser('~/.cache/ms-playwright')

# Set Chrome-specific environment variables
os.environ['CHROME_BIN'] = '/usr/bin/google-chrome'
os.environ['CHROME_PATH'] = '/usr/bin/google-chrome'

# Configure Selenium to use system Chrome
os.environ['WDM_LOG_LEVEL'] = '0'  # Suppress WebDriver Manager logs
os.environ['WDM_PRINT_FIRST_LINE'] = 'False'

# Start Xvfb in the background
if os.name == 'posix':
    try:
        # Check if Xvfb is already running
        xvfb_proc = subprocess.Popen(
            ['Xvfb', ':99', '-screen', '0', '1920x1080x16'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        logger.info("Started Xvfb process")
        # Give Xvfb time to start
        time.sleep(2)
    except Exception as e:
        logger.warning(f"Failed to start Xvfb: {e}")

# Configure Playwright to use system browsers
try:
    os.makedirs(os.environ['PLAYWRIGHT_BROWSERS_PATH'], exist_ok=True)
    os.chmod(os.environ['PLAYWRIGHT_BROWSERS_PATH'], 0o777)
    logger.info(f"Set up Playwright browsers path: {os.environ['PLAYWRIGHT_BROWSERS_PATH']}")
except Exception as e:
    logger.warning(f"Failed to set up Playwright browsers path: {e}")

# Import the main app after setting up the environment
try:
    logger.info("Importing main application...")
    from app import main
except ImportError as e:
    logger.error(f"Failed to import app: {e}")
    raise

# Run the main function
if __name__ == "__main__":
    try:
        logger.info("=== Starting GDPR Compliance Checker ===")
        logger.info(f"Python version: {sys.version}")
        logger.info(f"Current working directory: {os.getcwd()}")
        logger.info(f"Environment variables: {os.environ}")
        
        # Test browser availability
        try:
            from selenium import webdriver
            from selenium.webdriver.chrome.options import Options
            options = Options()
            options.add_argument('--headless')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.binary_location = os.environ.get('CHROME_BIN', '/usr/bin/google-chrome')
            
            driver = webdriver.Chrome(options=options)
            driver.get('https://www.google.com')
            logger.info(f"Successfully loaded page: {driver.title}")
            driver.quit()
        except Exception as e:
            logger.warning(f"Selenium test failed: {e}")
        
        main()
    except Exception as e:
        logger.exception("An error occurred in the main application:")
        # Re-raise the exception to ensure Streamlit shows the error
        raise
