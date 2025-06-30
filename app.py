"""GDPR Compliance Checker - Main Application"""
import os
import sys
import time
import tempfile
import logging
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('app.log')
    ]
)
logger = logging.getLogger(__name__)

# Import streamlit first and configure it
import streamlit as st

# Set page config - must be the first Streamlit command
st.set_page_config(
    page_title="Health Tech Privacy Compliance",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'report' not in st.session_state:
    st.session_state.report = None
if 'report_generated' not in st.session_state:
    st.session_state.report_generated = False
if 'pdf_bytes' not in st.session_state:
    st.session_state.pdf_bytes = None

# Add the project root to the Python path
project_root = str(Path(__file__).parent.absolute())
if project_root not in sys.path:
    sys.path.append(project_root)

from services.web_driver import WebDriverService
from services.pdf_generator import PDFGenerator
from models.gdpr_check import GDPRReport, GDPRCheckResult

# Import all checkers from components
from components import (
    CookieBannerChecker,
    PrivacyPolicyChecker,
    DataCollectionFormChecker,
    DataSubjectRightsChecker,
    ThirdPartyTrackingChecker,
    SecureDataTransferChecker,
    DataRetentionChecker,
    InternationalTransferChecker,
    DataBreachChecker,
    ConsentManagementChecker
)

# Custom CSS
st.markdown("""
    <style>
        .main-header { 
            color: #1a5276;
            font-size: 2.5rem;
            font-weight: 700;
        }
        .sub-header {
            color: #2874a6;
            font-size: 1.5rem;
            font-weight: 600;
            margin-top: -10px;
            margin-bottom: 20px;
        }
        .success { color: #1e8449; }
        .warning { color: #d68910; }
        .error { color: #c0392b; }
        .check-card { 
            border-left: 5px solid #2980b9;
            padding: 15px 20px;
            margin: 15px 0;
            border-radius: 8px;
            background-color: #f8f9fa;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        }
        .stProgress > div > div > div > div {
            background-color: #2980b9;
        }
        .sidebar .sidebar-content {
            background-color: #f8f9fa;
        }
        .footer {
            margin-top: 50px;
            padding: 15px;
            text-align: center;
            color: #7f8c8d;
            font-size: 0.9rem;
        }
    </style>
""", unsafe_allow_html=True)

class GDPRComplianceChecker:
    """Main GDPR Compliance Checker Application"""
    
    def __init__(self):
        """Initialize the application"""
        self.web_driver_service = WebDriverService()
        self.pdf_generator = PDFGenerator()
        self.report = None
        
        # Initialize all checks
        self.checkers = []
        
    def initialize_checkers(self, driver):
        """Initialize all checker instances with the WebDriver"""
        self.checkers = [
            CookieBannerChecker(driver),
            PrivacyPolicyChecker(driver),
            DataCollectionFormChecker(driver),
            DataSubjectRightsChecker(driver),
            ThirdPartyTrackingChecker(driver),
            SecureDataTransferChecker(driver),
            DataRetentionChecker(driver),
            InternationalTransferChecker(driver),
            DataBreachChecker(driver),
            ConsentManagementChecker(driver)
        ]
    
    def run_checks(self, url: str) -> GDPRReport:
        """Run all GDPR compliance checks"""
        report = GDPRReport(url=url)
        
        try:
            # Initialize WebDriver and run checks
            with st.spinner("Initializing browser..."):
                driver = self.web_driver_service.get_driver()
                self.initialize_checkers(driver)
            
            # Create a container for progress updates
            progress_container = st.empty()
            
            # Run each check
            for i, checker in enumerate(self.checkers):
                try:
                    # Update progress
                    with progress_container.container():
                        st.info(f"Running check {i + 1} of {len(self.checkers)}: {checker.check_name}")
                        progress_bar = st.progress(0)
                    
                    # Run the check
                    result = checker.execute(url)
                    report.add_result(result)
                    
                    # Update progress
                    progress_bar.progress((i + 1) / len(self.checkers))
                    
                    # Small delay to prevent overwhelming the browser
                    time.sleep(1)
                    
                except Exception as e:
                    error_result = GDPRCheckResult(
                        check_id=checker.check_id,
                        check_name=checker.check_name,
                        status="ERROR",
                        severity="high",
                        description=f"Error executing check: {str(e)}",
                        details={"error": str(e)}
                    )
                    report.results.append(error_result)
                    
            # Clear progress container when done
            progress_container.empty()
            
        except Exception as e:
            st.error(f"An error occurred during the compliance check: {str(e)}")
            
        return report
    
    def generate_pdf_report(self, report: GDPRReport) -> bytes:
        """Generate a PDF report from the check results"""
        return self.pdf_generator.generate_report(report)
    
    def cleanup(self) -> None:
        """Clean up resources including WebDriver instances"""
        try:
            if hasattr(self, 'web_driver_service') and self.web_driver_service:
                self.web_driver_service.quit_driver()
                logger.info("Successfully cleaned up WebDriver resources")
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
    
def main():
    """Main application entry point"""
    # Main header with project title
    st.markdown("""
        <div style='text-align: center;'>
            <h1 class='main-header'>Privacy Concerns in Health Tech</h1>
            <h2 class='sub-header'>GDPR Compliance Evaluation for Nigerian Healthcare Platforms</h2>
        </div>
        <div style='margin: 20px 0; text-align: center; color: #5d6d7e; font-size: 1.1rem;'>
            A Technical Evaluation of Data Protection Compliance in Nigeria's Digital Health Sector
        </div>
        <hr style='border: 1px solid #e0e0e0; margin: 20px 0;'>
    """, unsafe_allow_html=True)
    
    # Sidebar
    st.sidebar.markdown("""
    <div style='background-color: #2980b9; color: white; padding: 15px; border-radius: 8px; margin-bottom: 20px;'>
        <h3 style='color: white; margin: 0;'>Health Tech Privacy Scanner</h3>
        <p style='margin: 5px 0 0 0; font-size: 0.9rem;'>GDPR & NDPR Compliance Tool</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.sidebar.markdown("### About This Tool")
    st.sidebar.markdown("""
    This tool evaluates healthcare websites and applications for compliance with:
    - **GDPR** (General Data Protection Regulation)
    - **NDPR** (Nigeria Data Protection Regulation)
    - Industry best practices for health data protection
    """)
    
    st.sidebar.markdown("### How to Use")
    st.sidebar.markdown("""
    1. Enter the health platform's URL
    2. Click 'Run Compliance Check'
    3. Review detailed compliance report
    4. Download PDF for documentation
    """)
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("### Compliance Focus Areas")
    st.sidebar.markdown("""
    - Patient consent management
    - Data collection & processing
    - Third-party data sharing
    - Security measures
    - Data subject rights
    - Data retention policies
    """)
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("""
    <div class='footer'>
        <p>Developed for Technical Evaluation</p>
        <p>© 2025 Emenike Health Tech Privacy Initiative</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Main content
    url = st.text_input("Enter website URL (e.g., https://example.com):", placeholder="https://")
    
    col1, col2 = st.columns([1, 3])
    with col1:
        run_check = st.button("🔍 Run Compliance Check")
    
    # Run compliance check
    if run_check and url:
        with st.spinner("Running GDPR compliance checks..."):
            try:
                # Initialize and run checks
                checker = GDPRComplianceChecker()
                st.session_state.report = checker.run_checks(url)
                st.session_state.report_generated = True
                
                # Generate PDF report
                try:
                    pdf_generator = PDFGenerator()
                    st.session_state.pdf_bytes = pdf_generator.generate_report(st.session_state.report)
                except Exception as e:
                    st.error(f"Error generating PDF report: {str(e)}")
                    st.session_state.pdf_bytes = None
                
                # Cleanup
                checker.cleanup()
                
                st.success("Compliance check completed!")
                
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
    
    # Display results if available
    if st.session_state.report and st.session_state.report_generated:
        report = st.session_state.report
        
        # Show summary
        st.header("📊 Compliance Summary")
        
        # Calculate summary metrics
        total_checks = len(report.results)
        passed = sum(1 for r in report.results if r.status == "PASSED")
        failed = sum(1 for r in report.results if r.status == "FAILED")
        warnings = sum(1 for r in report.results if r.status == "WARNING")
        errors = sum(1 for r in report.results if r.status == "ERROR")
        
        # Summary cards
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Checks", total_checks)
        col2.metric("Passed", f"{passed} ({passed/total_checks*100:.1f}%)" if total_checks > 0 else "N/A")
        col3.metric("Failed", f"{failed}", delta_color="inverse")
        col4.metric("Warnings", warnings)
        
        # Show detailed results
        st.header("🔍 Detailed Results")
        
        for result in report.results:
            # Determine status color
            if result.status == "PASSED":
                status_emoji = "✅"
                status_class = "success"
            elif result.status == "WARNING":
                status_emoji = "⚠️"
                status_class = "warning"
            elif result.status == "ERROR":
                status_emoji = "❌"
                status_class = "error"
            else:  # FAILED
                status_emoji = "❌"
                status_class = "error"
            
            # Create expandable section for each check
            with st.expander(f"{status_emoji} {result.check_name}", expanded=True):
                st.markdown(f"**Status:** <span class='{status_class}'>{result.status}</span>", unsafe_allow_html=True)
                st.markdown(f"**Severity:** {result.severity.capitalize()}")
                st.markdown(f"**Description:** {result.description}")
                
                # Show details if available
                if result.details:
                    st.markdown("**Details:**")
                    for key, value in result.details.items():
                        st.text(f"- {key}: {value}")
                
                # Show solution if available
                if hasattr(result, 'solution') and result.solution:
                    if st.button(f"🔧 Show Solution for {result.check_name}", key=f"btn_{result.check_id}"):
                        st.markdown("### Recommended Solution")
                        st.markdown(result.solution.description)
                        
                        if result.solution.code_snippet:
                            st.code(
                                result.solution.code_snippet,
                                language=result.solution.language
                            )
        
        # Show download button for the report if available
        if 'pdf_bytes' in st.session_state and st.session_state.get('pdf_bytes'):
            st.markdown("---")
            st.download_button(
                label="📥 Download Full Report (PDF)",
                data=st.session_state.pdf_bytes,
                file_name=f"gdpr-compliance-report-{url.replace('https://', '').replace('http://', '').replace('/', '_') if url else 'report'}.pdf",
                mime="application/pdf"
            )
        else:
            st.warning("No report available for download. Please run a compliance check first.")

if __name__ == "__main__":
    main()