"""Streamlit Cloud entry point for GDPR Compliance Checker."""
import os
import sys
import subprocess
import logging
from pathlib import Path

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
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

# Set Chrome-specific environment variables
os.environ['CHROME_BIN'] = '/usr/bin/google-chrome'
os.environ['CHROME_PATH'] = '/usr/bin/google-chrome'

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
    except Exception as e:
        logger.warning(f"Failed to start Xvfb: {e}")

# Import the main app after setting up the environment
try:
    from app import main
except ImportError as e:
    logger.error(f"Failed to import app: {e}")
    raise

# Run the main function
if __name__ == "__main__":
    try:
        logger.info("Starting GDPR Compliance Checker...")
        main()
    except Exception as e:
        logger.exception("An error occurred in the main application:")
        # Re-raise the exception to ensure Streamlit shows the error
        raise
