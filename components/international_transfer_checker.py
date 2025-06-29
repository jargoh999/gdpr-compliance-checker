"""International Data Transfer Checker for GDPR Compliance"""
from typing import Dict, List, Optional, Set, Tuple
import re
import socket
import dns.resolver
import whois
from urllib.parse import urlparse, urljoin
from datetime import datetime

from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.common.by import By

from components.base_checker import BaseChecker
from models.gdpr_check import GDPRCheckResult, CheckStatus, GDPRSolution
from config.constants import SEVERITY_HIGH, SEVERITY_MEDIUM, SEVERITY_LOW

class InternationalTransferChecker(BaseChecker):
    """Checks for GDPR compliance in international data transfers"""
    
    @property
    def check_id(self) -> str:
        return "international_transfer"
    
    @property
    def check_name(self) -> str:
        return "International Data Transfer"
    
    def _execute_check(self, url: str) -> GDPRCheckResult:
        """Check for international data transfer compliance"""
        try:
            # Ensure URL has a scheme
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url
                
            parsed_url = urlparse(url)
            domain = parsed_url.netloc
            
            # Check for international data transfers
            transfer_issues = self._check_data_transfers(domain)
            
            # Check privacy policy for transfer information
            policy_issues = self._check_privacy_policy()
            
            # Check for third-party services
            third_party_issues = self._check_third_party_services()
            
            # Check for data protection safeguards
            safeguard_issues = self._check_safeguards()
            
            # Combine all issues
            all_issues = transfer_issues + policy_issues + third_party_issues + safeguard_issues
            
            # Prepare solution with detailed guidance
            solution = GDPRSolution(
                description=(
                    "To ensure GDPR compliance for international data transfers:\n\n"
                    "1. Document all international data transfers in your privacy policy\n"
                    "2. Implement appropriate safeguards for transfers outside the EEA\n"
                    "3. Use Standard Contractual Clauses (SCCs) or other approved mechanisms\n"
                    "4. Conduct Transfer Impact Assessments (TIAs) for high-risk transfers\n"
                    "5. Obtain explicit consent for transfers to countries without adequacy decisions\n"
                    "6. Implement technical measures like encryption for all transferred data"
                ),
                code_snippet="""<!-- Example privacy policy section for international transfers -->
<section id="international-transfers">
  <h2>International Data Transfers</h2>
  
  <p>We may transfer, store, and process your personal data in countries other than the country in which you are resident. These countries may have data protection laws that are different from the laws of your country.</p>
  
  <h3>Our Approach to International Transfers</h3>
  <p>We ensure that any international transfers of your personal data are made in compliance with applicable data protection laws, including the General Data Protection Regulation (GDPR).</p>
  
  <h4>Transfers Within Our Corporate Group</h4>
  <p>We may transfer your personal data to other companies within our corporate group that are located in different countries. We ensure that such transfers are governed by our Binding Corporate Rules (BCRs) or other appropriate safeguards.</p>
  
  <h4>Transfers to Third Parties</h4>
  <p>When we transfer your personal data to third-party service providers or partners located outside the European Economic Area (EEA), we implement appropriate safeguards, such as:</p>
  
  <ul>
    <li><strong>Standard Contractual Clauses (SCCs):</strong> We use the European Commission's approved standard contractual clauses for transfers to countries not deemed to provide an adequate level of data protection.</li>
    <li><strong>Adequacy Decisions:</strong> We may transfer data to countries that have been deemed to provide an adequate level of protection for personal data by the European Commission.</li>
    <li><strong>Binding Corporate Rules (BCRs):</strong> For transfers within our corporate group, we have implemented BCRs that have been approved by relevant data protection authorities.</li>
    <li><strong>EU-U.S. Data Privacy Framework:</strong> For transfers to certified organizations in the United States, we rely on the EU-U.S. Data Privacy Framework where applicable.</li>
  </ul>
  
  <h4>Your Rights Regarding International Transfers</h4>
  <p>You have the right to:</p>
  <ul>
    <li>Request information about the safeguards we have in place for international data transfers</li>
    <li>Request a copy of the specific mechanisms used to protect your data during transfer</li>
    <li>Withdraw your consent for specific transfers where consent is the legal basis</li>
    <li>Lodge a complaint with a supervisory authority if you believe your data is not adequately protected</li>
  </ul>
  
  <h4>Countries Where We Process Data</h4>
  <p>We operate in the following regions and may transfer data to service providers in these locations:</p>
  
  <table class="transfer-table">
    <thead>
      <tr>
        <th>Country</th>
        <th>Purpose of Processing</th>
        <th>Legal Basis</th>
        <th>Safeguards in Place</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td>Germany</td>
        <td>Primary data center, customer support</td>
        <td>Performance of contract, Legitimate interest</td>
        <td>EEA country - Adequate protection</td>
      </tr>
      <tr>
        <td>United States</td>
        <td>Email marketing, analytics, customer support</td>
        <td>Consent, Legitimate interest</td>
        <td>SCCs, EU-U.S. Data Privacy Framework (where applicable)</td>
      </tr>
      <tr>
        <td>United Kingdom</td>
        <td>Backup storage, customer support</td>
        <td>Performance of contract, Legal obligation</td>
        <td>Adequacy decision (UK GDPR)</td>
      </tr>
      <tr>
        <td>India</td>
        <td>Software development, technical support</td>
        <td>Performance of contract</td>
        <td>SCCs with additional safeguards</td>
      </tr>
    </tbody>
  </table>
  
  <div class="alert alert-info">
    <h5>Additional Safeguards</h5>
    <p>In addition to the legal mechanisms mentioned above, we implement the following technical and organizational measures to protect your data:</p>
    <ul>
      <li>Encryption of data in transit using TLS 1.2+</li>
      <li>Pseudonymization of personal data where possible</li>
      <li>Strict access controls and authentication mechanisms</li>
      <li>Regular security audits of our service providers</li>
      <li>Data minimization principles applied to all transfers</li>
    </ul>
  </div>
  
  <p>For more information about our international data transfer practices or to request details about specific transfers, please contact our Data Protection Officer at <a href="mailto:dpo@example.com">dpo@example.com</a>.</p>
</section>

<style>
.transfer-table {
  width: 100%;
  border-collapse: collapse;
  margin: 20px 0;
  font-size: 0.9em;
}
.transfer-table th, .transfer-table td {
  border: 1px solid #ddd;
  padding: 12px;
  text-align: left;
  vertical-align: top;
}
.transfer-table th {
  background-color: #f5f5f5;
  font-weight: 600;
}
.transfer-table tr:nth-child(even) {
  background-color: #f9f9f9;
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
.alert h5 {
  margin-top: 0;
  color: #055160;
}
</style>

<!-- Example Transfer Impact Assessment (TIA) documentation snippet -->
<div class="tia-documentation">
  <h3>Transfer Impact Assessment (TIA)</h3>
  <p>For transfers to countries without an adequacy decision, we conduct a Transfer Impact Assessment that includes:</p>
  
  <div class="tia-section">
    <h4>1. Data Mapping</h4>
    <p>We document the types of personal data being transferred, categories of data subjects, processing purposes, and retention periods.</p>
  </div>
  
  <div class="tia-section">
    <h4>2. Recipient Assessment</h4>
    <p>We evaluate the recipient's data protection practices, security measures, and legal environment in the destination country.</p>
  </div>
  
  <div class="tia-section">
    <h4>3. Risk Assessment</h4>
    <p>We assess potential risks to data subjects' rights and freedoms, considering the legal framework and practices in the destination country.</p>
  </div>
  
  <div class="tia-section">
    <h4>4. Supplementary Measures</h4>
    <p>Where necessary, we implement additional safeguards such as encryption, pseudonymization, or contractual clauses to ensure an adequate level of protection.</p>
  </div>
  
  <div class="tia-section">
    <h4>5. Documentation</h4>
    <p>We maintain detailed records of our assessment and the safeguards implemented for each international transfer.</p>
  </div>
</div>

<style>
.tia-documentation {
  background-color: #f8f9fa;
  border-left: 4px solid #0d6efd;
  padding: 15px 20px;
  margin: 20px 0;
}
.tia-section {
  margin-bottom: 15px;
}
.tia-section h4 {
  margin-bottom: 5px;
  color: #0a58ca;
}
.tia-section p {
  margin-top: 0;
  color: #495057;
}
</style>

<!-- Example Standard Contractual Clauses (SCCs) reference -->
<div class="scc-info">
  <h3>Standard Contractual Clauses (SCCs)</h3>
  <p>For transfers to countries without an adequacy decision, we use the European Commission's Standard Contractual Clauses (SCCs) as a transfer mechanism. Our SCCs include:</p>
  
  <ul>
    <li>Module One: Controller to Controller transfers</li>
    <li>Module Two: Controller to Processor transfers</li>
    <li>Module Three: Processor to Sub-processor transfers</li>
    <li>Module Four: Processor to Controller transfers</li>
  </ul>
  
  <p>These clauses include additional safeguards where necessary to ensure that the level of protection of natural persons guaranteed by the GDPR is not undermined.</p>
  
  <p><a href="/legal/scc" class="btn btn-outline-primary">View Our Standard Contractual Clauses</a></p>
</div>

<style>
.scc-info {
  background-color: #f8f9fa;
  border-radius: 5px;
  padding: 20px;
  margin: 20px 0;
  border: 1px solid #dee2e6;
}
.scc-info h3 {
  margin-top: 0;
  color: #0a58ca;
}
.scc-info ul {
  padding-left: 20px;
}
.btn {
  display: inline-block;
  font-weight: 400;
  line-height: 1.5;
  text-align: center;
  text-decoration: none;
  vertical-align: middle;
  cursor: pointer;
  user-select: none;
  background-color: transparent;
  border: 1px solid transparent;
  padding: 0.375rem 0.75rem;
  font-size: 1rem;
  border-radius: 0.25rem;
  transition: color 0.15s ease-in-out, background-color 0.15s ease-in-out, 
              border-color 0.15s ease-in-out, box-shadow 0.15s ease-in-out;
}
.btn-outline-primary {
  color: #0d6efd;
  border-color: #0d6efd;
}
.btn-outline-primary:hover {
  color: #fff;
  background-color: #0d6efd;
  border-color: #0d6efd;
}
</style>""",
                language="html"
            )
            
            if not all_issues:
                return self._create_result(
                    CheckStatus.PASSED,
                    "No international data transfer compliance issues detected.",
                    solution=solution
                )
                
            return self._create_result(
                CheckStatus.FAILED,
                "Potential GDPR compliance issues with international data transfers:\n\n• " + 
                "\n• ".join(all_issues),
                solution=solution
            )
            
        except Exception as e:
            return self._create_result(
                CheckStatus.ERROR,
                f"Error checking international data transfer compliance: {str(e)}",
                {"error": str(e)}
            )
    
    def _check_data_transfers(self, domain: str) -> List[str]:
        """Check for international data transfers"""
        issues = []
        
        try:
            # Get domain information
            domain_info = whois.whois(domain)
            
            # Check if domain is registered in EEA
            if hasattr(domain_info, 'country') and domain_info.country:
                registration_country = domain_info.country if isinstance(domain_info.country, str) else domain_info.country[0]
                if registration_country.upper() not in self._get_eea_countries():
                    issues.append(f"Domain registered in non-EEA country: {registration_country}")
            
            # Check DNS servers
            dns_servers = set()
            try:
                answers = dns.resolver.resolve(domain, 'NS')
                for rdata in answers:
                    dns_servers.add(str(rdata.target).rstrip('.'))
            except:
                pass
                
            # Check if DNS servers are in EEA
            non_eea_dns = []
            for server in dns_servers:
                try:
                    ip = socket.gethostbyname(server)
                    country = self._get_country_from_ip(ip)
                    if country and country.upper() not in self._get_eea_countries():
                        non_eea_dns.append(f"{server} ({country})")
                except:
                    continue
                    
            if non_eea_dns:
                issues.append(f"DNS servers located outside EEA: {', '.join(non_eea_dns)}")
            
            # Check for external resources
            external_resources = self._find_external_resources()
            if external_resources:
                issues.append(f"Found {len(external_resources)} external resources that may involve international data transfers")
            
        except Exception as e:
            issues.append(f"Error checking data transfers: {str(e)}")
            
        return issues
    
    def _check_privacy_policy(self) -> List[str]:
        """Check privacy policy for transfer information"""
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
            
            # Check for transfer-related terms
            transfer_terms = [
                'international transfer', 'cross-border', 'outside eea',
                'outside eu', 'outside europe', 'third countries',
                'standard contractual clauses', 'sccs', 'binding corporate rules',
                'bcr', 'privacy shield', 'adequacy decision', 'data transfer',
                'transfer impact assessment', 'tia', 'article 44', 'article 45',
                'article 46', 'article 47', 'article 49', 'chapter v'
            ]
            
            if not any(term in page_source for term in transfer_terms):
                issues.append("No clear mention of international data transfers in privacy policy")
                
            # Check for specific safeguards
            safeguard_terms = [
                'standard contractual clauses', 'sccs', 'binding corporate rules',
                'bcr', 'adequacy decision', 'privacy shield', 'data privacy framework',
                'approved code of conduct', 'certification mechanism', 'derogations',
                'article 49', 'explicit consent', 'contractual necessity', 'legal claim',
                'public interest', 'vital interests', 'transfer impact assessment', 'tia'
            ]
            
            if not any(term in page_source for term in safeguard_terms):
                issues.append("No safeguards mentioned for international data transfers")
                
        except Exception as e:
            issues.append(f"Error checking privacy policy: {str(e)}")
            
        return issues
    
    def _check_third_party_services(self) -> List[str]:
        """Check for third-party services that may involve international transfers"""
        issues = []
        
        try:
            # Get all external resources
            external_resources = self._find_external_resources()
            
            # Check for common third-party services
            third_party_domains = set()
            
            for resource in external_resources:
                domain = urlparse(resource).netloc.lower()
                
                # Skip empty domains and same-origin
                if not domain or domain in self.driver.current_url:
                    continue
                    
                # Check for common third-party services
                third_party_indicators = [
                    'google-analytics.com', 'googletagmanager.com', 'facebook.com',
                    'doubleclick.net', 'youtube.com', 'vimeo.com', 'twitter.com',
                    'linkedin.com', 'hotjar.com', 'hubspot.com', 'salesforce.com',
                    'stripe.com', 'paypal.com', 'addthis.com', 'sharethis.com',
                    'cloudflare.com', 'amazonaws.com', 'azure.com', 'googleapis.com',
                    'facebook.net', 'gstatic.com', 'youtube-nocookie.com', 'vimeocdn.com',
                    'twimg.com', 'linkedin.com', 'licdn.com', 'hs-scripts.com',
                    'hs-banner.com', 'hsadspixel.net', 'hs-sites.com', 'hsforms.com',
                    'hsforms.net', 'hs-analytics.net', 'hsappstatic.net', 'hsapp.com',
                    'hs-sites.com', 'hubspot.net', 'hubspotusercontent.com', 'hsadspixel.net',
                    'hsforms.com', 'hsforms.net', 'hs-analytics.net', 'hsappstatic.net',
                    'hsapp.com', 'hs-sites.com', 'hubspot.net', 'hubspotusercontent.com',
                    'stripe.network', 'stripe.com', 'paypal.com', 'paypalobjects.com',
                    'paypal.me', 'paypal-communication.com', 'paypalcorp.com', 'paypal.me'
                ]
                
                if any(indicator in domain for indicator in third_party_indicators):
                    third_party_domains.add(domain)
            
            if third_party_domains:
                issues.append(f"Found {len(third_party_domains)} third-party services that may involve international data transfers: {', '.join(sorted(third_party_domains))}")
                
        except Exception as e:
            issues.append(f"Error checking third-party services: {str(e)}")
            
        return issues
    
    def _check_safeguards(self) -> List[str]:
        """Check for data protection safeguards"""
        issues = []
        
        try:
            # Check for security headers
            headers = self.driver.execute_script("""return Object.fromEntries(
                Object.entries(performance.getEntriesByType('navigation')[0].toJSON())
                .filter(([key]) => key.startsWith('response'))
                .map(([key, value]) => [key, value?.headers || {}])
            )""")
            
            # Check for security headers
            security_headers = [
                'strict-transport-security',
                'x-frame-options',
                'x-content-type-options',
                'content-security-policy',
                'x-xss-protection',
                'referrer-policy',
                'permissions-policy',
                'cross-origin-opener-policy',
                'cross-origin-embedder-policy',
                'cross-origin-resource-policy'
            ]
            
            missing_headers = []
            for header in security_headers:
                if not any(header in str(h).lower() for h in headers.values()):
                    missing_headers.append(header)
                    
            if missing_headers:
                issues.append(f"Missing recommended security headers: {', '.join(missing_headers)}")
                
            # Check for secure cookies
            cookies = self.driver.get_cookies()
            insecure_cookies = []
            
            for cookie in cookies:
                if not cookie.get('secure', False) and cookie.get('name') not in ['__host-', '__secure-']:
                    insecure_cookies.append(cookie['name'])
                    
            if insecure_cookies:
                issues.append(f"Found {len(insecure_cookies)} cookies without Secure flag: {', '.join(insecure_cookies[:5])}{'...' if len(insecure_cookies) > 5 else ''}")
                
        except Exception as e:
            issues.append(f"Error checking security measures: {str(e)}")
            
        return issues
    
    def _find_external_resources(self) -> Set[str]:
        """Find external resources loaded by the page"""
        external_resources = set()
        
        try:
            # Get all resources
            resources = self.driver.execute_script("""
                return window.performance.getEntriesByType('resource')
                    .map(r => r.name);
            """)
            
            # Get current domain
            current_domain = urlparse(self.driver.current_url).netloc.lower()
            
            # Find external resources
            for resource in resources:
                try:
                    domain = urlparse(resource).netloc.lower()
                    if domain and domain != current_domain and not domain.endswith('.' + current_domain):
                        external_resources.add(resource)
                except:
                    continue
                    
        except:
            pass
            
        return external_resources
    
    def _get_country_from_ip(self, ip: str) -> Optional[str]:
        """Get country from IP address"""
        try:
            import geoip2.database
            import os
            
            # Try to find GeoLite2 database
            db_paths = [
                '/usr/share/GeoIP/GeoLite2-Country.mmdb',
                '/usr/local/share/GeoIP/GeoLite2-Country.mmdb',
                os.path.expanduser('~/.local/share/GeoIP/GeoLite2-Country.mmdb'),
                os.path.join(os.path.dirname(__file__), 'GeoLite2-Country.mmdb')
            ]
            
            for db_path in db_paths:
                if os.path.exists(db_path):
                    with geoip2.database.Reader(db_path) as reader:
                        response = reader.country(ip)
                        return response.country.iso_code
                        
            # Fallback to online service if database not found
            try:
                import requests
                response = requests.get(f'https://ipapi.co/{ip}/country/', timeout=5)
                if response.status_code == 200 and response.text.strip():
                    return response.text.strip()
            except:
                pass
                
        except ImportError:
            pass
            
        return None
    
    def _get_eea_countries(self) -> Set[str]:
        """Get list of EEA countries"""
        return {
            'AT', 'BE', 'BG', 'HR', 'CY', 'CZ', 'DK', 'EE', 'FI', 'FR',
            'DE', 'GR', 'HU', 'IS', 'IE', 'IT', 'LI', 'LV', 'LT', 'LU',
            'MT', 'NL', 'NO', 'PL', 'PT', 'RO', 'SK', 'SI', 'ES', 'SE',
            'GB', 'UK', 'CH', 'UK'  # Including UK and CH for completeness
        }
