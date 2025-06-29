"""GDPR Compliance Checker - Main Application"""
import os
import sys
import time
import tempfile
import streamlit as st
from typing import List, Dict, Any, Optional
from pathlib import Path

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

# Page config
st.set_page_config(
    page_title="Health Tech Privacy Compliance",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
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
        
        # Initialize WebDriver and run checks
        with st.spinner("Initializing browser..."):
            driver = self.web_driver_service.get_driver()
            self.initialize_checkers(driver)
        
        # Run each check
        for i, checker in enumerate(self.checkers):
            with st.spinner(f"Running {checker.check_name}..."):
                try:
                    # Show progress
                    progress = st.progress(0)
                    progress_text = st.empty()
                    progress_text.text(f"Checking: {checker.check_name}")
                    
                    # Run the check
                    result = checker.execute(url)
                    report.add_result(result)
                    
                    # Update progress
                    progress.progress((i + 1) / len(self.checkers))
                    
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
                    report.add_result(error_result)
                finally:
                    progress_text.empty()
        
        return report
    
    def generate_pdf_report(self, report: GDPRReport) -> bytes:
        """Generate a PDF report from the check results"""
        return self.pdf_generator.generate_report(report)
    
    def cleanup(self):
        """Clean up resources"""
        self.web_driver_service.quit_driver()

def initialize_session_state():
    """Initialize Streamlit session state variables"""
    if not hasattr(st, 'session_state'):
        st.session_state = {}
    
    # Initialize required session state variables
    defaults = {
        'report': None,
        'report_generated': False,
        'pdf_bytes': None,
        'initialized': True
    }
    
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

def main():
    """Main application entry point"""
    try:
        # Initialize session state first
        if not hasattr(st, 'session_state') or not st.session_state.get('initialized', False):
            initialize_session_state()
        
        # Ensure we have all required session state variables
        required_vars = ['report', 'report_generated', 'pdf_bytes']
        for var in required_vars:
            if var not in st.session_state:
                st.session_state[var] = None
        
        # Set page config at the start
        st.set_page_config(
            page_title="Health Tech Privacy Compliance",
            page_icon="🏥",
            layout="wide",
            initial_sidebar_state="expanded"
        )
        
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
    
    except Exception as e:
        st.error(f"Application initialization error: {str(e)}")
        st.stop()
    
    # Sidebar
    try:
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
    except Exception as e:
        st.sidebar.error(f"Error loading sidebar: {str(e)}")
    
    try:
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
    except Exception as e:
        st.sidebar.error(f"Error in sidebar content: {str(e)}")
        
    # Main content area with error handling
    try:
        # Main content area
        st.markdown("## Website Compliance Check")
        url = st.text_input("Enter website URL (e.g., https://example.com):", placeholder="https://", key="url_input")
        
        # Ensure we have a valid URL
        if not url:
            st.warning("Please enter a valid URL to begin the compliance check.")
            return
            
        col1, col2 = st.columns([1, 3])
        with col1:
            run_check = st.button("🔍 Run Compliance Check", key="run_check_btn")
            
        if not run_check:
            return
    
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
                        with st.spinner("Generating PDF report..."):
                            pdf_generator = PDFGenerator()
                            st.session_state.pdf_bytes = pdf_generator.generate_report(st.session_state.report)
                    except Exception as e:
                        st.error(f"Error generating PDF report: {str(e)}")
                        st.session_state.pdf_bytes = None
                    
                    # Cleanup resources
                    try:
                        checker.cleanup()
                    except Exception as e:
                        st.warning(f"Warning during cleanup: {str(e)}")
                    
                    st.success("Compliance check completed!")
                    
                except Exception as e:
                    st.error(f"An error occurred during compliance check: {str(e)}")
                    st.error("Please check the URL and try again. If the problem persists, the website might be blocking automated access.")
                    if st.session_state.get('report'):
                        st.session_state.report_generated = False
    except Exception as e:
        st.error(f"An unexpected error occurred: {str(e)}")
        st.stop()
        
        # Display results if available
        if st.session_state.get('report') and st.session_state.get('report_generated', False):
            try:
                report = st.session_state.report
                if not report or not hasattr(report, 'results') or not report.results:
                    st.warning("No compliance check results available. Please try running the check again.")
                    return
                
                # Show summary
                st.header("📊 Compliance Summary")
                
                # Calculate summary metrics
                total_checks = len(report.results)
                if total_checks == 0:
                    st.warning("No checks were performed. The report is empty.")
                    return
                    
                passed = sum(1 for r in report.results if r and hasattr(r, 'status') and r.status == "PASSED")
                failed = sum(1 for r in report.results if r and hasattr(r, 'status') and r.status == "FAILED")
                warnings = sum(1 for r in report.results if r and hasattr(r, 'status') and r.status == "WARNING")
                errors = sum(1 for r in report.results if r and hasattr(r, 'status') and r.status == "ERROR")
                
                # Ensure we have valid metrics
                if total_checks == 0:
                    st.error("No valid check results found in the report.")
                    return
        
                # Summary cards
                col1, col2, col3, col4 = st.columns(4)
                try:
                    col1.metric("Total Checks", total_checks)
                    col2.metric("Passed", f"{passed} ({passed/max(total_checks, 1)*100:.1f}%)" if total_checks > 0 else "N/A")
                    col3.metric("Failed", f"{failed}", delta_color="inverse")
                    col4.metric("Warnings", warnings)
                except Exception as e:
                    st.error(f"Error displaying summary metrics: {str(e)}")
                
                # Show detailed results
                st.header("🔍 Detailed Results")
                
                try:
                    for i, result in enumerate(report.results):
                        if not result or not hasattr(result, 'status'):
                            continue
                            
                        try:
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
                            with st.expander(f"{status_emoji} {getattr(result, 'check_name', f'Check {i+1}')}", expanded=True):
                                st.markdown(f"**Status:** <span class='{status_class}'>{getattr(result, 'status', 'UNKNOWN')}</span>", unsafe_allow_html=True)
                                st.markdown(f"**Severity:** {getattr(result, 'severity', 'medium').capitalize()}")
                                st.markdown(f"**Description:** {getattr(result, 'description', 'No description available')}")
                                
                                # Show details if available
                                if hasattr(result, 'details') and result.details:
                                    st.markdown("**Details:**")
                                    if isinstance(result.details, dict):
                                        for key, value in result.details.items():
                                            st.text(f"- {key}: {value}")
                                    else:
                                        st.text(str(result.details))
                                
                                # Show solution if available
                                if hasattr(result, 'solution') and result.solution:
                                    solution_key = f"solution_{i}_{hash(str(result))}"
                                    if st.button(f"🔧 Show Solution", key=solution_key):
                                        st.markdown("### Recommended Solution")
                                        st.markdown(getattr(result.solution, 'description', 'No solution available'))
                                        
                                        if hasattr(result.solution, 'code_snippet') and result.solution.code_snippet:
                                            st.code(
                                                result.solution.code_snippet,
                                                language=getattr(result.solution, 'language', 'python')
                                            )
                        except Exception as e:
                            st.error(f"Error displaying check result: {str(e)}")
                            continue
                except Exception as e:
                    st.error(f"Error processing results: {str(e)}")
                
                # Show download button for the report if available
                try:
                    if 'pdf_bytes' in st.session_state and st.session_state.get('pdf_bytes'):
                        st.markdown("---")
                        safe_url = url.replace('https://', '').replace('http://', '').replace('/', '_') if url else 'report'
                        st.download_button(
                            label="📥 Download Full Report (PDF)",
                            data=st.session_state.pdf_bytes,
                            file_name=f"gdpr-compliance-report-{safe_url[:100]}.pdf",
                            mime="application/pdf",
                            key="download_pdf"
                        )
                except Exception as e:
                    st.error(f"Error with PDF download: {str(e)}")
            except Exception as e:
                st.error(f"An error occurred while displaying results: {str(e)}")
                st.error("Please try running the compliance check again.")
                if 'report' in st.session_state:
                    st.session_state.report_generated = False
        else:
            st.warning("No report available for download. Please run a compliance check first.")

if __name__ == "__main__":
    main()