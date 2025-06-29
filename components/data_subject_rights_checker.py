"""Data Subject Rights Checker for GDPR Compliance"""
from typing import Dict, List, Optional
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.common.by import By
from urllib.parse import urljoin, urlparse

from components.base_checker import BaseChecker
from models.gdpr_check import GDPRCheckResult, CheckStatus, GDPRSolution
from config.constants import SEVERITY_HIGH, SEVERITY_MEDIUM, SEVERITY_LOW

class DataSubjectRightsChecker(BaseChecker):
    """Checks for implementation of data subject rights under GDPR"""
    
    @property
    def check_id(self) -> str:
        return "data_subject_rights"
    
    @property
    def check_name(self) -> str:
        return "Data Subject Rights Implementation"
    
    def _execute_check(self, url: str) -> GDPRCheckResult:
        """Check if the website implements data subject rights"""
        try:
            self.driver.get(url)
            
            # Look for common DSAR (Data Subject Access Request) related terms in links and buttons
            dsar_terms = [
                "data subject", "access request", "right to access", "right to be forgotten",
                "right to erasure", "right to rectification", "data portability",
                "privacy request", "gdpr request", "dsar", "subject access request"
            ]
            
            # Check page content for DSAR related terms
            page_text = self.driver.find_element(By.TAG_NAME, 'body').text.lower()
            found_terms = [term for term in dsar_terms if term in page_text]
            
            # Check for common DSAR form patterns
            dsar_forms = []
            for form in self.driver.find_elements(By.TAG_NAME, 'form'):
                form_html = form.get_attribute('outerHTML').lower()
                if any(term in form_html for term in dsar_terms):
                    dsar_forms.append(form)
            
            # Check privacy policy for DSAR information
            privacy_policy_links = self._find_privacy_policy_links()
            has_dsar_info = False
            
            if privacy_policy_links:
                for link in privacy_policy_links[:2]:  # Check first 2 privacy policy links
                    try:
                        self.driver.get(link)
                        policy_text = self.driver.find_element(By.TAG_NAME, 'body').text.lower()
                        if any(term in policy_text for term in dsar_terms):
                            has_dsar_info = True
                            break
                    except:
                        continue
            
            # Check for dedicated DSAR pages
            dsar_pages = self._find_dsar_pages()
            
            # Check contact information for DSAR requests
            contact_info = self._find_contact_information()
            has_dsar_contact = any(term in contact_info.lower() for term in dsar_terms + ["privacy", "data protection"])
            
            # Evaluate results
            issues = []
            
            if not found_terms and not dsar_forms and not has_dsar_info and not dsar_pages:
                issues.append("No clear information about data subject rights found on the website")
            
            if not has_dsar_contact:
                issues.append("No clear contact information for data subject requests found")
            
            if not issues:
                return self._create_result(
                    CheckStatus.PASSED,
                    "The website appears to implement data subject rights with clear information "
                    "and contact methods for requests."
                )
            
            return self._create_result(
                CheckStatus.FAILED,
                "Potential issues with data subject rights implementation:\n\n• " + 
                "\n• ".join(issues),
                solution=GDPRSolution(
                    description=("To properly implement data subject rights under GDPR, consider the following:\n\n"
                                "1. Create a dedicated Data Subject Access Request (DSAR) page\n"
                                "2. Clearly explain each data subject right (access, rectification, erasure, etc.)\n"
                                "3. Provide a clear and accessible way to submit requests\n"
                                "4. Include contact information for the Data Protection Officer (DPO) if applicable\n"
                                "5. Explain the process and timeline for handling requests\n"
                                "6. Provide information about any fees or identification requirements"),
                    code_snippet="""<!-- Example DSAR request form -->
<div class="dsar-request">
  <h2>Data Subject Access Request</h2>
  <p>Under GDPR, you have the right to access, correct, or delete your personal data.</p>
  
  <form id="dsar-form" action="/submit-dsar" method="post">
    <div class="form-group">
      <label for="request-type">Type of Request*</label>
      <select id="request-type" name="request_type" required>
        <option value="">-- Select Request Type --</option>
        <option value="access">Access my personal data</option>
        <option value="rectification">Correct my personal data</option>
        <option value="erasure">Delete my personal data (Right to be forgotten)</option>
        <option value="restriction">Restrict processing of my data</option>
        <option value="portability">Request data portability</option>
        <option value="object">Object to processing</option>
      </select>
    </div>
    
    <div class="form-group">
      <label for="name">Full Name*</label>
      <input type="text" id="name" name="name" required>
    </div>
    
    <div class="form-group">
      <label for="email">Email Address*</label>
      <input type="email" id="email" name="email" required>
    </div>
    
    <div class="form-group">
      <label for="description">Description of Request*</label>
      <textarea id="description" name="description" rows="5" required></textarea>
    </div>
    
    <div class="form-group">
      <p>To help us verify your identity, please provide additional information that can help us locate your data in our systems.</p>
      <label for="user-id">User ID (if known)</label>
      <input type="text" id="user-id" name="user_id">
    </div>
    
    <div class="form-group checkbox">
      <input type="checkbox" id="verify-identity" name="verify_identity" required>
      <label for="verify-identity">I understand that I may be asked to provide additional information to verify my identity*</label>
    </div>
    
    <div class="form-group">
      <p>We will respond to your request within 30 days. For more information, please see our <a href="/privacy-policy#dsar" target="_blank">Data Subject Rights Policy</a>.</p>
    </div>
    
    <button type="submit" class="btn btn-primary">Submit Request</button>
  </form>
</div>""",
                    language="html"
                )
            )
            
        except Exception as e:
            return self._create_result(
                CheckStatus.ERROR,
                f"Error checking data subject rights implementation: {str(e)}",
                {"error": str(e)}
            )
    
    def _find_privacy_policy_links(self) -> List[str]:
        """Find links to privacy policy pages"""
        privacy_terms = ["privacy", "datenschutz", "gdpr", "data protection"]
        links = []
        
        for a in self.driver.find_elements(By.TAG_NAME, 'a'):
            try:
                href = a.get_attribute('href')
                text = a.text.lower()
                if any(term in text or (href and any(term in href.lower() for term in privacy_terms)) for term in privacy_terms):
                    links.append(href)
            except:
                continue
        
        return links
    
    def _find_dsar_pages(self) -> List[str]:
        """Find DSAR (Data Subject Access Request) related pages"""
        dsar_terms = ["data subject", "access request", "right to access", "right to be forgotten"]
        links = []
        
        for a in self.driver.find_elements(By.TAG_NAME, 'a'):
            try:
                href = a.get_attribute('href')
                text = a.text.lower()
                if any(term in text or (href and any(term in href.lower() for term in dsar_terms)) for term in dsar_terms):
                    links.append(href)
            except:
                continue
        
        return links
    
    def _find_contact_information(self) -> str:
        """Extract contact information from contact/DSAR pages"""
        contact_terms = ["contact", "get in touch", "reach us", "data protection officer", "dpo"]
        contact_texts = []
        
        # Check current page for contact information
        try:
            contact_links = []
            for a in self.driver.find_elements(By.TAG_NAME, 'a'):
                try:
                    text = a.text.lower()
                    if any(term in text for term in contact_terms):
                        contact_links.append(a.get_attribute('href'))
                except:
                    continue
            
            # Follow contact links and collect text
            for link in contact_links[:2]:  # Limit to first 2 contact links
                try:
                    self.driver.get(link)
                    contact_texts.append(self.driver.find_element(By.TAG_NAME, 'body').text)
                except:
                    continue
        except:
            pass
        
        return " ".join(contact_texts)
