"""Base class for all GDPR compliance checkers"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.common.exceptions import WebDriverException
import time

from models.gdpr_check import GDPRCheckResult, CheckStatus, GDPRSolution
from config.constants import DEFAULT_TIMEOUT

class BaseChecker(ABC):
    """Abstract base class for all GDPR compliance checkers"""
    
    def __init__(self, driver: WebDriver):
        """Initialize the checker with a Selenium WebDriver instance
        
        Args:
            driver: Selenium WebDriver instance
        """
        self.driver = driver
        self.timeout = DEFAULT_TIMEOUT
    
    @property
    @abstractmethod
    def check_id(self) -> str:
        """Unique identifier for this check (e.g., 'gdpr_banner_exists')"""
        pass
    
    @property
    @abstractmethod
    def check_name(self) -> str:
        """Human-readable name for this check"""
        pass
    
    @property
    def severity(self) -> str:
        """Severity level if check fails (high, medium, low, info)"""
        return "high"
    
    @property
    def requires_page_reload(self) -> bool:
        """Whether this check requires a fresh page load"""
        return False
    
    def execute(self, url: str) -> GDPRCheckResult:
        """Execute the check and return the result
        
        Args:
            url: URL to check
            
        Returns:
            GDPRCheckResult: Result of the check
        """
        start_time = time.time()
        
        try:
            if self.requires_page_reload:
                self.driver.get(url)
                time.sleep(2)  # Allow page to load
            
            result = self._execute_check(url)
            
        except WebDriverException as e:
            return GDPRCheckResult(
                check_id=self.check_id,
                check_name=self.check_name,
                status=CheckStatus.ERROR,
                severity="high",
                description=f"Error executing check: {str(e)}",
                details={"error": str(e)}
            )
        except Exception as e:
            return GDPRCheckResult(
                check_id=self.check_id,
                check_name=self.check_name,
                status=CheckStatus.ERROR,
                severity="high",
                description=f"Unexpected error during check: {str(e)}",
                details={"error": str(e)}
            )
        finally:
            # Record execution time
            execution_time = time.time() - start_time
            if hasattr(self, 'result'):
                self.result.details['execution_time_seconds'] = round(execution_time, 2)
        
        return result
    
    @abstractmethod
    def _execute_check(self, url: str) -> GDPRCheckResult:
        """Implementation of the actual check logic
        
        Args:
            url: URL to check
            
        Returns:
            GDPRCheckResult: Result of the check
        """
        pass
    
    def _find_element(self, by: str, value: str, parent: Optional[WebElement] = None) -> Optional[WebElement]:
        """Safely find a single web element
        
        Args:
            by: Locator strategy (e.g., 'id', 'xpath', 'css_selector')
            value: Locator value
            parent: Optional parent element to search within
            
        Returns:
            WebElement if found, None otherwise
        """
        try:
            if parent:
                return parent.find_element(by, value)
            return self.driver.find_element(by, value)
        except:
            return None
    
    def _find_elements(self, by: str, value: str, parent: Optional[WebElement] = None) -> List[WebElement]:
        """Safely find multiple web elements
        
        Args:
            by: Locator strategy (e.g., 'id', 'xpath', 'css_selector')
            value: Locator value
            parent: Optional parent element to search within
            
        Returns:
            List of WebElements (may be empty)
        """
        try:
            if parent:
                return parent.find_elements(by, value)
            return self.driver.find_elements(by, value)
        except:
            return []
    
    def _element_exists(self, by: str, value: str, parent: Optional[WebElement] = None) -> bool:
        """Check if an element exists on the page
        
        Args:
            by: Locator strategy
            value: Locator value
            parent: Optional parent element to search within
            
        Returns:
            bool: True if element exists, False otherwise
        """
        return self._find_element(by, value, parent) is not None
    
    def _element_contains_text(self, by: str, value: str, text: str, case_sensitive: bool = False) -> bool:
        """Check if an element contains specific text
        
        Args:
            by: Locator strategy
            value: Locator value
            text: Text to search for
            case_sensitive: Whether the search should be case sensitive
            
        Returns:
            bool: True if element contains the text, False otherwise
        """
        element = self._find_element(by, value)
        if not element:
            return False
            
        element_text = element.text
        if not case_sensitive:
            element_text = element_text.lower()
            text = text.lower()
            
        return text in element_text
    
    def _create_solution(
        self, 
        description: str, 
        code_snippet: str = "", 
        language: str = "javascript",
        complexity: str = "medium"
    ) -> GDPRSolution:
        """Helper method to create a solution object
        
        Args:
            description: Description of the solution
            code_snippet: Optional code snippet implementing the solution
            language: Programming language of the code snippet
            complexity: Complexity level (low, medium, high)
            
        Returns:
            GDPRSolution: Configured solution object
        """
        return GDPRSolution(
            description=description,
            code_snippet=code_snippet,
            language=language,
            complexity=complexity
        )
    
    def _create_result(
        self,
        status: CheckStatus,
        description: str,
        details: Optional[Dict[str, Any]] = None,
        solution: Optional[GDPRSolution] = None
    ) -> GDPRCheckResult:
        """Helper method to create a check result
        
        Args:
            status: Status of the check
            description: Description of the result
            details: Additional details about the result
            solution: Optional solution for any issues found
            
        Returns:
            GDPRCheckResult: Configured result object
        """
        return GDPRCheckResult(
            check_id=self.check_id,
            check_name=self.check_name,
            status=status,
            severity=self.severity,
            description=description,
            details=details or {},
            solution=solution
        )
