"""Third-Party Tracking Checker for GDPR Compliance"""
from typing import Dict, List, Optional, Set
import re
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.common.by import By
from urllib.parse import urlparse

from components.base_checker import BaseChecker
from models.gdpr_check import GDPRCheckResult, CheckStatus, GDPRSolution
from config.constants import SEVERITY_HIGH, SEVERITY_MEDIUM, SEVERITY_LOW

class ThirdPartyTrackingChecker(BaseChecker):
    """Checks for third-party tracking and cookies"""
    
    # Common third-party trackers and analytics
    TRACKER_DOMAINS = [
        # Analytics
        'google-analytics.com', 'googletagmanager.com', 'googleadservices.com',
        'doubleclick.net', 'facebook.com/tr', 'facebook.net',
        'analytics.twitter.com', 'linkedin.com/analytics',
        'hotjar.com', 'mouseflow.com', 'crazyegg.com',
        'mixpanel.com', 'amplitude.com', 'segment.com',
        
        # Advertising
        'googlesyndication.com', 'doubleclick.net',
        'ads-twitter.com', 'ads.linkedin.com', 'bing.com/ads',
        'pubmatic.com', 'rubiconproject.com', 'openx.net', 
        'criteo.com', 'taboola.com', 'outbrain.com',
        
        # Social widgets
        'addthis.com', 'sharethis.com', 'addtoany.com',
        
        # Tag managers
        'googletagmanager.com', 'tealium.com', 'ensighten.com',
        
        # CDNs that might host tracking scripts
        'ajax.googleapis.com', 'cdnjs.cloudflare.com', 'code.jquery.com'
    ]
    
    @property
    def check_id(self) -> str:
        return "third_party_tracking"
    
    @property
    def check_name(self) -> str:
        return "Third-Party Tracking Detection"
    
    def _execute_check(self, url: str) -> GDPRCheckResult:
        """Check for third-party trackers and cookies"""
        try:
            self.driver.get(url)
            
            # Try to get performance logs, but don't fail if not available
            domains = set()
            try:
                performance_logs = self.driver.get_log('performance')
                
                # Extract domains from network requests
                for log in performance_logs:
                    try:
                        message = log.get('message', '')
                        if 'Network.requestWillBeSent' in message or 'Network.responseReceived' in message:
                            url_match = re.search(r'"url":"([^"]+)"', message)
                            if url_match:
                                domain = self._extract_domain(url_match.group(1))
                                if domain and any(tracker in domain for tracker in self.TRACKER_DOMAINS):
                                    domains.add(domain)
                    except Exception as e:
                        continue
            except Exception as e:
                # If we can't get performance logs, just continue with other checks
                print(f"Warning: Could not get performance logs: {str(e)}")
                pass
            
            # Check for tracking cookies and scripts
            tracking_cookies = self._check_tracking_cookies()
            tracking_scripts = self._check_tracking_scripts()
            
            # Check privacy policy for third-party disclosures
            has_third_party_disclosure = self._check_third_party_disclosure()
            
            # Prepare results
            issues = []
            
            if domains:
                issues.append(f"Found {len(domains)} potential third-party trackers")
            
            if tracking_cookies:
                issues.append(f"Found {len(tracking_cookies)} tracking cookies")
            
            if tracking_scripts:
                issues.append(f"Found {len(tracking_scripts)} tracking scripts")
            
            if not has_third_party_disclosure:
                issues.append("No clear disclosure of third-party data sharing in privacy policy")
            
            if not issues:
                return self._create_result(
                    CheckStatus.PASSED,
                    "No obvious third-party trackers detected."
                )
            
            return self._create_result(
                CheckStatus.FAILED if issues else CheckStatus.PASSED,
                "Potential third-party tracking issues found:" + 
                ("\n\n• " + "\n• ".join(issues) if issues else "None"),
                solution=GDPRSolution(
                    description=("To ensure GDPR compliance with third-party trackers:\n\n"
                                "1. Disclose all third-party trackers in your privacy policy\n"
                                "2. Implement a cookie consent banner\n"
                                "3. Load third-party scripts only after obtaining consent\n"
                                "4. Use privacy-friendly analytics alternatives\n"
                                "5. Sign Data Processing Agreements (DPAs) with third parties"),
                    code_snippet="""<!-- Example of privacy-focused analytics with consent -->
<script>
// Only load analytics if consent is given
function loadAnalytics() {
  if (localStorage.getItem('analytics-consent') === 'true') {
    // Load Google Analytics with IP anonymization
    window.dataLayer = window.dataLayer || [];
    function gtag(){dataLayer.push(arguments);}
    gtag('js', new Date());
    gtag('config', 'YOUR-GA-ID', { 
      'anonymize_ip': true,
      'ad_storage': 'denied',
      'analytics_storage': 'denied'
    });
  }
}
</script>""",
                    language="html"
                )
            )
            
        except Exception as e:
            return self._create_result(
                CheckStatus.ERROR,
                f"Error checking for third-party trackers: {str(e)}",
                {"error": str(e)}
            )
    
    def _extract_domain(self, url: str) -> str:
        """Extract domain from URL"""
        try:
            domain = url.split('//')[-1].split('/')[0].replace('www.', '')
            return domain.split(':')[0].lower()
        except:
            return ""
    
    def _check_tracking_cookies(self) -> List[Dict]:
        """Check for tracking cookies"""
        try:
            cookies = self.driver.get_cookies()
            tracking_terms = [
                '_ga', '_gid', '_gat', '_fbp', 'fr', 'tr', 'sb', 'datr',
                'personalization_id', 'guest_id', '_hjid', '_ym_', 'yandexuid'
            ]
            return [c for c in cookies if any(t in c['name'].lower() for t in tracking_terms)]
        except:
            return []
    
    def _check_tracking_scripts(self) -> List[str]:
        """Check for tracking scripts"""
        try:
            scripts = self.driver.find_elements(By.TAG_NAME, 'script')
            tracking_terms = ['analytics', 'track', 'pixel', 'facebook', 'google-analytics', 'gtag', 'ga(']
            return [s.get_attribute('src') or s.get_attribute('innerHTML')[:100] 
                   for s in scripts 
                   if any(t in (s.get_attribute('src') or '').lower() or 
                         t in (s.get_attribute('innerHTML') or '').lower() 
                         for t in tracking_terms)]
        except:
            return []
    
    def _check_third_party_disclosure(self) -> bool:
        """Check privacy policy for third-party disclosures"""
        try:
            # Look for privacy policy link
            privacy_links = []
            for a in self.driver.find_elements(By.TAG_NAME, 'a'):
                try:
                    text = a.text.lower()
                    href = a.get_attribute('href', '').lower()
                    if 'privacy' in text or 'privacy' in href or 'gdpr' in text or 'gdpr' in href:
                        privacy_links.append(href)
                except:
                    continue
            
            # If no privacy policy found, return False
            if not privacy_links:
                return False
                
            # Check the first privacy policy link
            self.driver.get(privacy_links[0])
            page_text = self.driver.find_element(By.TAG_NAME, 'body').text.lower()
            
            # Look for third-party related terms
            third_party_terms = [
                'third party', 'third-party', 'service provider', 'data processor',
                'analytics', 'advertising', 'marketing', 'tracking', 'cookies',
                'google analytics', 'facebook pixel', 'social media', 'partners'
            ]
            
            return any(term in page_text for term in third_party_terms)
            
        except:
            return False
