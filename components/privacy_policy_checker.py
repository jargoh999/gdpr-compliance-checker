"""GDPR Privacy Policy Checker"""
from typing import Dict, Any, List, Optional
from urllib.parse import urljoin, urlparse
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.common.by import By
import requests

from .base_checker import BaseChecker
from models.gdpr_check import GDPRCheckResult, CheckStatus, GDPRSolution

class PrivacyPolicyChecker(BaseChecker):
    """Checks for the presence and content of a privacy policy"""
    
    @property
    def check_id(self) -> str:
        return "privacy_policy_check"
    
    @property
    def check_name(self) -> str:
        return "Privacy Policy Check"
    
    @property
    def severity(self) -> str:
        return "high"
    
    def _execute_check(self, url: str) -> GDPRCheckResult:
        """Check for the presence and content of a privacy policy"""
        # First, try to find a link to the privacy policy
        privacy_links = self._find_privacy_links()
        
        if not privacy_links:
            return self._create_result(
                status=CheckStatus.FAILED,
                description="No privacy policy link found on the website.",
                solution=self._create_solution(
                    description="Add a clearly visible link to your privacy policy in the website footer or main navigation.",
                    code_snippet="""
<!-- Example of a privacy policy link in the footer -->
<footer>
    <div class="container">
        <div class="footer-links">
            <a href="/privacy-policy">Privacy Policy</a>
            <a href="/terms">Terms of Service</a>
            <a href="/cookies">Cookie Policy</a>
        </div>
    </div>
</footer>

<!-- Or in the main navigation -->
<nav>
    <a href="/">Home</a>
    <a href="/about">About</a>
    <a href="/contact">Contact</a>
    <a href="/privacy-policy" class="privacy-link">Privacy</a>
</nav>

<style>
/* Make the privacy link stand out */
.privacy-link {
    color: #dc3545;
    font-weight: bold;
}
</style>
"""
                )
            )
        
        # Check the first privacy policy link found
        privacy_url = privacy_links[0]
        privacy_content = self._get_page_content(privacy_url)
        
        if not privacy_content:
            return self._create_result(
                status=CheckStatus.FAILED,
                description=f"Could not access privacy policy at {privacy_url}",
                solution=self._create_solution(
                    description="Ensure the privacy policy URL is accessible and returns a 200 OK status code.",
                    code_snippet="# Check your server logs to ensure the privacy policy page is accessible\n# and not returning any errors."
                )
            )
        
        # Check for common privacy policy sections
        required_sections = [
            ("data collection", "information we collect"),
            ("data usage", "how we use your information"),
            ("data sharing", "sharing your information"),
            ("cookies", "cookies and tracking"),
            ("rights", "your rights"),
            ("gdpr", "gdpr"),
            ("contact", "contact us")
        ]
        
        missing_sections = []
        content_lower = privacy_content.lower()
        
        for section_key, section_name in required_sections:
            if section_key not in content_lower:
                missing_sections.append(section_name)
        
        if missing_sections:
            return self._create_result(
                status=CheckStatus.FAILED,
                description=f"Privacy policy is missing important sections: {', '.join(missing_sections)}.",
                details={
                    "privacy_policy_url": privacy_url,
                    "missing_sections": missing_sections
                },
                solution=self._create_solution(
                    description=f"Update your privacy policy to include the following sections: {', '.join(missing_sections)}. Ensure it covers all required GDPR information.",
                    code_snippet="""
<!-- Example privacy policy structure -->
<div class="privacy-policy">
    <h1>Privacy Policy</h1>
    
    <section>
        <h2>1. Information We Collect</h2>
        <p>We collect the following types of information:</p>
        <ul>
            <li>Personal information (name, email, etc.)</li>
            <li>Usage data and analytics</li>
            <li>Cookies and tracking information</li>
        </ul>
    </section>
    
    <section>
        <h2>2. How We Use Your Information</h2>
        <p>We use your information to:</p>
        <ul>
            <li>Provide and maintain our service</li>
            <li>Improve user experience</li>
            <li>Send important notifications</li>
        </ul>
    </section>
    
    <section>
        <h2>3. Data Sharing and Disclosure</h2>
        <p>We do not sell your personal information. We may share data with:</p>
        <ul>
            <li>Service providers</li>
            <li>Legal requirements</li>
            <li>Business transfers</li>
        </ul>
    </section>
    
    <section>
        <h2>4. Your Rights Under GDPR</h2>
        <p>Under GDPR, you have the right to:</p>
        <ul>
            <li>Access your personal data</li>
            <li>Rectify inaccurate data</li>
            <li>Request deletion of your data</li>
            <li>Restrict or object to processing</li>
            <li>Data portability</li>
            <li>Withdraw consent</li>
        </ul>
        <p>To exercise these rights, contact us at privacy@example.com.</p>
    </section>
    
    <section>
        <h2>5. Cookies and Tracking</h2>
        <p>We use cookies to improve your experience. You can manage your cookie preferences in your browser settings.</p>
    </section>
    
    <section>
        <h2>6. Contact Us</h2>
        <p>If you have any questions about this Privacy Policy, please contact us:</p>
        <p>Email: privacy@example.com</p>
        <p>Address: 123 Privacy St, City, Country</p>
    </section>
    
    <section>
        <h2>7. Changes to This Policy</h2>
        <p>We may update our Privacy Policy from time to time. We will notify you of any changes by posting the new Privacy Policy on this page.</p>
    </section>
</div>
"""
                )
            )
        
        return self._create_result(
            status=CheckStatus.PASSED,
            description="Privacy policy is properly implemented and includes all required sections.",
            details={
                "privacy_policy_url": privacy_url,
                "has_required_sections": True
            }
        )
    
    def _find_privacy_links(self) -> List[str]:
        """Find links to the privacy policy on the page"""
        privacy_terms = [
            'privacy', 'gdpr', 'data protection', 'privacy policy', 'privacy notice',
            'privacy statement', 'datenschutz', 'confidentialité', 'privacidad',
            'privacy-policy', 'privacypolicy', 'privacy_notice', 'privacy-policy.html'
        ]
        
        # Check common footer links
        footer = self._find_element(By.TAG_NAME, 'footer')
        if footer:
            links = footer.find_elements(By.TAG_NAME, 'a')
            for link in links:
                href = link.get_attribute('href')
                text = link.text.lower()
                if href and any(term in text or term in href.lower() for term in privacy_terms):
                    return [self._make_absolute_url(href)]
        
        # Check all links on the page
        links = self.driver.find_elements(By.TAG_NAME, 'a')
        found_links = []
        
        for link in links:
            try:
                href = link.get_attribute('href')
                text = link.text.lower()
                if href and any(term in text or term in href.lower() for term in privacy_terms):
                    found_links.append(self._make_absolute_url(href))
            except:
                continue
        
        return found_links
    
    def _make_absolute_url(self, url: str) -> str:
        """Convert a relative URL to absolute"""
        if url.startswith('http'):
            return url
        
        # Get the base URL from the current page
        base_url = f"{self.driver.current_url.split('//')[0]}//{self.driver.current_url.split('//')[1].split('/')[0]}"
        
        # Handle relative URLs
        if url.startswith('/'):
            return f"{base_url}{url}"
        else:
            return f"{base_url}/{url}"
    
    def _get_page_content(self, url: str) -> Optional[str]:
        """Get the content of a web page"""
        try:
            # First try with Selenium to handle JavaScript-rendered content
            self.driver.get(url)
            return self.driver.page_source
        except Exception as e:
            try:
                # Fall back to requests if Selenium fails
                response = requests.get(url, timeout=10)
                if response.status_code == 200:
                    return response.text
            except:
                pass
        return None
