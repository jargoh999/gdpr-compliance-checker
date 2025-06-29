"""GDPR Compliance Checker Constants"""

# Severity Constants (module level for direct import)
SEVERITY_HIGH = "High"
SEVERITY_MEDIUM = "Medium"
SEVERITY_LOW = "Low"
SEVERITY_INFO = "Information"

# GDPR Check Categories
class CheckCategory:
    SECURITY = "Security"
    PRIVACY = "Privacy"
    COOKIES = "Cookies"
    FORMS = "Forms"
    BANNERS = "Banners"

# Severity Levels
class Severity:
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"
    INFO = "Information"

# Check Status
class Status:
    PASSED = "PASSED"
    FAILED = "FAILED"
    WARNING = "WARNING"
    INFO = "INFORMATION"

# Browser Configuration
BROWSER_OPTIONS = {
    'headless': True,
    'disable-gpu': True,
    'no-sandbox': True,
    'disable-dev-shm-usage': True,
    'window-size': '1920,1080',
}

# PDF Configuration
PDF_CONFIG = {
    'font_family': 'Arial',
    'title_font_size': 16,
    'header_font_size': 12,
    'body_font_size': 10,
    'normal_font_size': 10,  # Default normal font size
    'code_font_size': 8,
    'margin': 15,
    'line_height': 5,
    'page_width': 210,  # A4 width in mm
    'page_height': 297,  # A4 height in mm
}

# Common Keywords for Detection
KEYWORDS = {
    'privacy': ['privacy', 'gdpr', 'data protection', 'ccpa', 'lgpd'],
    'cookies': ['cookie', 'consent', 'tracking', 'opt-'],
    'security': ['https', 'ssl', 'tls', 'encryption', 'secure'],
    'forms': ['form', 'newsletter', 'signup', 'register', 'contact'],
}

# Default Check Timeout (in seconds)
DEFAULT_TIMEOUT = 30
