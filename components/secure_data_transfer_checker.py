"""Secure Data Transfer Checker for GDPR Compliance"""
from typing import Dict, List, Optional
import re
import ssl
import socket
import requests
from urllib.parse import urlparse
from datetime import datetime
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.common.by import By

from components.base_checker import BaseChecker
from models.gdpr_check import GDPRCheckResult, CheckStatus, GDPRSolution
from config.constants import SEVERITY_HIGH, SEVERITY_MEDIUM, SEVERITY_LOW

class SecureDataTransferChecker(BaseChecker):
    """Checks for secure data transfer mechanisms"""
    
    @property
    def check_id(self) -> str:
        return "secure_data_transfer"
    
    @property
    def check_name(self) -> str:
        return "Secure Data Transfer"
    
    def _execute_check(self, url: str) -> GDPRCheckResult:
        """Check for secure data transfer mechanisms"""
        try:
            # Ensure URL has a scheme
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url
                
            parsed_url = urlparse(url)
            domain = parsed_url.netloc
            
            # Check if HTTPS is enforced
            https_issues = self._check_https_enforcement(url)
            
            # Check SSL/TLS configuration
            ssl_issues = self._check_ssl_configuration(domain)
            
            # Check for mixed content
            mixed_content_issues = self._check_mixed_content()
            
            # Check HSTS header
            hsts_issues = self._check_hsts_header(url)
            
            # Check for secure forms
            form_issues = self._check_form_security()
            
            # Prepare results
            issues = []
            issues.extend(https_issues)
            issues.extend(ssl_issues)
            issues.extend(mixed_content_issues)
            issues.extend(hsts_issues)
            issues.extend(form_issues)
            
            if not issues:
                return self._create_result(
                    CheckStatus.PASSED,
                    "All data transfers appear to be secure and GDPR compliant."
                )
            
            return self._create_result(
                CheckStatus.FAILED if issues else CheckStatus.PASSED,
                "Potential secure data transfer issues found:" + 
                ("\n\n• " + "\n• ".join(issues) if issues else "None"),
                solution=GDPRSolution(
                    description=("To ensure secure data transfer and GDPR compliance:\n\n"
                                "1. Enforce HTTPS across your entire website\n"
                                "2. Use strong SSL/TLS protocols and ciphers\n"
                                "3. Implement HSTS (HTTP Strict Transport Security)\n"
                                "4. Ensure all forms submit over HTTPS\n"
                                "5. Fix any mixed content issues\n"
                                "6. Keep SSL certificates up to date"),
                    code_snippet="""<!-- Example of secure form submission -->
<form action="https://yourdomain.com/process" method="POST">
  <!-- Always use HTTPS in form actions -->
  <input type="text" name="username" required>
  <input type="password" name="password" required>
  <input type="submit" value="Submit">
</form>

<!-- Example of secure iframe -->
<iframe src="https://secure-payment.example.com" 
        sandbox="allow-forms allow-scripts allow-same-origin" 
        style="border: 0; width: 100%; min-height: 500px;">
</iframe>

<!-- Example of Content Security Policy (CSP) header -->
<!-- 
Content-Security-Policy: 
  default-src 'self';
  script-src 'self' 'unsafe-inline' https://trusted.cdn.com;
  style-src 'self' 'unsafe-inline';
  img-src 'self' data: https://trusted.cdn.com;
  font-src 'self' https://fonts.gstatic.com;
  connect-src 'self' https://api.yourdomain.com;
  frame-ancestors 'none';
  form-action 'self';
  base-uri 'self';
  object-src 'none';
  upgrade-insecure-requests;
  block-all-mixed-content;
-->
""",
                    language="html"
                )
            )
            
        except Exception as e:
            return self._create_result(
                CheckStatus.ERROR,
                f"Error checking secure data transfer: {str(e)}",
                {"error": str(e)}
            )
    
    def _check_https_enforcement(self, url: str) -> List[str]:
        """Check if HTTPS is properly enforced"""
        issues = []
        
        # Try HTTP version to check for redirect to HTTPS
        http_url = url.replace('https://', 'http://', 1)
        try:
            response = requests.get(http_url, allow_redirects=False, timeout=10)
            if response.status_code == 301 or response.status_code == 302:
                if not response.headers.get('Location', '').startswith('https://'):
                    issues.append("HTTP to HTTPS redirect is not properly configured")
            elif response.status_code == 200:
                issues.append("Website is accessible via HTTP without redirect to HTTPS")
        except:
            pass
            
        return issues
    
    def _check_ssl_configuration(self, domain: str) -> List[str]:
        """Check SSL/TLS configuration"""
        issues = []
        
        try:
            context = ssl.create_default_context()
            with socket.create_connection((domain, 443)) as sock:
                with context.wrap_socket(sock, server_hostname=domain) as ssock:
                    cert = ssock.getpeercert()
                    
                    # Check certificate expiration
                    expiry_date = datetime.strptime(cert['notAfter'], '%b %d %H:%M:%S %Y %Z')
                    if (expiry_date - datetime.utcnow()).days < 30:
                        issues.append(f"SSL certificate expires soon: {expiry_date.strftime('%Y-%m-%d')}")
                    
                    # Check protocol version
                    protocol = ssock.version()
                    if protocol in ['SSLv2', 'SSLv3', 'TLSv1', 'TLSv1.1']:
                        issues.append(f"Insecure protocol version detected: {protocol}")
                    
                    # Check certificate hostname
                    try:
                        ssl.match_hostname(cert, domain)
                    except ssl.CertificateError:
                        issues.append("Certificate hostname mismatch")
                        
        except ssl.SSLError as e:
            issues.append(f"SSL/TLS error: {str(e)}")
        except Exception as e:
            issues.append(f"Error checking SSL configuration: {str(e)}")
            
        return issues
    
    def _check_mixed_content(self) -> List[str]:
        """Check for mixed content issues"""
        issues = []
        
        try:
            # Check for mixed content in page source
            page_source = self.driver.page_source.lower()
            insecure_urls = re.findall(r'src=["\']http://[^"\']+', page_source)
            
            # Filter out common false positives
            ignored_domains = ['localhost', '127.0.0.1', '::1', '0.0.0.0']
            insecure_urls = [url for url in insecure_urls 
                           if not any(domain in url for domain in ignored_domains)]
            
            if insecure_urls:
                issues.append(f"Found {len(insecure_urls)} potential mixed content resources")
                
        except Exception as e:
            issues.append(f"Error checking for mixed content: {str(e)}")
            
        return issues
    
    def _check_hsts_header(self, url: str) -> List[str]:
        """Check HSTS header configuration"""
        issues = []
        
        try:
            response = requests.head(url, allow_redirects=True, timeout=10)
            hsts_header = response.headers.get('Strict-Transport-Security', '').lower()
            
            if not hsts_header:
                issues.append("HSTS header is missing")
            else:
                if 'max-age=0' in hsts_header:
                    issues.append("HSTS max-age is set to 0, which disables HSTS")
                elif 'max-age' not in hsts_header:
                    issues.append("HSTS max-age is missing")
                elif 'includesubdomains' not in hsts_header:
                    issues.append("HSTS should include subdomains (includeSubDomains)")
                if 'preload' not in hsts_header:
                    issues.append("Consider adding 'preload' to HSTS header for better security")
                    
        except Exception as e:
            issues.append(f"Error checking HSTS header: {str(e)}")
            
        return issues
    
    def _check_form_security(self) -> List[str]:
        """Check form security"""
        issues = []
        
        try:
            forms = self.driver.find_elements(By.TAG_NAME, 'form')
            insecure_forms = []
            
            for i, form in enumerate(forms, 1):
                action = form.get_attribute('action') or ''
                method = form.get_attribute('method') or 'get'
                
                # Check if form action is secure
                if action.startswith('http://'):
                    insecure_forms.append(f"Form {i}: Insecure form action (HTTP)")
                
                # Check if login/password form uses POST
                if (method.lower() == 'get' and 
                   (form.find_elements(By.XPATH(".//input[@type='password']")) or 
                    form.find_elements(By.XPATH(".//*[contains(translate(., 'PASSWORD', 'password'), 'password')]")))):
                    insecure_forms.append(f"Form {i}: Password form uses GET method")
            
            issues.extend(insecure_forms)
            
        except Exception as e:
            issues.append(f"Error checking form security: {str(e)}")
            
        return issues
