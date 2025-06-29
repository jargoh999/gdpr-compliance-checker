"""Data Collection Form Checker for GDPR Compliance"""
from typing import Dict, List, Optional
from bs4 import BeautifulSoup
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.common.by import By

from components.base_checker import BaseChecker
from models.gdpr_check import GDPRCheckResult, CheckStatus, GDPRSolution
from config.constants import SEVERITY_HIGH, SEVERITY_MEDIUM, SEVERITY_LOW

class DataCollectionFormChecker(BaseChecker):
    """Checks for GDPR compliance in data collection forms"""
    
    @property
    def check_id(self) -> str:
        return "data_collection_forms"
    
    @property
    def check_name(self) -> str:
        return "Data Collection Form Compliance"
    
    def _execute_check(self, url: str) -> GDPRCheckResult:
        """Check if data collection forms are GDPR compliant"""
        try:
            self.driver.get(url)
            forms = self.driver.find_elements(By.TAG_NAME, "form")
            
            if not forms:
                return self._create_result(
                    CheckStatus.PASSED,
                    "No data collection forms found on the page."
                )
            
            issues = []
            
            for i, form in enumerate(forms):
                form_issues = self._check_form_compliance(form, i+1)
                issues.extend(form_issues)
            
            if not issues:
                return self._create_result(
                    CheckStatus.PASSED,
                    "All data collection forms appear to be GDPR compliant."
                )
            
            return self._create_result(
                CheckStatus.FAILED,
                "Found potential GDPR compliance issues in data collection forms:",
                {"issues": issues},
                solution=self._create_solution(
                    "Address the following issues in your data collection forms:",
                    """1. Add privacy policy links to all forms
2. Ensure all required fields are clearly marked
3. Add explicit consent checkboxes where needed""",
                    language="markdown",
                    complexity="medium"
                )
            )
            
        except Exception as e:
            return self._create_result(
                CheckStatus.ERROR,
                f"Error checking data collection forms: {str(e)}",
                {"error": str(e)}
            )
    
    def _check_form_compliance(self, form, form_number: int) -> List[str]:
        """Check a single form for GDPR compliance issues"""
        issues = []
        
        # Check for privacy policy link
        privacy_links = form.find_elements(By.XPATH, 
            ".//a[contains(translate(., 'PRIVACYPOLICY', 'privacypolicy'), 'privacy') or "
            "contains(translate(@href, 'PRIVACYPOLICY', 'privacypolicy'), 'privacy')]"
        )
        
        if not privacy_links:
            issues.append(f"Form {form_number}: No privacy policy link found near the form")
        
        # Check for required fields
        required_fields = form.find_elements(By.CSS_SELECTOR, "[required]")
        
        # Check for consent checkboxes
        checkboxes = form.find_elements(By.CSS_SELECTOR, "input[type='checkbox']")
        consent_terms = ["consent", "agree", "accept", "gdpr"]
        has_consent = any(
            any(term in checkbox.get_attribute("id").lower() or 
                term in checkbox.get_attribute("name").lower() or
                term in checkbox.get_attribute("class").lower() or
                term in (checkbox.get_attribute("aria-label") or "").lower() or
                term in (checkbox.get_attribute("value") or "").lower()
                for term in consent_terms)
            for checkbox in checkboxes
        )
        
        if not has_consent and (required_fields or form.find_elements(By.CSS_SELECTOR, "input[type='email'], input[type='tel'], input[type='text']")):
            issues.append(f"Form {form_number}: No explicit consent checkbox found for data processing")
        
        # Check for secure submission
        form_action = form.get_attribute("action") or ""
        if form_action.startswith("http://") and not form_action.startswith("https://"):
            issues.append(f"Form {form_number}: Form is submitted over HTTP instead of HTTPS")
        
        # Check for sensitive data collection
        sensitive_fields = form.find_elements(By.CSS_SELECTOR, 
            "input[type='password'], input[type='credit-card'], input[type='cc-number']"
        )
        
        if sensitive_fields and not form_action.startswith("https://"):
            issues.append(f"Form {form_number}: Sensitive data collection detected without HTTPS")
        
        return issues
