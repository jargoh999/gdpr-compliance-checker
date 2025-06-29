"""GDPR Cookie Consent Banner Checker"""
from typing import Dict, Any, List, Optional
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.common.by import By

from .base_checker import BaseChecker
from models.gdpr_check import GDPRCheckResult, CheckStatus, GDPRSolution

class CookieBannerChecker(BaseChecker):
    """Checks for the presence and compliance of cookie consent banners"""
    
    @property
    def check_id(self) -> str:
        return "cookie_banner_check"
    
    @property
    def check_name(self) -> str:
        return "Cookie Consent Banner Check"
    
    @property
    def severity(self) -> str:
        return "high"
    
    def _execute_check(self, url: str) -> GDPRCheckResult:
        """Check for the presence and compliance of a cookie consent banner"""
        banner_found = False
        banner_text = ""
        has_accept = False
        has_reject = False
        has_more_info = False
        
        # Common cookie banner selectors
        cookie_banner_selectors = [
            # General cookie banner selectors
            'div[class*="cookie"][class*="banner"], div[class*="cookie"][class*="notice"]',
            'div[id*="cookie"][id*="banner"], div[id*="cookie"][id*="notice"]',
            'div[class*="cc-banner"], div[class*="cookieconsent"]',
            'div[class*="gdpr"], div[class*="cc-window"]',
            
            # Specific consent management platforms
            '#cookie-law-info-bar, #onetrust-consent-sdk',
            '.cc-window, #cookieConsent, #cookie-notice',
            '#CybotCookiebotDialog, #cookie-notification',
            '#ccc-notify, #cookieChoiceInfo, #cookie-law',
            '#cookie-consent, #cookie-warning, #cookie_consent',
            '#cookieAccept, #accept-cookies, #acceptCookies',
            '#cookieAgree, #cookie_agree, #cookies-agree',
        ]
        
        # Check for banner presence
        banner = None
        for selector in cookie_banner_selectors:
            banner = self._find_element(By.CSS_SELECTOR, selector)
            if banner:
                banner_found = True
                banner_text = banner.text.lower()
                break
        
        if not banner_found:
            return self._create_result(
                status=CheckStatus.FAILED,
                description="No cookie consent banner found",
                solution=self._create_solution(
                    description="Implement a cookie consent banner that clearly informs users about cookie usage and obtains their consent before setting non-essential cookies.",
                    code_snippet="""
// Example implementation using vanilla JavaScript
function showCookieConsent() {
    const banner = document.createElement('div');
    banner.id = 'cookie-consent-banner';
    banner.style.cssText = `
        position: fixed;
        bottom: 0;
        left: 0;
        right: 0;
        background: #f8f9fa;
        padding: 15px;
        box-shadow: 0 -2px 10px rgba(0,0,0,0.1);
        z-index: 9999;
        display: flex;
        flex-wrap: wrap;
        gap: 10px;
        align-items: center;
        justify-content: space-between;
    `;
    
    banner.innerHTML = `
        <div style="flex: 1;">
            We use cookies to enhance your experience. By continuing to visit this site you agree to our use of cookies.
            <a href="/privacy-policy" style="color: #0d6efd;">Learn more</a>
        </div>
        <div style="display: flex; gap: 10px;">
            <button id="cookie-reject" style="padding: 5px 15px; background: #f8f9fa; border: 1px solid #dee2e6; border-radius: 4px; cursor: pointer;">
                Reject
            </button>
            <button id="cookie-accept" style="padding: 5px 15px; background: #0d6efd; color: white; border: none; border-radius: 4px; cursor: pointer;">
                Accept All
            </button>
        </div>
    `;
    
    document.body.appendChild(banner);
    
    // Add event listeners
    document.getElementById('cookie-accept').addEventListener('click', () => {
        // Set a cookie to remember the consent
        document.cookie = 'cookie_consent=true; path=/; max-age=31536000; SameSite=Lax';
        banner.style.display = 'none';
        // Load analytics/tracking scripts here
    });
    
    document.getElementById('cookie-reject').addEventListener('click', () => {
        // Set a cookie to remember the rejection
        document.cookie = 'cookie_consent=false; path=/; max-age=31536000; SameSite=Lax';
        banner.style.display = 'none';
    });
    
    // Check for existing consent
    if (document.cookie.includes('cookie_consent=')) {
        banner.style.display = 'none';
    }
}

// Show banner when DOM is loaded
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', showCookieConsent);
} else {
    showCookieConsent();
}
"""
                )
            )
        
        # Check for accept button
        accept_buttons = [
            'accept', 'agree', 'allow all', 'accept all', 'got it', 'i accept', 'consent',
            'accept cookies', 'agree & continue', 'i agree', 'okay', 'ok', 'close', 'continue',
            'confirm my choices', 'save preferences', 'accept all cookies'
        ]
        
        # Check for reject button
        reject_buttons = [
            'reject', 'decline', 'deny', 'necessary only', 'only necessary', 'reject all',
            'decline all', 'deny all', 'customize', 'settings', 'preferences', 'no thanks',
            'reject non-essential', 'decline non-essential', 'deny non-essential'
        ]
        
        # Check for more info link
        more_info_terms = [
            'learn more', 'more info', 'read more', 'cookie policy', 'privacy policy',
            'cookie settings', 'preferences', 'customize', 'manage cookies', 'cookie notice',
            'cookie information', 'how we use cookies', 'our cookie policy'
        ]
        
        # Check buttons and links in the banner
        if banner:
            buttons = banner.find_elements(By.TAG_NAME, 'button')
            links = banner.find_elements(By.TAG_NAME, 'a')
            
            for button in buttons:
                btn_text = button.text.lower()
                if any(term in btn_text for term in accept_buttons):
                    has_accept = True
                if any(term in btn_text for term in reject_buttons):
                    has_reject = True
            
            for link in links:
                link_text = link.text.lower()
                if any(term in link_text for term in more_info_terms):
                    has_more_info = True
                    break
        
        # Evaluate the banner compliance
        issues = []
        if not has_accept:
            issues.append("No clear 'Accept' button found")
        if not has_reject:
            issues.append("No clear 'Reject' or 'Decline' option found")
        if not has_more_info:
            issues.append("No link to more information about cookies")
        
        if not issues:
            return self._create_result(
                status=CheckStatus.PASSED,
                description="Cookie consent banner is properly implemented with accept, reject, and more info options.",
                details={
                    "banner_found": True,
                    "has_accept": has_accept,
                    "has_reject": has_reject,
                    "has_more_info": has_more_info
                }
            )
        else:
            return self._create_result(
                status=CheckStatus.FAILED,
                description=f"Cookie consent banner has the following issues: {', '.join(issues)}.",
                details={
                    "banner_found": True,
                    "has_accept": has_accept,
                    "has_reject": has_reject,
                    "has_more_info": has_more_info,
                    "issues": issues
                },
                solution=self._create_solution(
                    description="Ensure your cookie consent banner includes: 1) A clear 'Accept' button, 2) An equally visible 'Reject' button, and 3) A link to more information about cookie usage.",
                    code_snippet="""
// Example of a compliant cookie banner implementation
document.addEventListener('DOMContentLoaded', function() {
    // Check if consent was already given
    if (!document.cookie.includes('cookie_consent=')) {
        const banner = document.createElement('div');
        banner.id = 'gdpr-banner';
        banner.style.cssText = `
            position: fixed;
            bottom: 0;
            left: 0;
            right: 0;
            background: #ffffff;
            padding: 15px 20px;
            box-shadow: 0 -2px 10px rgba(0,0,0,0.1);
            z-index: 10000;
            font-family: Arial, sans-serif;
            font-size: 14px;
            line-height: 1.5;
        `;
        
        banner.innerHTML = `
            <div style="max-width: 1200px; margin: 0 auto; display: flex; flex-wrap: wrap; gap: 15px; align-items: center;">
                <div style="flex: 1; color: #333;">
                    We use cookies to enhance your experience on our website. Some are necessary for the site to work, 
                    while others help us improve your experience. By clicking "Accept All", you consent to our use of cookies.
                    <a href="/cookie-policy" style="color: #0066cc; text-decoration: underline; margin-left: 5px;">
                        Learn more
                    </a>
                </div>
                <div style="display: flex; gap: 10px; flex-wrap: wrap;">
                    <button id="gdpr-reject" style="
                        padding: 8px 16px;
                        background: #f8f9fa;
                        border: 1px solid #dee2e6;
                        border-radius: 4px;
                        cursor: pointer;
                        font-weight: 500;
                    ">
                        Reject All
                    </button>
                    <button id="gdpr-settings" style="
                        padding: 8px 16px;
                        background: #ffffff;
                        border: 1px solid #0d6efd;
                        color: #0d6efd;
                        border-radius: 4px;
                        cursor: pointer;
                        font-weight: 500;
                    ">
                        Cookie Settings
                    </button>
                    <button id="gdpr-accept" style="
                        padding: 8px 16px;
                        background: #0d6efd;
                        color: white;
                        border: none;
                        border-radius: 4px;
                        cursor: pointer;
                        font-weight: 500;
                    ">
                        Accept All
                    </button>
                </div>
            </div>
        `;
        
        document.body.appendChild(banner);
        
        // Add event listeners
        document.getElementById('gdpr-accept').addEventListener('click', function() {
            // Set consent cookie (30 days expiration)
            const expiryDate = new Date();
            expiryDate.setDate(expiryDate.getDate() + 30);
            document.cookie = `cookie_consent=all; expires=${expiryDate.toUTCString()}; path=/; SameSite=Lax`;
            
            // Load analytics/tracking scripts here
            loadTrackingScripts();
            
            // Remove banner
            banner.remove();
        });
        
        document.getElementById('gdpr-reject').addEventListener('click', function() {
            // Set rejection cookie (30 days expiration)
            const expiryDate = new Date();
            expiryDate.setDate(expiryDate.getDate() + 30);
            document.cookie = `cookie_consent=necessary; expires=${expiryDate.toUTCString()}; path=/; SameSite=Lax`;
            
            // Only load necessary cookies
            loadNecessaryCookies();
            
            // Remove banner
            banner.remove();
        });
        
        document.getElementById('gdpr-settings').addEventListener('click', function() {
            // Show cookie settings modal
            showCookieSettings();
        });
    }
});

function loadTrackingScripts() {
    // Load Google Analytics, Facebook Pixel, etc.
    console.log('Loading tracking scripts...');
}

function loadNecessaryCookies() {
    // Only load essential cookies
    console.log('Loading only necessary cookies...');
}

function showCookieSettings() {
    // Implementation for cookie settings modal
    console.log('Showing cookie settings...');
}
"""
                )
            )
