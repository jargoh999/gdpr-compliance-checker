"""Data Retention Policy Checker for GDPR Compliance"""
from typing import Dict, List, Optional, Tuple
import re
from datetime import datetime, timedelta
from urllib.parse import urljoin

from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.common.by import By

from components.base_checker import BaseChecker
from models.gdpr_check import GDPRCheckResult, CheckStatus, GDPRSolution
from config.constants import SEVERITY_HIGH, SEVERITY_MEDIUM, SEVERITY_LOW

class DataRetentionChecker(BaseChecker):
    """Checks for proper data retention policies and practices"""
    
    @property
    def check_id(self) -> str:
        return "data_retention"
    
    @property
    def check_name(self) -> str:
        return "Data Retention Policy"
    
    def _execute_check(self, url: str) -> GDPRCheckResult:
        """Check for data retention policy compliance"""
        try:
            # Check privacy policy for retention information
            retention_info = self._check_privacy_policy()
            
            # Check for user account data retention
            account_retention = self._check_account_retention()
            
            # Check for cookie retention periods
            cookie_retention = self._check_cookie_retention()
            
            # Check for data deletion options
            deletion_options = self._check_deletion_options()
            
            # Check for data export options
            export_options = self._check_export_options()
            
            # Prepare issues list
            issues = []
            
            # Check if retention periods are specified
            if not retention_info['has_retention_section']:
                issues.append("No explicit data retention period found in privacy policy")
            
            if not retention_info['has_legal_basis']:
                issues.append("Legal basis for data retention not clearly specified")
                
            if not retention_info['has_retention_periods']:
                issues.append("Specific retention periods for different data types not specified")
                
            if not account_retention['has_retention_policy']:
                issues.append("User account data retention policy not clearly defined")
                
            if not cookie_retention['has_retention_info']:
                issues.append("Cookie retention periods not clearly specified")
                
            if not deletion_options['has_deletion_option']:
                issues.append("No clear option for users to request data deletion")
                
            if not export_options['has_export_option']:
                issues.append("No clear option for users to export their data")
            
            # Prepare solution with detailed guidance
            solution = GDPRSolution(
                description=(
                    "To ensure GDPR compliance for data retention:\n\n"
                    "1. Document your data retention policy clearly in your privacy policy\n"
                    "2. Specify retention periods for different categories of personal data\n"
                    "3. Explain the legal basis for retaining personal data\n"
                    "4. Implement processes for secure data deletion when retention periods expire\n"
                    "5. Provide users with options to request data deletion or export\n"
                    "6. Document your data retention schedule and review it regularly"
                ),
                code_snippet="""<!-- Example privacy policy section for data retention -->
<section id="data-retention">
  <h2>Data Retention</h2>
  <p>We retain personal data only for as long as necessary to fulfill the purposes for which it was collected, including for the purposes of satisfying any legal, accounting, or reporting requirements. To determine the appropriate retention period, we consider:</p>
  
  <ul>
    <li>The amount, nature, and sensitivity of the personal data</li>
    <li>The potential risk of harm from unauthorized use or disclosure</li>
    <li>The purposes for which we process your data</li>
    <li>Any applicable legal requirements</li>
  </ul>
  
  <p>Our retention periods are as follows:</p>
  
  <table class="retention-table">
    <thead>
      <tr>
        <th>Type of Data</th>
        <th>Retention Period</th>
        <th>Legal Basis</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td>User account information</td>
        <td>3 years after last activity</td>
        <td>Contract, Legitimate Interest</td>
      </tr>
      <tr>
        <td>Transaction records</td>
        <td>7 years</td>
        <td>Legal Obligation</td>
      </tr>
      <tr>
        <td>Website analytics</td>
        <td>26 months</td>
        <td>Consent</td>
      </tr>
      <tr>
        <td>Marketing data</td>
        <td>Until consent is withdrawn</td>
        <td>Consent</td>
      </tr>
      <tr>
        <td>Job applicant data</td>
        <td>6 months after application</td>
        <td>Legitimate Interest</td>
      </tr>
    </tbody>
  </table>
  
  <p>After the retention period expires, we will either delete or anonymize your personal data so that it can no longer be associated with you.</p>
  
  <h3>Your Rights</h3>
  <p>Under the GDPR, you have the right to:</p>
  <ul>
    <li>Request access to your personal data</li>
    <li>Request correction of your personal data</li>
    <li>Request erasure of your personal data</li>
    <li>Object to processing of your personal data</li>
    <li>Request restriction of processing</li>
    <li>Request data portability</li>
    <li>Withdraw consent at any time</li>
  </ul>
  
  <p>To exercise any of these rights, please contact us using the details in the "Contact Us" section.</p>
</section>

<style>
.retention-table {
  width: 100%;
  border-collapse: collapse;
  margin: 20px 0;
}
.retention-table th, .retention-table td {
  border: 1px solid #ddd;
  padding: 12px;
  text-align: left;
}
.retention-table th {
  background-color: #f5f5f5;
}
.retention-table tr:nth-child(even) {
  background-color: #f9f9f9;
}
</style>

<!-- Example data deletion request form -->
<div id="data-deletion-request" class="card">
  <div class="card-header">
    <h3>Data Deletion Request</h3>
    <p>Use this form to request deletion of your personal data in accordance with GDPR Article 17.</p>
  </div>
  <div class="card-body">
    <form id="deletion-request-form" action="/gdpr/delete-account" method="POST">
      <div class="form-group">
        <label for="email">Email Address</label>
        <input type="email" class="form-control" id="email" name="email" required>
      </div>
      
      <div class="form-group">
        <label for="reason">Reason for Deletion (optional)</label>
        <textarea class="form-control" id="reason" name="reason" rows="3"></textarea>
      </div>
      
      <div class="form-check mb-3">
        <input type="checkbox" class="form-check-input" id="confirm-deletion" required>
        <label class="form-check-label" for="confirm-deletion">
          I understand that this action is irreversible and will permanently delete my account and all associated data.
        </label>
      </div>
      
      <div class="form-group">
        <button type="submit" class="btn btn-danger">Request Account Deletion</button>
      </div>
    </form>
  </div>
  <div class="card-footer text-muted">
    <small>We will process your request within 30 days as required by GDPR. You will receive a confirmation email once your data has been deleted.</small>
  </div>
</div>

<!-- Example data export request form -->
<div id="data-export-request" class="card mt-4">
  <div class="card-header">
    <h3>Data Export Request</h3>
    <p>Request a copy of your personal data in a structured, commonly used, and machine-readable format.</p>
  </div>
  <div class="card-body">
    <form id="export-request-form" action="/gdpr/export-data" method="POST">
      <div class="form-group">
        <label for="export-email">Email Address</label>
        <input type="email" class="form-control" id="export-email" name="email" required>
      </div>
      
      <div class="form-group">
        <label for="format">Preferred Format</label>
        <select class="form-control" id="format" name="format">
          <option value="json">JSON</option>
          <option value="csv">CSV</option>
          <option value="xml">XML</option>
        </select>
      </div>
      
      <div class="form-group">
        <button type="submit" class="btn btn-primary">Request Data Export</button>
      </div>
    </form>
  </div>
  <div class="card-footer text-muted">
    <small>We will process your request within 30 days as required by GDPR. You will receive a download link via email once your data is ready.</small>
  </div>
</div>""",
                language="html"
            )
            
            if not issues:
                return self._create_result(
                    CheckStatus.PASSED,
                    "Data retention policies appear to be properly documented and implemented.",
                    solution=solution
                )
                
            return self._create_result(
                CheckStatus.FAILED,
                "Potential GDPR compliance issues with data retention policies:" + 
                "\n\n• " + "\n• ".join(issues),
                solution=solution
            )
            
        except Exception as e:
            return self._create_result(
                CheckStatus.ERROR,
                f"Error checking data retention policies: {str(e)}",
                {"error": str(e)}
            )
    
    def _check_privacy_policy(self) -> Dict[str, bool]:
        """Check privacy policy for retention information"""
        result = {
            'has_retention_section': False,
            'has_legal_basis': False,
            'has_retention_periods': False
        }
        
        try:
            # Look for privacy policy link
            privacy_links = self.driver.find_elements(
                By.XPATH, "//a[contains(translate(., 'PRIVACY', 'privacy'), 'privacy') or "
                         "contains(translate(., 'POLICY', 'policy'), 'policy')]"
            )
            
            if not privacy_links:
                return result
                
            # Click the first privacy policy link
            privacy_links[0].click()
            
            # Get page content
            page_source = self.driver.page_source.lower()
            
            # Check for retention-related terms
            retention_terms = [
                'retention', 'store data', 'keep information', 'data retention',
                'period of retention', 'how long we keep', 'data storage',
                'retain personal data', 'data minimization', 'storage limitation'
            ]
            
            # Check for legal basis terms
            legal_basis_terms = [
                'legal basis', 'legitimate interest', 'consent', 'contract',
                'legal obligation', 'vital interests', 'public task',
                'article 6', 'gdpr', 'general data protection regulation'
            ]
            
            # Check for specific retention periods
            retention_period_terms = [
                'months', 'years', 'days', 'weeks', 'until', 'as long as',
                'for the duration', 'after which', 'until the end',
                'retention period', 'storage period'
            ]
            
            result['has_retention_section'] = any(term in page_source for term in retention_terms)
            result['has_legal_basis'] = any(term in page_source for term in legal_basis_terms)
            result['has_retention_periods'] = any(term in page_source for term in retention_period_terms)
            
        except Exception:
            # If any error occurs, return the current result
            pass
            
        return result
    
    def _check_account_retention(self) -> Dict[str, bool]:
        """Check user account data retention"""
        result = {
            'has_retention_policy': False,
            'has_inactivity_period': False,
            'has_deletion_process': False
        }
        
        try:
            # Check for account-related pages
            account_links = self.driver.find_elements(
                By.XPATH, "//a[contains(translate(., 'ACCOUNT', 'account'), 'account') or "
                         "contains(translate(., 'PROFILE', 'profile'), 'profile') or "
                         "contains(translate(., 'SETTINGS', 'settings'), 'settings')]"
            )
            
            if account_links:
                # Click the first account link
                account_links[0].click()
                
                # Check for deletion options
                page_source = self.driver.page_source.lower()
                
                deletion_terms = [
                    'delete account', 'close account', 'deactivate account',
                    'remove account', 'account deletion', 'right to erasure',
                    'right to be forgotten', 'gdpr erasure', 'data deletion'
                ]
                
                result['has_deletion_process'] = any(term in page_source for term in deletion_terms)
                
                # Check for inactivity policy
                inactivity_terms = [
                    'inactive account', 'account inactivity', 'dormant account',
                    'account closure', 'account termination', 'account retention'
                ]
                
                result['has_inactivity_period'] = any(term in page_source for term in inactivity_terms)
                
                # Check for retention info in account settings
                retention_terms = [
                    'data retention', 'how long we keep', 'storage period',
                    'data storage', 'keep data', 'retention policy'
                ]
                
                result['has_retention_policy'] = any(term in page_source for term in retention_terms)
                
        except Exception:
            # If any error occurs, return the current result
            pass
            
        return result
    
    def _check_cookie_retention(self) -> Dict[str, bool]:
        """Check cookie retention information"""
        result = {
            'has_cookie_policy': False,
            'has_retention_info': False,
            'has_cookie_controls': False
        }
        
        try:
            # Look for cookie policy or banner
            cookie_selectors = [
                "//*[contains(translate(., 'COOKIE', 'cookie'), 'cookie')]",
                "//*[contains(translate(., 'TRACKING', 'tracking'), 'tracking')]",
                "//*[contains(translate(., 'PRIVACY', 'privacy'), 'privacy')]"
            ]
            
            cookie_elements = []
            for selector in cookie_selectors:
                elements = self.driver.find_elements(By.XPATH, selector)
                if elements:
                    cookie_elements.extend(elements)
            
            if not cookie_elements:
                return result
                
            # Click the first cookie-related element
            try:
                cookie_elements[0].click()
                
                # Check cookie policy content
                page_source = self.driver.page_source.lower()
                
                # Check for cookie policy section
                result['has_cookie_policy'] = any(term in page_source for term in ['cookie policy', 'cookies policy'])
                
                # Check for retention information
                retention_terms = [
                    'expires', 'duration', 'retention', 'how long', 'stored for',
                    'persistent', 'session cookie', 'lifetime', 'valid for'
                ]
                
                result['has_retention_info'] = any(term in page_source for term in retention_terms)
                
                # Check for cookie controls
                control_terms = [
                    'manage cookies', 'cookie settings', 'preferences',
                    'consent manager', 'privacy settings', 'opt-out',
                    'withdraw consent', 'change cookie settings'
                ]
                
                result['has_cookie_controls'] = any(term in page_source for term in control_terms)
                
            except Exception:
                # If clicking fails, try to find and click a close button
                try:
                    close_buttons = self.driver.find_elements(
                        By.XPATH, "//button[contains(., '×') or contains(., 'X') or "
                                 "contains(., 'Close') or contains(., 'close') or "
                                 "contains(., 'Accept') or contains(., 'accept')]"
                    )
                    if close_buttons:
                        close_buttons[0].click()
                except:
                    pass
                    
        except Exception:
            # If any error occurs, return the current result
            pass
            
        return result
    
    def _check_deletion_options(self) -> Dict[str, bool]:
        """Check for data deletion options"""
        result = {
            'has_deletion_option': False,
            'has_contact_method': False,
            'has_online_form': False
        }
        
        try:
            # Look for contact or support pages
            contact_links = self.driver.find_elements(
                By.XPATH, "//a[contains(translate(., 'CONTACT', 'contact'), 'contact') or "
                         "contains(translate(., 'SUPPORT', 'support'), 'support') or "
                         "contains(translate(., 'HELP', 'help'), 'help') or "
                         "contains(translate(., 'GDPR', 'gdpr'), 'gdpr')]"
            )
            
            if not contact_links:
                return result
                
            # Click the first contact link
            contact_links[0].click()
            
            # Check page content
            page_source = self.driver.page_source.lower()
            
            # Check for deletion-related terms
            deletion_terms = [
                'delete my data', 'right to erasure', 'right to be forgotten',
                'gdpr request', 'data deletion', 'remove my information',
                'forget me', 'erasure request', 'delete account', 'close account'
            ]
            
            result['has_deletion_option'] = any(term in page_source for term in deletion_terms)
            
            # Check for contact methods
            contact_terms = [
                'email', 'contact form', 'phone', 'address', 'write to us',
                'reach us', 'get in touch', 'customer service', 'support',
                'data protection officer', 'dpo', 'privacy contact'
            ]
            
            result['has_contact_method'] = any(term in page_source for term in contact_terms)
            
            # Check for online forms
            form_terms = [
                'form', 'request form', 'online form', 'submit a request',
                'data request form', 'gdpr form', 'privacy request',
                'data subject request', 'dsar form'
            ]
            
            result['has_online_form'] = any(term in page_source for term in form_terms)
            
        except Exception:
            # If any error occurs, return the current result
            pass
            
        return result
    
    def _check_export_options(self) -> Dict[str, bool]:
        """Check for data export options"""
        result = {
            'has_export_option': False,
            'has_download_option': False,
            'has_portability_info': False
        }
        
        try:
            # Check account settings or privacy settings
            settings_links = self.driver.find_elements(
                By.XPATH, "//a[contains(translate(., 'SETTINGS', 'settings'), 'settings') or "
                         "contains(translate(., 'ACCOUNT', 'account'), 'account') or "
                         "contains(translate(., 'PROFILE', 'profile'), 'profile') or "
                         "contains(translate(., 'PRIVACY', 'privacy'), 'privacy')]"
            )
            
            if not settings_links:
                return result
                
            # Click the first settings link
            settings_links[0].click()
            
            # Check page content
            page_source = self.driver.page_source.lower()
            
            # Check for export-related terms
            export_terms = [
                'export data', 'download data', 'data portability', 'get my data',
                'request data', 'data export', 'right to data portability',
                'download my information', 'export my data', 'gdpr export'
            ]
            
            result['has_export_option'] = any(term in page_source for term in export_terms)
            
            # Check for download options
            download_terms = [
                'download', 'export as', 'download my data', 'get a copy',
                'download archive', 'export to', 'download all', 'backup',
                'export history', 'download information'
            ]
            
            result['has_download_option'] = any(term in page_source for term in download_terms)
            
            # Check for portability information
            portability_terms = [
                'data portability', 'right to data portability', 'gdpr article 20',
                'transfer my data', 'port my data', 'move my data', 'take my data',
                'structured format', 'machine-readable', 'commonly used format'
            ]
            
            result['has_portability_info'] = any(term in page_source for term in portability_terms)
            
        except Exception:
            # If any error occurs, return the current result
            pass
            
        return result
