import os
from flask import Flask, render_template, request, jsonify, send_file
from datetime import datetime, timezone
import tldextract
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time
import io

app = Flask(__name__)

# Configuration
CHROMEDRIVER_PATH = '/usr/lib/chromium-browser/chromedriver'

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/audit', methods=['POST'])
def run_audit():
    url = request.form.get('url', '').strip()
    if not url:
        return jsonify({'error': 'URL is required'}), 400
    
    # Add https:// if not present
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    
    try:
        # Setup browser
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        
        # Initialize Chrome WebDriver
        driver = webdriver.Chrome(options=options)
        driver.get(url)
        time.sleep(5)

        # Run GDPR audit
        audit_results = run_gdpr_audit(driver, url)
        
        # Clean up
        driver.quit()
        
        # Generate report
        report = generate_report(audit_results)
        
        # Save report to a temporary file
        report_filename = f"GDPR_Audit_Report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(report_filename, 'w', encoding='utf-8') as f:
            f.write(report)
            
        return jsonify({
            'success': True,
            'report': report,
            'filename': report_filename
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/download/<path:filename>')
def download_file(filename):
    try:
        return send_file(
            filename,
            as_attachment=True,
            download_name=filename,
            mimetype='text/plain'
        )
    except Exception as e:
        return str(e), 404

def run_gdpr_audit(driver, url):
    """Run GDPR audit checks and return results."""
    audit = {
        'app_url': url,
        'timestamp': datetime.now(timezone.utc).strftime("%Y-%m-%dT%H%M%SZ"),
        'results': {},
        'logs': []
    }
    
    def log(step, result, detail=""):
        audit["results"][step] = result
        audit["logs"].append({
            "step": step,
            "result": result,
            "detail": detail,
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
    
    # Run checks
    try:
        # HTTPS check
        log("HTTPS Enabled", url.startswith("https://"))
        
        # Cookie banner check
        page_text = driver.page_source.lower()
        banner_present = any(k in page_text for k in ["cookie", "consent", "privacy"])
        log("Cookie Consent Banner", banner_present)
        
        # Privacy Policy Link
        links = driver.find_elements(By.TAG_NAME, "a")
        privacy_link = any("privacy" in link.text.lower() for link in links)
        log("Privacy Policy Link Found", privacy_link)
        
        # Data leakage
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "html.parser")
        leaks = [tag.strip() for tag in soup.find_all(string=True) if "@" in tag or "patient" in tag.lower()]
        log("Personal Data Leak Before Consent", bool(leaks), leaks[:5])
        
        # Third-party scripts
        scripts = driver.find_elements(By.TAG_NAME, "script")
        domain = tldextract.extract(url).registered_domain
        third_party = [s.get_attribute("src") for s in scripts if s.get_attribute("src") and domain not in s.get_attribute("src")]
        log("Third-Party Trackers Detected", bool(third_party), third_party[:5])
        
    except Exception as e:
        log("Error during audit", False, str(e))
    
    return audit

def generate_report(audit):
    """Generate a text report from audit results."""
    report = []
    report.append("="*80)
    report.append("GDPR AUDIT REPORT".center(80))
    report.append("="*80)
    report.append(f"\nApp URL: {audit['app_url']}")
    report.append(f"Test Date: {audit['timestamp']}")

    report.append("\nRESULTS SUMMARY")
    report.append("-"*15)
    for key, value in audit["results"].items():
        report.append(f"{key}: {value}")

    report.append("\nDETAILED LOGS")
    report.append("-"*12)
    for log_item in audit["logs"]:
        try:
            timestamp = log_item.get('timestamp', '')
            step = log_item.get('step', '')
            result = log_item.get('result', '')
            detail = log_item.get('detail', '')
            
            report.append(f"[{timestamp}] {step} -> {result}")
            if detail:
                report.append(f"Details: {detail}\n")
        except Exception as e:
            report.append(f"Error processing log item: {e}")
    
    return '\n'.join(report)

if __name__ == '__main__':
    app.run(debug=True)
