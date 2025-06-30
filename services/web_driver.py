"""WebDriver service for Selenium browser automation"""
import os
import sys
import time
import logging
from typing import Optional, Dict, Any, Union, List, Tuple
from selenium import webdriver
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    WebDriverException, TimeoutException, NoSuchElementException
)

# Import our utility functions
from browser_utils import get_chrome_driver, ensure_browser_setup

# Set up logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Add a console handler if not already present
if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    logger.addHandler(handler)

# Default browser options
BROWSER_OPTIONS = {
    'headless': True,
    'no-sandbox': True,
    'disable-dev-shm-usage': True,
    'disable-gpu': True,
    'disable-extensions': True,
    'disable-infobars': True,
    'disable-notifications': True,
    'disable-browser-side-navigation': True,
    'disable-features': 'VizDisplayCompositor',
    'disable-setuid-sandbox': True,
    'disable-web-security': True,
    'ignore-certificate-errors': True,
    'remote-debugging-port': '9222',
}

class WebDriverService:
    """Service for managing Selenium WebDriver instances"""
    
    def __init__(self, headless: bool = True):
        """Initialize the WebDriver service
        
        Args:
            headless: Whether to run browser in headless mode
        """
        self.headless = headless
        self.driver: Optional[webdriver.Chrome] = None
    
    def _get_chrome_version(self) -> Optional[str]:
        """Get the installed Chrome version.
        
        Returns:
            Optional[str]: Chrome version string or None if not found
        """
        try:
            # Try to get Chrome version using subprocess
            import subprocess
            result = subprocess.run(
                [os.environ.get('CHROME_BIN', 'google-chrome'), '--version'],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                version = result.stdout.strip().split()[-1]
                logger.info(f"Found Chrome version: {version}")
                return version
        except Exception as e:
            logger.warning(f"Could not determine Chrome version: {e}")
        
        return None

    def _get_webdriver_options(self, options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Get WebDriver options with proper configuration.
        
        Args:
            options: Additional options to override defaults
            
        Returns:
            Dict: Configured WebDriver options
        """
        # Start with default options
        driver_options = BROWSER_OPTIONS.copy()
        
        # Apply user-provided options
        if options:
            if isinstance(options, dict):
                driver_options.update(options)
            elif isinstance(options, list):
                # Convert list of arguments to dict
                for opt in options:
                    if opt.startswith('--'):
                        parts = opt[2:].split('=', 1)
                        if len(parts) == 1:
                            driver_options[parts[0]] = True
                        else:
                            driver_options[parts[0]] = parts[1]
        
        # Ensure required options are set
        if 'headless' not in driver_options:
            driver_options['headless'] = self.headless
            
        return driver_options

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
                time.sleep(1)  # Small delay to ensure clean shutdown
            except Exception as e:
                logger.warning(f"Error quitting existing driver: {e}")
        
        # Ensure browser setup is complete
        if not ensure_browser_setup():
            logger.warning("Browser setup check failed, attempting to continue anyway...")
        
        # Get Chrome version for logging
        chrome_version = self._get_chrome_version()
        if chrome_version:
            logger.info(f"Using Chrome version: {chrome_version}")
        else:
            logger.warning("Could not determine Chrome version")
        
        # Get configured options
        driver_options = self._get_webdriver_options(options)
        logger.info(f"Starting WebDriver with options: {driver_options}")
        
        # Attempt to start Chrome WebDriver with retries
        max_retries = 3
        for attempt in range(max_retries):
            try:
                # Use our utility function to get a Chrome WebDriver
                self.driver = get_chrome_driver(headless=driver_options.get('headless', True))
                
                if self.driver:
                    # Set a default window size
                    self.driver.set_window_size(1920, 1080)
                    logger.info("Successfully started WebDriver")
                    return self.driver
                
            except Exception as e:
                last_error = e
                logger.warning(f"WebDriver attempt {attempt + 1}/{max_retries} failed: {e}")
                
                # Clean up any partially started driver
                if self.driver:
                    try:
                        self.driver.quit()
                    except:
                        pass
                    self.driver = None
                
                # Add a small delay before retry
                if attempt < max_retries - 1:
                    wait_time = (attempt + 1) * 2  # Exponential backoff
                    logger.info(f"Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                continue
        
        # If we get here, all attempts failed
        error_msg = "Failed to start WebDriver after multiple attempts. "
        if last_error:
            error_msg += f"Last error: {type(last_error).__name__}: {str(last_error)}"
        
        logger.error(error_msg)
        raise RuntimeError(error_msg)
    
    def _try_start_webdriver(self, options: Optional[Dict[str, Any]], headless: bool = True) -> dict:
        """Attempt to start a WebDriver instance with the given options."""
        try:
            # Get Chrome options with the specified settings
            chrome_options = self._get_chrome_options(options)
            
            # Set headless mode if requested
            if headless and '--headless' not in str(chrome_options.arguments):
                chrome_options.add_argument('--headless=new')
            
            # Try to get a WebDriver instance with Chrome first, then fall back to Chromium
            chrome_types = [ChromeType.GOOGLE, ChromeType.CHROMIUM]
            last_error = None
            
            for chrome_type in chrome_types:
                try:
                    # Try to install the appropriate ChromeDriver
                    chrome_driver_path = ChromeDriverManager(chrome_type=chrome_type).install()
                    
                    # Create the WebDriver
                    self.driver = webdriver.Chrome(
                        service=Service(chrome_driver_path),
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
                        'browser': 'chrome' if chrome_type == ChromeType.GOOGLE else 'chromium'
                    }
                    
                except Exception as e:
                    last_error = str(e)
                    logging.warning(f"Failed to start {chrome_type} WebDriver: {last_error}")
                    
                    # Clean up if driver was partially created
                    if hasattr(self, 'driver') and self.driver:
                        try:
                            self.driver.quit()
                        except:
                            pass
                        self.driver = None
            
            # If we get here, all Chrome/Chromium attempts failed
            raise RuntimeError(f"Failed to start any Chrome/Chromium WebDriver. Last error: {last_error}")
            
            return {
                'success': False,
                'error': last_error or 'Unknown error',
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
            import sys
            import subprocess
            
            # Ensure Playwright is installed
            try:
                from playwright.sync_api import sync_playwright
            except ImportError:
                logging.info("Playwright not found, installing...")
                subprocess.check_call([sys.executable, "-m", "pip", "install", "playwright"])
                subprocess.check_call([sys.executable, "-m", "playwright", "install-deps"])
                subprocess.check_call([sys.executable, "-m", "playwright", "install", "chromium"])
                from playwright.sync_api import sync_playwright
            
            # Try to start Playwright with Chromium
            playwright = sync_playwright().start()
            
            # Try with Chromium first, fall back to WebKit if needed
            browsers_to_try = ['chromium', 'webkit']
            last_error = None
            
            for browser_type_name in browsers_to_try:
                try:
                    browser_type = getattr(playwright, browser_type_name)
                    browser = browser_type.launch(headless=True)
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
                        'browser': browser_type_name,
                        'headless': True
                    }
                    
                except Exception as e:
                    last_error = str(e)
                    logging.warning(f"Failed to start Playwright with {browser_type_name}: {last_error}")
                    
                    # Clean up if browser was partially created
                    if 'browser' in locals() and browser:
                        try:
                            browser.close()
                        except:
                            pass
            
            # If we get here, all Playwright attempts failed
            raise RuntimeError(f"Failed to start any Playwright browser. Last error: {last_error}")
            
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
            
            # Common options for better compatibility
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
                '--remote-debugging-port=9222',
                '--remote-debugging-address=0.0.0.0',
                '--disable-browser-side-navigation',
                '--disable-features=IsolateOrigins,site-per-process',
                '--disable-site-isolation-trials',
                '--disable-features=BlockInsecurePrivateNetworkRequests',
                '--disable-web-security',
                '--allow-running-insecure-content',
                '--disable-client-side-phishing-detection',
                '--disable-component-update',
                '--disable-default-apps',
                '--disable-hang-monitor',
                '--no-default-browser-check',
                '--no-first-run',
                '--window-size=1920,1080',
                '--start-maximized',
                '--ignore-certificate-errors',
                '--ignore-ssl-errors',
                '--disable-translate',
                '--disable-background-networking',
                '--disable-sync',
                '--metrics-recording-only',
                '--mute-audio',
                '--no-zygote',
                '--single-process',
                '--disable-breakpad',
                '--disable-client-side-phishing-detection',
                '--disable-component-extensions-with-background-pages',
                '--disable-default-apps',
                '--disable-dev-shm-usage',
                '--disable-extensions',
                '--disable-features=TranslateUI',
                '--disable-hang-monitor',
                '--disable-ipc-flooding-protection',
                '--disable-popup-blocking',
                '--disable-prompt-on-repost',
                '--disable-renderer-backgrounding',
                '--disable-sync',
                '--force-color-profile=srgb',
                '--metrics-recording-only',
                '--safebrowsing-disable-auto-update',
                '--password-store=basic',
                '--use-mock-keychain',
                '--disable-background-timer-throttling',
                '--disable-backgrounding-occluded-windows',
                '--disable-component-update',
                '--disable-ipc-flooding-protection',
                '--disable-renderer-backgrounding'
            ]
            
            # Add all common arguments
            for arg in chrome_args:
                if arg not in ' '.join(options.arguments):
                    options.add_argument(arg)
            
            # Set headless mode for server environments or if explicitly requested
            if (os.environ.get('STREAMLIT_SERVER_RUNNING', '').lower() == 'true' or 
                os.environ.get('HEADLESS', 'true').lower() == 'true'):
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
            if hasattr(self.driver, 'close') and hasattr(self.driver, 'contexts'):
                # Try to get the browser type for logging
                browser_type = getattr(self.driver, '_browser_type', 'unknown')
                logger.info(f"Closing Playwright browser ({browser_type})")
                
                # Close all contexts
                for context in self.driver.contexts:
                    try:
                        context.close()
                    except Exception as e:
                        logger.warning(f"Error closing context: {e}")
                
                # Close the browser
                try:
                    self.driver.close()
                except Exception as e:
                    logger.warning(f"Error closing browser: {e}")
                    
                # Stop Playwright if we can access it
                if hasattr(self.driver, '_playwright') and self.driver._playwright:
                    try:
                        self.driver._playwright.stop()
                    except Exception as e:
                        logger.warning(f"Error stopping Playwright: {e}")
                        
            else:  # Regular Selenium WebDriver
                # Close all windows
                try:
                    for handle in self.driver.window_handles:
                        try:
                            self.driver.switch_to.window(handle)
                            self.driver.close()
                            time.sleep(0.5)  # Small delay between window closes
                        except Exception as e:
                            logger.warning(f"Error closing window {handle}: {e}")
                except Exception as e:
                    logger.warning(f"Error closing windows: {e}")
                
                # Quit the driver
                try:
                    self.driver.quit()
                    logger.info("Successfully quit WebDriver")
                except Exception as e:
                    logger.error(f"Error quitting WebDriver: {e}")
                    
        except Exception as e:
            logger.error(f"Error during WebDriver cleanup: {e}")
            # Try a more forceful cleanup if normal quit fails
            try:
                import psutil
                    
                # Get the process ID if this is a Selenium WebDriver
                if hasattr(self.driver, 'service') and self.driver.service:
                    pid = self.driver.service.process.pid if hasattr(self.driver.service, 'process') else None
                    
                    # Try to terminate the process
                    if pid:
                        try:
                            process = psutil.Process(pid)
                            process.terminate()
                            logger.info(f"Terminated WebDriver process {pid}")
                        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess) as e:
                            logger.warning(f"Could not terminate process {pid}: {e}")
            except Exception as e:
                logger.error(f"Error during process cleanup: {e}")
                
        finally:
            # Additional cleanup
            try:
                # Clear any remaining WebDriver processes
                self._cleanup_driver_processes()
            except Exception as e:
                logger.warning(f"Error during additional cleanup: {e}")
                
            # Ensure driver reference is cleared
            self.driver = None
    
def _cleanup_driver_processes(self):
    """Clean up any remaining WebDriver processes."""
    try:
        import psutil
            
        # List of common WebDriver process names
        driver_processes = ['chromedriver', 'geckodriver', 'msedgedriver', 'safaridriver']
            
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                # Check if process name matches any known WebDriver
                if any(driver in proc.info['name'].lower() for driver in driver_processes):
                    logger.info(f"Terminating orphaned WebDriver process: {proc.info}")
                    proc.terminate()
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue
    except Exception as e:
        logger.warning(f"Error cleaning up WebDriver processes: {e}")
        
def __enter__(self):
    """Context manager entry"""
    return self.get_driver()
    
def __exit__(self, exc_type, exc_val, exc_tb):
    """Context manager exit"""
    self.quit_driver()

# Singleton instance
web_driver_service = WebDriverService()
