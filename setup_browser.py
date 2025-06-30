"""Setup script for browser automation dependencies.

This script ensures all necessary dependencies for browser automation are installed,
including system packages, Chrome/Chromium, and browser drivers.
"""
import os
import sys
import logging
import subprocess
import platform
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('browser_setup.log')
    ]
)
logger = logging.getLogger(__name__)

def run_command(command: str, cwd: str = None) -> bool:
    """Run a shell command and return True if successful."""
    logger.info(f"Running command: {command}")
    try:
        result = subprocess.run(
            command,
            shell=True,
            cwd=cwd,
            check=True,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        logger.debug(f"Command output: {result.stdout}")
        if result.stderr:
            logger.debug(f"Command error: {result.stderr}")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Command failed with error: {e}")
        if e.stdout:
            logger.error(f"Command output: {e.stdout}")
        if e.stderr:
            logger.error(f"Command error: {e.stderr}")
        return False

def install_system_packages() -> bool:
    """Install required system packages for browser automation."""
    system = platform.system().lower()
    
    if system == 'linux':
        # Install Chrome/Chromium and dependencies
        commands = [
            'apt-get update',
            'apt-get install -y wget gnupg2',
            'wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add -',
            'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list',
            'apt-get update',
            'apt-get install -y google-chrome-stable xvfb x11-utils',
            'apt-get install -y libgbm-dev libxshmfence-dev libnss3-dev libatk1.0-0 libatk-bridge2.0-0 libdrm2 libxkbcommon0 libxcomposite1 libxdamage1 libxfixes3 libxrandr2 libgbm1 libasound2 libatspi2.0-0',
            'rm -rf /var/lib/apt/lists/*',
        ]
    elif system == 'darwin':  # macOS
        commands = [
            'brew update',
            'brew install --cask google-chrome',
            'brew install libxshmfence',
        ]
    elif system == 'windows':
        # On Windows, we'll use the webdriver-manager to handle ChromeDriver
        commands = []
    else:
        logger.warning(f"Unsupported operating system: {system}")
        return False
    
    success = True
    for cmd in commands:
        if not run_command(cmd):
            success = False
            logger.warning(f"Failed to run command: {cmd}")
    
    return success

def install_python_packages() -> bool:
    """Install required Python packages."""
    packages = [
        'selenium>=4.10.0',
        'webdriver-manager>=4.0.0',
        'playwright>=1.35.0',
        'selenium-wire>=5.1.0',
        'pyvirtualdisplay>=3.0.0',
        'xvfbwrapper>=0.2.9',
        'psutil>=5.9.5',
    ]
    
    success = True
    for package in packages:
        cmd = f"{sys.executable} -m pip install --upgrade {package}"
        if not run_command(cmd):
            success = False
            logger.warning(f"Failed to install package: {package}")
    
    return success

def install_playwright_browsers() -> bool:
    """Install Playwright browsers."""
    try:
        import playwright
        from playwright.__main__ import main as playwright_install
        
        logger.info("Installing Playwright browsers...")
        playwright_install(['install'])
        playwright_install(['install-deps'])
        
        # Verify installation
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            for browser_type in [p.chromium, p.firefox, p.webkit]:
                try:
                    browser = browser_type.launch(headless=True)
                    browser.close()
                    logger.info(f"Successfully verified {browser_type.name} installation")
                except Exception as e:
                    logger.error(f"Failed to verify {browser_type.name} installation: {e}")
                    return False
        
        return True
        
    except Exception as e:
        logger.error(f"Failed to install Playwright browsers: {e}")
        return False

def setup_environment() -> bool:
    """Set up environment variables for browser automation."""
    try:
        # Set up Playwright browsers path
        playwright_browsers_path = os.path.expanduser('~/.cache/ms-playwright')
        os.makedirs(playwright_browsers_path, exist_ok=True)
        os.environ['PLAYWRIGHT_BROWSERS_PATH'] = playwright_browsers_path
        
        # Set Chrome/Chromium paths
        system = platform.system().lower()
        if system == 'linux':
            chrome_paths = [
                '/usr/bin/google-chrome',
                '/usr/bin/chromium-browser',
                '/usr/bin/chromium',
            ]
        elif system == 'darwin':  # macOS
            chrome_paths = [
                '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
                '/Applications/Chromium.app/Contents/MacOS/Chromium',
            ]
        elif system == 'windows':
            chrome_paths = [
                'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe',
                'C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe',
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
        
        return True
        
    except Exception as e:
        logger.error(f"Failed to set up environment: {e}")
        return False

def main():
    """Main setup function."""
    logger.info("Starting browser setup...")
    
    # Create a .gitignore file if it doesn't exist
    gitignore_path = Path('.gitignore')
    if not gitignore_path.exists():
        with open(gitignore_path, 'w') as f:
            f.write("# Browser automation\n")
            f.write("browser_setup.log\n")
            f.write("playwright/.local-browsers/\n")
            f.write(".pytest_cache/\n")
            f.write("__pycache__/\n")
    
    # Install system packages
    logger.info("Installing system packages...")
    if not install_system_packages():
        logger.warning("Failed to install some system packages. Continuing anyway...")
    
    # Install Python packages
    logger.info("Installing Python packages...")
    if not install_python_packages():
        logger.error("Failed to install required Python packages.")
        return False
    
    # Install Playwright browsers
    logger.info("Installing Playwright browsers...")
    if not install_playwright_browsers():
        logger.warning("Failed to install some Playwright browsers. Some features may not work.")
    
    # Set up environment
    logger.info("Setting up environment...")
    if not setup_environment():
        logger.warning("Failed to set up some environment variables. Some features may not work.")
    
    logger.info("Browser setup completed successfully!")
    return True

if __name__ == "__main__":
    if main():
        sys.exit(0)
    else:
        sys.exit(1)
