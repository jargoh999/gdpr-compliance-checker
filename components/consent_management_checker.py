"""Consent Management Platform (CMP) Checker for GDPR Compliance"""
from typing import Dict, List, Optional, Set, Tuple, Any
import re
import json
from urllib.parse import urlparse, urljoin

from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from components.base_checker import BaseChecker
from models.gdpr_check import GDPRCheckResult, CheckStatus, GDPRSolution
from config.constants import SEVERITY_HIGH, SEVERITY_MEDIUM, SEVERITY_LOW

class ConsentManagementChecker(BaseChecker):
    """Checks for GDPR compliance in consent management and cookie banners"""
    
    @property
    def check_id(self) -> str:
        return "consent_management"
    
    @property
    def check_name(self) -> str:
        return "Consent Management"
    
    def _execute_check(self, url: str) -> GDPRCheckResult:
        """Check for consent management compliance"""
        try:
            banner_issues = self._check_cookie_banner()
            cmp_issues = self._check_cmp_implementation()
            policy_issues = self._check_cookie_policy()
            tracking_issues = self._check_tracking_technologies()
            
            all_issues = banner_issues + cmp_issues + policy_issues + tracking_issues
            
            solution = GDPRSolution(
                description=(
                    "To ensure GDPR compliance for consent management:\n\n"
                    "1. Implement a clear, GDPR-compliant cookie banner\n"
                    "2. Provide granular consent options (accept, reject, customize)"
                    "3. Allow users to easily withdraw consent\n"
                    "4. Document and store user consent\n"
                    "5. Only load non-essential cookies after consent\n"
                ),
                code_snippet="""<!-- Example GDPR-compliant Cookie Banner -->
<div id="cookie-consent-banner">
  <div class="cookie-banner-content">
    <p>We use cookies to enhance your experience. 
       <a href="/cookie-policy">Learn more</a></p>
    <div class="cookie-actions">
      <button id="accept-cookies">Accept All</button>
      <button id="settings-cookies">Settings</button>
      <button id="reject-cookies">Reject Non-Essential</button>
    </div>
  </div>
</div>""",
                language="html"
            )
            
            if not all_issues:
                return self._create_result(
                    CheckStatus.PASSED,
                    "No consent management compliance issues detected.",
                    solution=solution
                )
                
            return self._create_result(
                CheckStatus.FAILED,
                "GDPR compliance issues with consent management:",
                solution=solution
            )
            
        except Exception as e:
            return self._create_result(
                CheckStatus.ERROR,
                f"Error checking consent management: {str(e)}",
                {"error": str(e)}
            )
    
    def _check_cookie_banner(self) -> List[str]:
        """Check for presence and compliance of cookie banner"""
        issues = []
        
        try:
            # Look for common cookie banner selectors
            banner_selectors = [
                "//*[contains(translate(., 'COOKIE', 'cookie')), 'cookie')]",
                "//*[contains(translate(@id, 'COOKIE', 'cookie'), 'cookie')]",
                "//*[contains(translate(@class, 'BANNER', 'banner'), 'banner')]"
            ]
            
            banner_found = False
            for selector in banner_selectors:
                try:
                    elements = self.driver.find_elements(By.XPATH, selector)
                    if elements and any(el.is_displayed() for el in elements):
                        banner_found = True
                        break
                except:
                    continue
            
            if not banner_found:
                issues.append("No cookie banner or consent mechanism found")
            
            # Check for required buttons
            if banner_found:
                try:
                    accept_buttons = self.driver.find_elements(
                        By.XPATH, "//button[contains(translate(., 'ACCEPT', 'accept'), 'accept')]"
                    )
                    
                    reject_buttons = self.driver.find_elements(
                        By.XPATH, "//button[contains(translate(., 'REJECT', 'reject'), 'reject') or "
                                 "contains(translate(., 'DECLINE', 'decline'), 'decline')]"
                    )
                    
                    settings_buttons = self.driver.find_elements(
                        By.XPATH, "//button[contains(translate(., 'SETTINGS', 'settings'), 'settings') or "
                                 "contains(translate(., 'PREFERENCES', 'preferences'), 'preferences')]"
                    )
                    
                    if not accept_buttons:
                        issues.append("Cookie banner missing accept button")
                    if not reject_buttons:
                        issues.append("Cookie banner missing reject/decline button")
                    if not settings_buttons:
                        issues.append("Cookie banner missing settings/preferences button")
                        
                except Exception as e:
                    issues.append(f"Error checking banner buttons: {str(e)}")
            
        except Exception as e:
            issues.append(f"Error checking cookie banner: {str(e)}")
            
        return issues
    
    def _check_cmp_implementation(self) -> List[str]:
        """Check for Consent Management Platform implementation"""
        issues = []
        
        try:
            # Check for common CMP frameworks
            common_cmps = [
                'onetrust', 'trustarc', 'truste', 'civic', 'cookiebot',
                'cookie-law', 'cookieconsent', 'quantcast', 'sirdata',
                'didomi', 'usercentrics', 'cookiefirst', 'cookiepro'
            ]
            
            # Check for CMP scripts
            scripts = self.driver.find_elements(By.TAG_NAME, 'script')
            found_cmp = False
            
            for script in scripts:
                src = script.get_attribute('src') or ''
                for cmp in common_cmps:
                    if cmp in src.lower():
                        found_cmp = True
                        break
                if found_cmp:
                    break
            
            # Check for IAB TCF compliance
            try:
                tcf_api = self.driver.execute_script("return window.__tcfapi !== undefined")
                if not tcf_api and found_cmp:
                    issues.append("CMP detected but IAB TCF API not implemented")
            except:
                pass
            
            # Check for consent cookie
            try:
                cookies = self.driver.get_cookies()
                consent_cookies = [c for c in cookies if 'consent' in c['name'].lower() or 'gdpr' in c['name'].lower()]
                
                if not consent_cookies and found_cmp:
                    issues.append("CMP detected but no consent cookie found")
            except:
                pass
            
        except Exception as e:
            issues.append(f"Error checking CMP: {str(e)}")
            
        return issues
    
    def _check_cookie_policy(self) -> List[str]:
        """Check for cookie policy and settings"""
        issues = []
        
        try:
            # Look for cookie policy link
            policy_links = self.driver.find_elements(
                By.XPATH, "//a[contains(translate(., 'COOKIE POLICY', 'cookie policy'), 'cookie policy') or "
                         "contains(translate(., 'COOKIE NOTICE', 'cookie notice'), 'cookie notice')]"
            )
            
            if not policy_links:
                issues.append("No cookie policy link found in the main navigation or footer")
            else:
                # Check policy page content
                try:
                    policy_links[0].click()
                    page_source = self.driver.page_source.lower()
                    
                    required_terms = [
                        'what are cookies', 'types of cookies', 'how we use cookies',
                        'managing cookies', 'third-party cookies'
                    ]
                    
                    for term in required_terms:
                        if term not in page_source:
                            issues.append(f"Cookie policy missing section: {term}")
                            
                except Exception as e:
                    issues.append(f"Error checking cookie policy page: {str(e)}")
            
        except Exception as e:
            issues.append(f"Error finding cookie policy: {str(e)}")
            
        return issues
    
    def _check_tracking_technologies(self) -> List[str]:
        """Check for tracking technologies and consent requirements"""
        issues = []
        
        try:
            # Check for common tracking scripts
            tracking_scripts = [
                'google-analytics.com', 'googletagmanager.com',
                'facebook.net', 'doubleclick.net', 'hotjar.com',
                'linkedin.com/analytics', 'twitter.com/analytics'
            ]
            
            scripts = self.driver.find_elements(By.TAG_NAME, 'script')
            found_trackers = []
            
            for script in scripts:
                src = script.get_attribute('src') or ''
                for tracker in tracking_scripts:
                    if tracker in src.lower() and tracker not in found_trackers:
                        found_trackers.append(tracker)
            
            if found_trackers:
                # Check if consent is required before loading
                try:
                    # Check for data attributes that might indicate consent-aware loading
                    consent_aware = self.driver.execute_script("""
                        return Array.from(document.querySelectorAll('script[data-cookiescript], script[data-cookieconsent]'))
                            .length > 0;
                    """)
                    
                    if not consent_aware:
                        issues.append("Tracking scripts detected without clear consent mechanism: " + 
                                    ", ".join(found_trackers))
                        
                except Exception as e:
                    issues.append(f"Error checking script consent: {str(e)}")
            
        except Exception as e:
            issues.append(f"Error checking tracking technologies: {str(e)}")
            
        return issues
