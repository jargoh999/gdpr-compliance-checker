"""Data Breach Notification Checker for GDPR Compliance"""
from typing import Dict, List, Optional, Set, Tuple
import re
from datetime import datetime, timedelta
from urllib.parse import urljoin, urlparse

from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.common.by import By

from components.base_checker import BaseChecker
from models.gdpr_check import GDPRCheckResult, CheckStatus, GDPRSolution
from config.constants import SEVERITY_HIGH, SEVERITY_MEDIUM, SEVERITY_LOW

class DataBreachChecker(BaseChecker):
    """Checks for GDPR compliance in data breach notification procedures"""
    
    @property
    def check_id(self) -> str:
        return "data_breach"
    
    @property
    def check_name(self) -> str:
        return "Data Breach Notification"
    
    def _execute_check(self, url: str) -> GDPRCheckResult:
        """Check for data breach notification compliance"""
        try:
            # Check privacy policy for breach notification information
            policy_issues = self._check_privacy_policy()
            
            # Check for breach notification procedures
            procedure_issues = self._check_breach_procedures()
            
            # Check for contact methods for breach reporting
            contact_issues = self._check_contact_methods()
            
            # Check for data protection officer (DPO) information
            dpo_issues = self._check_dpo_information()
            
            # Combine all issues
            all_issues = policy_issues + procedure_issues + contact_issues + dpo_issues
            
            # Prepare solution with detailed guidance
            solution = GDPRSolution(
                description=(
                    "To ensure GDPR compliance for data breach notifications:\n\n"
                    "1. Document your data breach response procedures in your privacy policy\n"
                    "2. Create a clear process for detecting, reporting, and investigating breaches\n"
                    "3. Establish a 72-hour response timeline for reporting breaches to authorities\n"
                    "4. Implement a process for notifying affected individuals when necessary\n"
                    "5. Maintain an internal breach register to document all incidents\n"
                    "6. Provide clear contact methods for reporting potential breaches"
                ),
                code_snippet="""<!-- Example privacy policy section for data breach notifications -->
<section id="data-breaches">
  <h2>Data Breach Notification</h2>
  
  <p>We take the security of your personal data seriously and have implemented measures to prevent data breaches. However, in the unlikely event of a data breach, we have procedures in place to respond effectively.</p>
  
  <h3>Our Data Breach Response Process</h3>
  <p>In accordance with the General Data Protection Regulation (GDPR), we will notify the relevant supervisory authority of a data breach within 72 hours of becoming aware of it, unless the breach is unlikely to result in a risk to your rights and freedoms.</p>
  
  <p>If the breach is likely to result in a high risk to your rights and freedoms, we will also notify you without undue delay. The notification will include:</p>
  
  <ul>
    <li>A description of the nature of the breach</li>
    <li>The name and contact details of our Data Protection Officer</li>
    <li>The likely consequences of the breach</li>
    <li>The measures taken or proposed to address the breach</li>
    <li>Steps you can take to protect yourself</li>
  </ul>
  
  <h3>Reporting a Suspected Data Breach</h3>
  <p>If you suspect a data breach has occurred, please immediately contact our Data Protection Officer at <a href="mailto:dpo@example.com">dpo@example.com</a> or by phone at +1 (555) 123-4567.</p>
  
  <p>When reporting a suspected breach, please provide as much information as possible, including:</p>
  <ul>
    <li>A description of the incident</li>
    <li>The date and time you became aware of the incident</li>
    <li>The type of personal data that may be affected</li>
    <li>The potential impact of the breach</li>
    <li>Any steps you've already taken in response</li>
  </ul>
  
  <h3>Our Commitment to Security</h3>
  <p>We implement appropriate technical and organizational measures to ensure a level of security appropriate to the risk, including:</p>
  <ul>
    <li>Regular security assessments and testing</li>
    <li>Encryption of personal data in transit and at rest</li>
    <li>Access controls and authentication mechanisms</li>
    <li>Staff training on data protection and security</li>
    <li>Regular review of our information security policies</li>
  </ul>
  
  <div class="alert alert-info">
    <h4>Data Protection Officer</h4>
    <p>We have appointed a Data Protection Officer (DPO) who is responsible for overseeing questions in relation to data protection. If you have any questions about this Data Breach Policy, please contact our DPO:</p>
    <address>
      <strong>Data Protection Officer</strong><br>
      Example Company Ltd.<br>
      123 Data Protection Street<br>
      London, EC1A 1AA<br>
      United Kingdom<br>
      Email: <a href="mailto:dpo@example.com">dpo@example.com</a><br>
      Phone: +1 (555) 123-4567
    </address>
  </div>
</section>

<style>
#data-breaches {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
  font-family: Arial, sans-serif;
  line-height: 1.6;
}

#data-breaches h2 {
  color: #2c3e50;
  border-bottom: 2px solid #3498db;
  padding-bottom: 10px;
  margin-top: 30px;
}

#data-breaches h3 {
  color: #2980b9;
  margin-top: 25px;
}

#data-breaches h4 {
  color: #2c3e50;
  margin-top: 20px;
}

#data-breaches ul {
  padding-left: 20px;
}

#data-breaches li {
  margin-bottom: 8px;
}

.alert {
  padding: 15px;
  margin: 20px 0;
  border: 1px solid #b8daff;
  border-radius: 4px;
  background-color: #e7f5ff;
}

.alert-info {
  color: #055160;
  background-color: #cff4fc;
  border-color: #b6effb;
}

address {
  font-style: normal;
  margin: 15px 0;
  line-height: 1.6;
}

a {
  color: #007bff;
  text-decoration: none;
}

a:hover {
  text-decoration: underline;
}
</style>

<!-- Data Breach Response Plan Document -->
<div class="breach-response-plan">
  <h2>Data Breach Response Plan</h2>
  
  <div class="section">
    <h3>1. Breach Detection and Assessment</h3>
    <p>All staff are trained to recognize and report potential data breaches immediately to the Data Protection Officer (DPO).</p>
    
    <h4>1.1 Identifying a Breach</h4>
    <p>A personal data breach means a breach of security leading to the accidental or unlawful destruction, loss, alteration, unauthorized disclosure of, or access to, personal data.</p>
    
    <h4>1.2 Initial Assessment</h4>
    <p>Upon receiving a report of a potential breach, the DPO will conduct an initial assessment to determine:</p>
    <ul>
      <li>If a breach has occurred</li>
      <li>The nature of the personal data involved</li>
      <li>Who might be affected</li>
      <li>The potential impact on individuals</li>
      <li>Whether the breach needs to be reported to the relevant supervisory authority</li>
    </ul>
  </div>
  
  <div class="section">
    <h3>2. Containing the Breach</h3>
    <p>Immediate steps will be taken to contain the breach and prevent further unauthorized access or damage.</p>
    
    <h4>2.1 Containment Actions</h4>
    <ul>
      <li>Isolate affected systems</li>
      <li>Revoke or change access credentials</li>
      <li>Preserve evidence for investigation</li>
      <li>Engage forensic experts if necessary</li>
    </ul>
  </div>
  
  <div class="section">
    <h3>3. Assessing the Risk</h3>
    <p>The DPO will assess the risk to individuals' rights and freedoms, considering:</p>
    <ul>
      <li>The type of breach</li>
      <li>The nature, sensitivity, and volume of personal data</li>
      <li>Ease of identification of individuals</li>
      <li>Severity of consequences for individuals</li>
      <li>Special characteristics of individuals (e.g., children, vulnerable persons)</li>
      <li>Special categories of personal data involved</li>
    </ul>
  </div>
  
  <div class="section">
    <h3>4. Notifying the Supervisory Authority</h3>
    <p>Where a breach is likely to result in a risk to individuals' rights and freedoms, the DPO will notify the relevant supervisory authority within 72 hours of becoming aware of the breach.</p>
    
    <h4>4.1 Information to Include</h4>
    <ul>
      <li>Nature of the personal data breach</li>
      <li>Categories and approximate number of individuals affected</li>
      <li>Name and contact details of the DPO</li>
      <li>Likely consequences of the breach</li>
      <li>Measures taken or proposed to address the breach</li>
    </ul>
  </div>
  
  <div class="section">
    <h3>5. Communicating with Affected Individuals</h3>
    <p>If the breach is likely to result in a high risk to individuals' rights and freedoms, affected individuals will be notified without undue delay.</p>
    
    <h4>5.1 Notification Content</h4>
    <p>Notifications to individuals will be clear and include:</p>
    <ul>
      <li>Description of the breach in clear language</li>
      <li>Name and contact details of the DPO</li>
      <li>Likely consequences of the breach</li>
      <li>Measures taken or proposed to address the breach</li>
      <li>Steps individuals can take to protect themselves</li>
    </ul>
  </div>
  
  <div class="section">
    <h3>6. Review and Prevention</h3>
    <p>Following any data breach, we will conduct a thorough review of the incident to identify lessons learned and implement improvements to prevent similar breaches in the future.</p>
    
    <h4>6.1 Post-Incident Review</h4>
    <ul>
      <li>Root cause analysis</li>
      <li>Effectiveness of response</li>
      <li>Policy and procedure updates</li>
      <li>Additional staff training requirements</li>
      <li>Technical or organizational changes needed</li>
    </ul>
  </div>
  
  <div class="section">
    <h3>7. Documentation</h3>
    <p>All data breaches, regardless of whether they are reported to the supervisory authority, will be documented in our internal breach register, including:</p>
    <ul>
      <li>Date and time of the breach</li>
      <li>Date and time of detection</li>
      <li>Description of the breach</li>
      <li>Categories of personal data affected</li>
      <li>Number of individuals affected</li>
      <li>Consequences of the breach</li>
      <li>Remedial actions taken</li>
    </ul>
  </div>
</div>

<style>
.breach-response-plan {
  max-width: 900px;
  margin: 0 auto;
  padding: 20px;
  font-family: Arial, sans-serif;
  line-height: 1.6;
  color: #333;
}

.breach-response-plan h2 {
  color: #2c3e50;
  text-align: center;
  margin-bottom: 30px;
  padding-bottom: 10px;
  border-bottom: 2px solid #3498db;
}

.breach-response-plan h3 {
  color: #2980b9;
  margin-top: 30px;
  padding-bottom: 5px;
  border-bottom: 1px solid #eee;
}

.breach-response-plan h4 {
  color: #2c3e50;
  margin-top: 20px;
}

.breach-response-plan p {
  margin: 10px 0;
}

.breach-response-plan ul {
  padding-left: 25px;
}

.breach-response-plan li {
  margin-bottom: 8px;
}

.section {
  margin-bottom: 30px;
  padding: 15px;
  background-color: #fff;
  border-radius: 5px;
  box-shadow: 0 2px 5px rgba(0,0,0,0.1);
}

.section:last-child {
  margin-bottom: 0;
}

/* Responsive design */
@media (max-width: 768px) {
  .breach-response-plan {
    padding: 10px;
  }
  
  .section {
    padding: 10px;
  }
}
</style>

<!-- Data Breach Notification Email Template -->
<div class="email-template">
  <div class="email-header">
    <h2>Data Breach Notification</h2>
    <p><strong>Subject:</strong> Important Notice: Data Security Incident</p>
  </div>
  
  <div class="email-body">
    <p>Dear [Recipient's Name],</p>
    
    <p>We are writing to inform you about a recent data security incident that may have involved some of your personal information. The privacy and security of your data is of utmost importance to us, and we take this matter very seriously.</p>
    
    <h3>What Happened</h3>
    <p>On [Date], we became aware of [brief description of the breach, including when it was discovered and what systems were affected].</p>
    
    <h3>What Information Was Involved</h3>
    <p>The information involved may have included: [list of data types, e.g., names, email addresses, passwords, etc.].</p>
    
    <h3>What We Are Doing</h3>
    <p>We have taken the following steps in response to this incident:</p>
    <ul>
      <li>Immediately secured our systems and conducted a thorough investigation</li>
      <li>Engaged cybersecurity experts to assist with our response</li>
      <li>Notified the relevant data protection authorities</li>
      <li>Implemented additional security measures to prevent similar incidents</li>
    </ul>
    
    <h3>What You Can Do</h3>
    <p>While we have no evidence that your information has been misused, we recommend that you:</p>
    <ol>
      <li>Change your password for our service and any other accounts where you use the same or similar passwords</li>
      <li>Be cautious of any suspicious emails or communications that ask for personal information</li>
      <li>Monitor your accounts for any unauthorized activity</li>
      <li>Consider placing a fraud alert or credit freeze on your credit files</li>
    </ol>
    
    <h3>For More Information</h3>
    <p>We sincerely apologize for any concern or inconvenience this may cause. If you have any questions or need assistance, please contact our dedicated support team at [contact information] or visit [URL] for more information.</p>
    
    <p>Thank you for your understanding and continued trust in [Company Name].</p>
    
    <p>Sincerely,<br>
    [Your Name]<br>
    [Your Position]<br>
    [Company Name]</p>
  </div>
  
  <div class="email-footer">
    <p><strong>Contact Information:</strong><br>
    [Company Name]<br>
    [Company Address]<br>
    [Phone Number]<br>
    [Email Address]</p>
    
    <p class="small">This email was sent to [email] because you are a valued customer of [Company Name]. If you would prefer not to receive emails from us, please <a href="[unsubscribe link]" style="color: #3498db;">unsubscribe here</a>.</p>
  </div>
</div>

<style>
.email-template {
  max-width: 600px;
  margin: 0 auto;
  font-family: Arial, sans-serif;
  line-height: 1.6;
  color: #333;
  border: 1px solid #ddd;
  border-radius: 5px;
  overflow: hidden;
}

.email-header {
  background-color: #f8f9fa;
  padding: 20px;
  border-bottom: 1px solid #eee;
}

.email-header h2 {
  margin: 0 0 10px 0;
  color: #2c3e50;
}

.email-body {
  padding: 20px;
  background-color: #fff;
}

.email-body h3 {
  color: #2c3e50;
  margin: 20px 0 10px 0;
}

.email-body ul, .email-body ol {
  margin: 10px 0;
  padding-left: 25px;
}

.email-body li {
  margin-bottom: 5px;
}

.email-footer {
  padding: 15px 20px;
  background-color: #f8f9fa;
  border-top: 1px solid #eee;
  font-size: 0.9em;
  color: #666;
}

.email-footer .small {
  font-size: 0.8em;
  margin-top: 15px;
  padding-top: 15px;
  border-top: 1px solid #eee;
}

/* Responsive design */
@media (max-width: 480px) {
  .email-template {
    margin: 10px;
  }
  
  .email-header, .email-body, .email-footer {
    padding: 15px;
  }
}
</style>""",
                language="html"
            )
            
            if not all_issues:
                return self._create_result(
                    CheckStatus.PASSED,
                    "No data breach notification compliance issues detected.",
                    solution=solution
                )
                
            return self._create_result(
                CheckStatus.FAILED,
                "Potential GDPR compliance issues with data breach notifications:\n\n• " + 
                "\n• ".join(all_issues),
                solution=solution
            )
            
        except Exception as e:
            return self._create_result(
                CheckStatus.ERROR,
                f"Error checking data breach notification compliance: {str(e)}",
                {"error": str(e)}
            )
    
    def _check_privacy_policy(self) -> List[str]:
        """Check privacy policy for breach notification information"""
        issues = []
        
        try:
            # Look for privacy policy link
            privacy_links = self.driver.find_elements(
                By.XPATH, "//a[contains(translate(., 'PRIVACY', 'privacy'), 'privacy') or "
                         "contains(translate(., 'POLICY', 'policy'), 'policy')]"
            )
            
            if not privacy_links:
                issues.append("No privacy policy link found")
                return issues
                
            # Click the first privacy policy link
            privacy_links[0].click()
            
            # Get page content
            page_source = self.driver.page_source.lower()
            
            # Check for breach-related terms
            breach_terms = [
                'data breach', 'security breach', 'personal data breach',
                'breach notification', 'gdpr article 33', 'gdpr article 34',
                '72 hour', 'seventy-two hour', 'report a breach', 'breach response',
                'data security incident', 'security incident', 'data incident'
            ]
            
            if not any(term in page_source for term in breach_terms):
                issues.append("No data breach notification procedures found in privacy policy")
                
            # Check for specific requirements
            requirement_terms = [
                '72 hour', 'seventy-two hour', 'without undue delay',
                'supervisory authority', 'data protection authority',
                'high risk to rights and freedoms', 'affected individuals',
                'data protection officer', 'dpo', 'breach response plan'
            ]
            
            if not any(term in page_source for term in requirement_terms):
                issues.append("Insufficient detail about breach notification requirements")
                
        except Exception as e:
            issues.append(f"Error checking privacy policy: {str(e)}")
            
        return issues
    
    def _check_breach_procedures(self) -> List[str]:
        """Check for documented breach procedures"""
        issues = []
        
        try:
            # Look for security or breach-related pages
            security_links = self.driver.find_elements(
                By.XPATH, "//a[contains(translate(., 'SECURITY', 'security'), 'security') or "
                         "contains(translate(., 'BREACH', 'breach'), 'breach') or "
                         "contains(translate(., 'INCIDENT', 'incident'), 'incident') or "
                         "contains(translate(., 'REPORT', 'report'), 'report')]"
            )
            
            if not security_links:
                issues.append("No security or breach reporting pages found")
                return issues
                
            # Check each security-related page
            found_breach_info = False
            
            for link in security_links[:3]:  # Check first 3 links to avoid too many clicks
                try:
                    link_text = link.text.lower()
                    if 'login' in link_text or 'sign in' in link_text:
                        continue
                        
                    link.click()
                    
                    # Check page content
                    page_source = self.driver.page_source.lower()
                    
                    # Look for breach-related content
                    if any(term in page_source for term in ['data breach', 'security incident', 'report a breach']):
                        found_breach_info = True
                        
                        # Check for specific elements
                        if not any(term in page_source for term in ['contact us', 'report', 'email', 'phone', 'form']):
                            issues.append("Breach reporting page lacks clear contact methods")
                            
                        if not any(term in page_source for term in ['what to report', 'what information to include', 'details needed']):
                            issues.append("Breach reporting page lacks guidance on what information to provide")
                            
                        break
                        
                except:
                    continue
                    
            if not found_breach_info:
                issues.append("No detailed breach reporting procedures found")
                
        except Exception as e:
            issues.append(f"Error checking breach procedures: {str(e)}")
            
        return issues
    
    def _check_contact_methods(self) -> List[str]:
        """Check for contact methods to report breaches"""
        issues = []
        
        try:
            # Look for contact or support pages
            contact_links = self.driver.find_elements(
                By.XPATH, "//a[contains(translate(., 'CONTACT', 'contact'), 'contact') or "
                         "contains(translate(., 'SUPPORT', 'support'), 'support') or "
                         "contains(translate(., 'HELP', 'help'), 'help') or "
                         "contains(translate(., 'REPORT', 'report'), 'report')]"
            )
            
            if not contact_links:
                issues.append("No contact or support page found")
                return issues
                
            # Check each contact page
            found_breach_contact = False
            
            for link in contact_links[:3]:  # Check first 3 links
                try:
                    link_text = link.text.lower()
                    if 'login' in link_text or 'sign in' in link_text:
                        continue
                        
                    link.click()
                    
                    # Check page content
                    page_source = self.driver.page_source.lower()
                    
                    # Look for breach reporting options
                    if any(term in page_source for term in ['data breach', 'security incident', 'report a breach', 'security concern']):
                        found_breach_contact = True
                        
                        # Check for specific contact methods
                        contact_methods = []
                        
                        # Check for email
                        if re.search(r'[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}', page_source):
                            contact_methods.append("email")
                            
                        # Check for phone
                        if re.search(r'\+?[\d\s-()]{10,}', page_source):
                            contact_methods.append("phone")
                            
                        # Check for contact form
                        if 'form' in page_source or 'submit' in page_source:
                            contact_methods.append("form")
                            
                        if not contact_methods:
                            issues.append("No clear contact methods found on breach reporting page")
                            
                        break
                        
                except:
                    continue
                    
            if not found_breach_contact:
                issues.append("No specific contact method for reporting breaches found")
                
        except Exception as e:
            issues.append(f"Error checking contact methods: {str(e)}")
            
        return issues
    
    def _check_dpo_information(self) -> List[str]:
        """Check for Data Protection Officer (DPO) information"""
        issues = []
        
        try:
            # Look for DPO or privacy-related information
            dpo_links = self.driver.find_elements(
                By.XPATH, "//a[contains(., 'DPO') or contains(., 'Data Protection Officer') or "
                         "contains(., 'Privacy Officer') or contains(., 'Data Privacy') or "
                         "contains(., 'GDPR')]"
            )
            
            # Also check privacy policy
            privacy_links = self.driver.find_elements(
                By.XPATH, "//a[contains(translate(., 'PRIVACY', 'privacy'), 'privacy') or "
                         "contains(translate(., 'POLICY', 'policy'), 'policy')]"
            )
            
            if not dpo_links and not privacy_links:
                issues.append("No DPO or privacy information found")
                return issues
                
            # Check DPO links first
            found_dpo_info = False
            
            for link in dpo_links[:2]:  # Check first 2 DPO links
                try:
                    link.click()
                    
                    # Check page content
                    page_source = self.driver.page_source.lower()
                    
                    # Look for DPO contact information
                    if any(term in page_source for term in ['data protection officer', 'dpo', 'privacy officer', 'gdpr']):
                        found_dpo_info = True
                        
                        # Check for contact details
                        if not any(term in page_source for term in ['@', 'email', 'phone', 'contact']):
                            issues.append("DPO page lacks contact information")
                            
                        break
                        
                except:
                    continue
            
            # If no DPO info found, check privacy policy
            if not found_dpo_info and privacy_links:
                try:
                    privacy_links[0].click()
                    
                    # Check page content
                    page_source = self.driver.page_source.lower()
                    
                    # Look for DPO information
                    if any(term in page_source for term in ['data protection officer', 'dpo', 'privacy officer']):
                        found_dpo_info = True
                        
                        # Check for contact details
                        if not any(term in page_source for term in ['@', 'email', 'phone', 'contact']):
                            issues.append("Privacy policy mentions DPO but lacks contact information")
                    else:
                        issues.append("No Data Protection Officer (DPO) information found")
                        
                except:
                    pass
                    
            if not found_dpo_info:
                issues.append("No Data Protection Officer (DPO) information found")
                
        except Exception as e:
            issues.append(f"Error checking DPO information: {str(e)}")
            
        return issues
