
# import requests
# from selenium import webdriver
# from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.common.by import By
# from bs4 import BeautifulSoup
# import tldextract
# import time

# # --- Configuration ---
# URL = "https://myonecare.ng/"  # Replace with your app URL
# HEADLESS = True

# # --- Setup headless browser ---
# options = Options()
# if HEADLESS:
#     options.add_argument("--headless")
# options.add_argument("--disable-gpu")
# options.add_argument("--no-sandbox")
# driver = webdriver.Chrome(options=options)
# driver.get(URL)
# time.sleep(5)  # Wait for scripts to load

# # --- 1. HTTPS Check ---
# def check_https():
#     return URL.startswith("https://")

# # --- 2. Cookie Consent Banner ---
# def check_cookie_banner():
#     keywords = ["cookie", "consent", "privacy"]
#     page_text = driver.page_source.lower()
#     return any(k in page_text for k in keywords)

# # --- 3. Privacy Policy Link ---
# def check_privacy_policy():
#     links = driver.find_elements(By.TAG_NAME, "a")
#     return any("privacy" in link.text.lower() for link in links)

# # --- 4. Personal Data Leak Before Consent ---
# def check_data_leak():
#     response = requests.get(URL)
#     soup = BeautifulSoup(response.text, "html.parser")
#     leaks = []
#     for tag in soup.find_all(string=True):
#         if "@" in tag or "patient" in tag.lower() or "dob" in tag.lower():
#             leaks.append(tag.strip())
#     return leaks

# # --- 5. Third-Party Trackers ---
# def check_third_party_requests():
#     scripts = driver.find_elements(By.TAG_NAME, "script")
#     third_party = []
#     domain = tldextract.extract(URL).registered_domain
#     for s in scripts:
#         src = s.get_attribute("src")
#         if src and domain not in src:
#             third_party.append(src)
#     return third_party

# # --- 6. DSAR Endpoint Discovery ---
# def check_dsar_endpoints():
#     endpoints = ["/request-data", "/delete-account", "/export-data"]
#     found = []
#     for ep in endpoints:
#         try:
#             r = requests.get(URL + ep)
#             if r.status_code in [200, 401, 403]:
#                 found.append(ep)
#         except:
#             continue
#     return found

# # --- Run Tests ---
# print("🔍 GDPR Advanced Compliance Test")
# print(f"1. HTTPS Enabled: {check_https()}")
# print(f"2. Cookie Consent Banner Present: {check_cookie_banner()}")
# print(f"3. Privacy Policy Link Found: {check_privacy_policy()}")
# leaks = check_data_leak()
# print(f"4. Personal Data Leak Before Consent: {'Yes' if leaks else 'No'}")
# if leaks:
#     print("   ➤ Leaked Snippets:", leaks)
# third_party = check_third_party_requests()
# print(f"5. Third-Party Trackers Detected: {len(third_party)}")
# for t in third_party:
#     print(f"   ➤ {t}")
# dsar = check_dsar_endpoints()
# print(f"6. DSAR Endpoints Found: {dsar if dsar else 'None'}")

# driver.quit()
import requests, json, platform, tldextract, time
from datetime import datetime, timezone
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from fpdf import FPDF, FPDF_VERSION
import sys

# Use fpdf2 if available
try:
    from fpdf import FPDF as FPDF2
    FPDF = FPDF2
except ImportError:
    print("fpdf2 not found, falling back to fpdf", file=sys.stderr)

# CONFIG
URL = "https://www.ehr.com.ng/"  # TODO: Replace with your actual healthcare app URL
HEADLESS = True
TIMESTAMP = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H%M%SZ")
PDF_NAME = f"GDPR_Audit_Report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"

# Setup browser
options = Options()
if HEADLESS:
    options.add_argument("--headless")
driver = webdriver.Chrome(options=options)
driver.get(URL)
time.sleep(5)

# Prepare audit log
audit = {
    "app_url": URL,
    "timestamp": TIMESTAMP,
    "system": platform.platform(),
    "results": {},
    "logs": []
}
def log(step, result, detail=""):
    audit["results"][step] = result
    audit["logs"].append({
        "step": step,
        "result": result,
        "detail": detail,
        "timestamp": datetime.now(timezone.utc).isoformat()
    })

# === TESTS START ===
log("HTTPS Enabled", URL.startswith("https://"))

# Cookie banner
page_text = driver.page_source.lower()
banner_present = any(k in page_text for k in ["cookie", "consent", "privacy"])
log("Cookie Consent Banner", banner_present)

# Privacy Policy Link
links = driver.find_elements(By.TAG_NAME, "a")
privacy_link = any("privacy" in link.text.lower() for link in links)
log("Privacy Policy Link Found", privacy_link)

# Data leakage
response = requests.get(URL)
soup = BeautifulSoup(response.text, "html.parser")
leaks = [tag.strip() for tag in soup.find_all(string=True) if "@" in tag or "patient" in tag.lower()]
log("Personal Data Leak Before Consent", bool(leaks), leaks[:5])

# Third-party scripts
scripts = driver.find_elements(By.TAG_NAME, "script")
domain = tldextract.extract(URL).registered_domain
third_party = [s.get_attribute("src") for s in scripts if s.get_attribute("src") and domain not in s.get_attribute("src")]
log("Third-Party Trackers Detected", bool(third_party), third_party[:5])

# DSAR endpoints
endpoints = ["/request-data", "/delete-account", "/export-data"]
found = []
for ep in endpoints:
    try:
        r = requests.get(URL + ep)
        if r.status_code in [200, 401, 403]:
            found.append(ep)
    except:
        continue
log("DSAR Endpoints Found", bool(found), found)

driver.quit()

# === Text Report ===
# Since we're having issues with PDF generation, let's create a text report instead
report = []
report.append("="*80)
report.append("GDPR AUDIT REPORT".center(80))
report.append("="*80)
report.append(f"\nApp URL: {audit['app_url']}")
report.append(f"Test Date: {audit['timestamp']}")
report.append(f"System Info: {audit['system']}\n")

report.append("RESULTS SUMMARY")
report.append("-"*15)
for key, value in audit["results"].items():
    report.append(f"{key}: {value}")

report.append("\nDETAILED LOGS")
report.append("-"*12)
for log_item in audit["logs"]:
    try:
        # Clean up the text to avoid encoding issues
        def clean_text(text):
            return str(text).encode('ascii', 'replace').decode('ascii')
            
        timestamp = clean_text(log_item.get('timestamp', ''))
        step = clean_text(log_item.get('step', ''))
        result = clean_text(log_item.get('result', ''))
        detail = clean_text(log_item.get('detail', ''))
        
        report.append(f"[{timestamp}] {step} -> {result}")
        report.append(f"Details: {detail}\n")
    except Exception as e:
        report.append(f"Error processing log item: {e}")

# Save the report to a text file
TXT_NAME = PDF_NAME.replace('.pdf', '.txt')
with open(TXT_NAME, 'w', encoding='utf-8') as f:
    f.write('\n'.join(report))

print(f"✅ GDPR audit complete. Report saved as: {TXT_NAME}")
print("\n".join(report))