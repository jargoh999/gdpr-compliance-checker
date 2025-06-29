"""PDF Generation Service for GDPR Compliance Reports"""
from typing import Dict, Any, List, Optional, Union
from datetime import datetime
from fpdf import FPDF
import base64
import re
import string
import os

from config.constants import PDF_CONFIG
from models.gdpr_check import GDPRReport, CheckStatus, GDPRSolution

class PDFGenerator:
    """Service for generating GDPR compliance reports in PDF format"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the PDF generator
        
        Args:
            config: Configuration overrides for PDF generation
        """
        self.config = {**PDF_CONFIG, **(config or {})}
        
        # Force ASCII-only mode to avoid font issues
        self.config['ascii_only'] = True
    
    def _clean_text(self, text: Any) -> str:
        """Clean text to ensure it only contains printable ASCII characters
        
        Args:
            text: Input text that may contain non-ASCII characters or be a non-string type
            
        Returns:
            str: Cleaned text with non-ASCII characters replaced
        """
        if text is None:
            return ''
            
        # Handle bytearray and bytes objects
        if isinstance(text, (bytearray, bytes)):
            try:
                text = text.decode('utf-8', errors='replace')
            except Exception:
                text = str(text, errors='replace')
        # Convert any other non-string type to string
        elif not isinstance(text, str):
            text = str(text)
            
        # Replace common problematic characters
        replacements = {
            '•': '-',
            '—': '--',
            '–': '-',
            '“': '"',
            '”': '"',
            '‘': "'",
            '’': "'"
        }
        
        # First replace known problematic characters
        for old, new in replacements.items():
            text = text.replace(old, new)
            
        # Then replace any remaining non-ASCII characters
        cleaned = []
        for char in text:
            if ord(char) < 128 and char in string.printable:
                cleaned.append(char)
            else:
                cleaned.append('?')
                
        return ''.join(cleaned)
    
    def _safe_multi_cell(self, pdf: FPDF, w: float = 0, h: float = 10, txt: Any = '', border = 0, 
                        align = 'J', fill = False, max_line_height = None, 
                        split_only = False, link = None) -> None:
        """Wrapper around multi_cell that ensures text is clean"""
        if txt is None:
            txt = ''
        try:
            cleaned_text = self._clean_text(txt)
            pdf.multi_cell(
                w=w, 
                h=h, 
                txt=cleaned_text,
                border=border, 
                align=align, 
                fill=fill, 
                max_line_height=max_line_height,
                split_only=split_only,
                link=link
            )
        except Exception as e:
            # Log the error and try with empty string
            print(f"Error in _safe_multi_cell: {str(e)}")
            pdf.multi_cell(w=w, h=h, txt='[Content not displayable]', border=border, align=align)
        
    def _safe_cell(self, pdf: FPDF, w: float = 0, h: float = 10, txt: Any = '', 
                 border = 0, ln = 0, align = '', fill = False, link = '') -> None:
        """Wrapper around cell that ensures text is clean"""
        if txt is None:
            txt = ''
        try:
            cleaned_text = self._clean_text(txt)
            pdf.cell(
                w=w, 
                h=h, 
                txt=cleaned_text,
                border=border, 
                ln=ln, 
                align=align, 
                fill=fill, 
                link=link
            )
        except Exception as e:
            # Log the error and try with empty string
            print(f"Error in _safe_cell: {str(e)}")
            pdf.cell(w=w, h=h, txt='[Error]', border=border, ln=ln, align=align)
    
    def generate_report(self, report: GDPRReport) -> bytes:
        """Generate a PDF report from a GDPRReport object
        
        Args:
            report: The GDPR compliance report to convert to PDF
            
        Returns:
            bytes: PDF content as bytes
        """
        pdf = FPDF(unit='mm', format='A4')
        
        # Set document metadata
        pdf.set_title(self._clean_text(f'GDPR Compliance Report - {report.url}'))
        pdf.set_author('GDPR Compliance Checker')
        pdf.set_creator('GDPR Compliance Checker')
        pdf.set_subject(self._clean_text(f'GDPR Compliance Report for {report.url}'))
        
        try:
            # Add cover page
            self._add_cover_page(pdf, report)
            
            # Add table of contents
            self._add_table_of_contents(pdf, report)
            
            # Add detailed findings
            self._add_detailed_findings(pdf, report)
            
            # Add solutions appendix
            self._add_solutions_appendix(pdf, report)
            
            # Get the PDF content
            result = pdf.output(dest='S')
            
            # Handle both string and bytes/bytearray cases
            if isinstance(result, (bytes, bytearray)):
                return bytes(result)
            elif isinstance(result, str):
                return result.encode('latin-1')
            else:
                return str(result).encode('latin-1')
                
        except Exception as e:
            print(f"Error generating PDF: {str(e)}")
            # Return an empty PDF with error message
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font('Arial', 'B', 16)
            pdf.cell(0, 10, 'Error Generating Report', 0, 1)
            pdf.set_font('Arial', '', 12)
            pdf.multi_cell(0, 10, f'An error occurred while generating the PDF report: {str(e)[:200]}')
            return pdf.output(dest='S').encode('latin-1')
    
    def _add_cover_page(self, pdf: FPDF, report: GDPRReport) -> None:
        """Add a cover page to the PDF with health tech privacy theme
        
        Args:
            pdf: FPDF instance
            report: GDPR report data
        """
        # Add first page
        pdf.add_page()
        
        # Set background color for header
        pdf.set_fill_color(13, 60, 85)  # Dark blue
        pdf.rect(0, 0, 210, 40, 'F')
        
        # Add title
        pdf.set_font(self.config['font_family'], 'B', 24)
        pdf.set_text_color(255, 255, 255)  # White text
        pdf.set_xy(10, 15)
        self._safe_cell(pdf, 0, 10, 'GDPR Compliance Report', 0, 1, 'L')
        
        # Add subtitle
        pdf.set_font(self.config['font_family'], 'I', 12)
        pdf.set_text_color(200, 200, 200)  # Light gray
        pdf.set_xy(10, 25)
        self._safe_cell(pdf, 0, 10, 'Health Tech Privacy Assessment', 0, 1, 'L')
        
        # Add assessment details
        pdf.set_font(self.config['font_family'], '', 12)
        pdf.set_text_color(0, 0, 0)  # Black text
        pdf.ln(30)
        
        # Website URL
        pdf.set_font(self.config['font_family'], 'B', 12)
        self._safe_cell(pdf, 40, 10, 'Website:', 0, 0)
        pdf.set_font(self.config['font_family'], '', 12)
        self._safe_cell(pdf, 0, 10, report.url, 0, 1)
        
        # Assessment date
        pdf.set_font(self.config['font_family'], 'B', 12)
        self._safe_cell(pdf, 40, 10, 'Assessment Date:', 0, 0)
        pdf.set_font(self.config['font_family'], '', 12)
        self._safe_cell(pdf, 0, 10, report.timestamp.strftime('%Y-%m-%d %H:%M:%S'), 0, 1)
        
        # Add summary metrics
        pdf.ln(15)
        pdf.set_font(self.config['font_family'], 'B', 14)
        self._safe_cell(pdf, 0, 10, 'Summary', 0, 1, 'L')
        
        # Calculate metrics
        total_checks = len(report.results)
        passed = sum(1 for r in report.results if r.status == CheckStatus.PASSED)
        failed = sum(1 for r in report.results if r.status == CheckStatus.FAILED)
        warning = sum(1 for r in report.results if r.status == CheckStatus.WARNING)
        
        # Add metrics in a 2x2 grid
        pdf.set_font(self.config['font_family'], '', 10)
        self._add_metric(pdf, 'Total Checks', str(total_checks), (13, 60, 85))
        self._add_metric(pdf, 'Passed', str(passed), (40, 167, 69))  # Green
        pdf.ln(15)
        self._add_metric(pdf, 'Failed', str(failed), (220, 53, 69))   # Red
        self._add_metric(pdf, 'Warnings', str(warning), (255, 193, 7)) # Yellow
        
        # Add footer
        pdf.set_font(self.config['font_family'], 'I', 8)
        pdf.set_text_color(100, 100, 100)
        pdf.set_y(-15)
        self._safe_cell(pdf, 0, 10, 'Generated by GDPR Compliance Checker', 0, 0, 'C')
    
    def _draw_rounded_rect(self, pdf, x, y, w, h, r, color):
        """Draw a standard rectangle with fill color
        
        Note: Using standard rectangle instead of rounded rectangle for compatibility
        with the base FPDF library.
        """
        pdf.set_fill_color(*color)
        pdf.rect(x, y, w, h, 'F')
    
    def _add_table_of_contents(self, pdf: FPDF, report: GDPRReport) -> None:
        """Add a styled table of contents to the PDF
        
        Args:
            pdf: FPDF instance
            report: GDPR report data
        """
        pdf.add_page()
        
        # Add header with blue background
        pdf.set_fill_color(41, 128, 185)
        pdf.set_text_color(255, 255, 255)
        pdf.set_font(self.config['font_family'], 'B', 16)
        pdf.cell(0, 15, 'TABLE OF CONTENTS', 0, 1, 'C', 1)
        
        # Reset colors
        pdf.set_fill_color(255, 255, 255)
        pdf.set_text_color(0, 0, 0)
        
        # Add sections with proper spacing
        sections = [
            ('1. EXECUTIVE SUMMARY', 1),
            ('2. COMPLIANCE ASSESSMENT OVERVIEW', 3),
            ('3. DETAILED FINDINGS', 5)
        ]
        
        # Add main sections
        for i, (title, page) in enumerate(sections):
            self._add_toc_item(pdf, title, page, 0, is_section=True)
        
        # Add findings as subsections
        current_page = 5
        for i, result in enumerate(report.results, 1):
            self._add_toc_item(
                pdf, 
                f"3.{i} {result.check_name.upper()}",
                current_page + i,
                level=1,
                is_section=False
            )
        
        # Add appendices
        current_page += len(report.results) + 2
        appendices = [
            ('4. IMPLEMENTATION RECOMMENDATIONS', current_page),
            ('5. GLOSSARY OF TERMS', current_page + 1),
            ('6. METHODOLOGY', current_page + 2),
            ('7. ABOUT THIS REPORT', current_page + 3)
        ]
        
        for title, page in appendices:
            self._add_toc_item(pdf, title, page, 0, is_section=True)
        
        # Add footer note
        pdf.set_font(self.config['font_family'], 'I', 8)
        pdf.set_text_color(150, 150, 150)
        pdf.set_xy(10, 280)
        pdf.cell(0, 5, 'This report is automatically generated by Health Tech Privacy Scanner', 0, 0, 'C')
    
    def _add_detailed_findings(self, pdf: FPDF, report: GDPRReport) -> None:
        """Add detailed findings to the PDF
        
        Args:
            pdf: FPDF instance
            report: GDPR report data
        """
        pdf.add_page()
        self._add_section_header(pdf, 'Detailed Findings')
        
        for i, result in enumerate(report.results, 1):
            pdf.set_font(self.config['font_family'], 'B', 14)
            pdf.set_text_color(0, 0, 0)
            self._safe_cell(pdf, 0, 10, f'{i}. {result.check_name}', 0, 1, 'L')
            
            # Status and severity with colors
            status_color = {
                CheckStatus.PASSED: (0, 128, 0),    # Green
                CheckStatus.FAILED: (255, 0, 0),    # Red
                CheckStatus.WARNING: (255, 165, 0), # Orange
                CheckStatus.INFO: (0, 0, 255)       # Blue
            }.get(result.status, (128, 128, 128))   # Gray for unknown
            
            severity_color = {
                'High': (220, 53, 69),     # Red
                'Medium': (255, 193, 7),    # Yellow
                'Low': (40, 167, 69),       # Green
                'Information': (23, 162, 184) # Light Blue
            }.get(result.severity, (108, 117, 125))  # Gray for unknown severity
            
            # Status and severity in a row
            pdf.set_font(self.config['font_family'], 'B', 10)
            self._safe_cell(pdf, 40, 8, 'Status: ', 0, 0, 'L')
            pdf.set_text_color(*status_color)
            self._safe_cell(pdf, 60, 8, result.status.value, 0, 0, 'L')
            
            pdf.set_text_color(0, 0, 0)
            self._safe_cell(pdf, 30, 8, 'Severity: ', 0, 0, 'L')
            pdf.set_text_color(*severity_color)
            self._safe_cell(pdf, 0, 8, result.severity, 0, 1, 'L')
            
            # Add description
            pdf.set_text_color(0, 0, 0)
            pdf.set_font(self.config['font_family'], '', 10)
            self._safe_multi_cell(pdf, 0, 5, result.description)
            
            # Add details if any
            if result.details:
                pdf.ln(3)
                pdf.set_font(self.config['font_family'], 'B', 10)
                self._safe_cell(pdf, 0, 6, 'Details:', 0, 1, 'L')
                pdf.set_font(self.config['font_family'], '', 9)
                
                for key, value in result.details.items():
                    if isinstance(value, (list, tuple, set)):
                        value = ', '.join(str(v) for v in value)
                    if isinstance(value, dict):
                        value = ', '.join(f"{k}: {v}" for k, v in value.items())
                    self._safe_multi_cell(pdf, 0, 5, f"- {key}: {value}")
            
            # Add solution if available
            if result.solution:
                self._add_solution(pdf, result.solution)
            
            # Add page break if we're getting close to the bottom
            if pdf.get_y() > 250:
                pdf.add_page()
            else:
                pdf.ln(5)
                pdf.line(10, pdf.get_y(), 200, pdf.get_y())
                pdf.ln(5)
    
    def _add_solutions_appendix(self, pdf: FPDF, report: GDPRReport) -> None:
        """Add implementation solutions to the PDF
        
        Args:
            pdf: FPDF instance
            report: GDPR report data
        """
        pdf.add_page()
        self._add_section_header(pdf, 'Implementation Solutions')
        
        for i, result in enumerate([r for r in report.results if r.solution], 1):
            pdf.set_font(self.config['font_family'], 'B', 12)
            pdf.cell(0, 10, f'Solution {i}: {result.check_name}', 0, 1, 'L')
            
            # Add solution description
            pdf.set_font(self.config['font_family'], '', 10)
            pdf.multi_cell(0, 5, result.solution.description)
            
            # Add code snippet
            if result.solution.code_snippet:
                self._add_code_block(
                    pdf, 
                    result.solution.code_snippet,
                    result.solution.language
                )
            
            pdf.ln(5)
    
    def _add_section_header(self, pdf: FPDF, title: str, level: int = 1) -> None:
        """Add a section header
        
        Args:
            pdf: FPDF instance
            title: Section title
            level: Header level (1-3)
        """
        font_sizes = {1: 16, 2: 14, 3: 12}
        font_size = font_sizes.get(level, 12)
        
        pdf.set_font(self.config['font_family'], 'B', font_size)
        pdf.set_text_color(51, 122, 183)  # Blue color
        pdf.cell(0, 10, title, 0, 1, 'L')
        pdf.set_text_color(0, 0, 0)  # Reset to black
        pdf.line(10, pdf.get_y(), 200, pdf.get_y())
        pdf.ln(5)
    
    def _add_metric(self, pdf: FPDF, label: str, value: str, 
                   color: tuple = (0, 0, 0), font_size: int = 12) -> None:
        """Add a metric to the PDF
        
        Args:
            pdf: FPDF instance
            label: Metric label
            value: Metric value
            color: Text color as RGB tuple
            font_size: Font size
        """
        pdf.set_font(self.config['font_family'], 'B', font_size)
        pdf.set_text_color(0, 0, 0)
        pdf.cell(60, 10, f"{label}:", 0, 0, 'R')
        
        pdf.set_text_color(*color)
        pdf.cell(0, 10, value, 0, 1, 'L')
        
        # Reset text color
        pdf.set_text_color(0, 0, 0)
    
    def _add_toc_item(self, pdf: FPDF, text: str, page: int, level: int = 0, is_section: bool = False) -> None:
        """Add a styled table of contents item with proper indentation and styling
        
        Args:
            pdf: FPDF instance
            text: Item text
            page: Page number
            level: Indentation level (0 for main sections, 1 for subsections, etc.)
            is_section: Whether this is a main section (affects styling)
        """
        # Set styling based on level and section type
        if is_section:
            # Main section styling
            font_size = 12
            font_weight = 'B'
            text_color = (41, 128, 185)  # Blue
            bg_color = (241, 248, 255)   # Light blue background
            y_offset = 8
            line_height = 10
        else:
            # Subsection styling
            font_size = 10 - (level * 1)
            font_weight = 'B' if level == 0 else ''
            text_color = (50, 50, 50)    # Dark gray
            bg_color = (255, 255, 255)   # White background
            y_offset = 5
            line_height = 8
        
        # Set font and colors
        pdf.set_font(self.config['font_family'], font_weight, font_size)
        pdf.set_text_color(*text_color)
        
        # Calculate positions
        x = 15 + (level * 8)  # Indent based on level
        y = pdf.get_y()
        
        # Add background for main sections
        if is_section:
            pdf.set_fill_color(*bg_color)
            pdf.rect(10, y, 190, line_height + 2, 'F')
        
        # Add left border for main sections
        if is_section:
            pdf.set_draw_color(*text_color)
            pdf.set_line_width(0.5)
            pdf.line(10, y, 10, y + line_height + 2)
        
        # Draw the text
        pdf.set_xy(x, y + 1)
        pdf.cell(0, line_height, text, 0, 0, 'L')
        
        # Add dots for non-section items
        if not is_section:
            dot_leader = '. ' * 20  # More spaced dots for better readability
            available_width = 180 - x - 20  # Leave space for page number
            dots_width = pdf.get_string_width(dot_leader)
            
            # Calculate how many dots we can fit
            dots_to_draw = int((available_width - pdf.get_string_width(text)) / pdf.get_string_width('. '))
            dot_leader = '. ' * dots_to_draw if dots_to_draw > 0 else ' '
            
            pdf.set_xy(x + pdf.get_string_width(text), y + 1)
            pdf.set_text_color(200, 200, 200)  # Light gray dots
            pdf.cell(0, line_height, dot_leader, 0, 0, 'L')
        
        # Add page number
        pdf.set_text_color(*text_color)  # Reset text color
        pdf.set_xy(170, y + 1)
        pdf.cell(30, line_height, str(page), 0, 1, 'R')
        
        # Add spacing after item
        pdf.ln(2 if is_section else 1)
    
    def _add_code_block(self, pdf: FPDF, code: str, language: str = 'javascript') -> None:
        """Add a code block to the PDF with syntax highlighting and line numbers
        
        Args:
            pdf: FPDF instance
            code: Code content (must be a string)
            language: Programming language for syntax highlighting (not currently used)
        """
        # Validate inputs
        if not code or not isinstance(code, str):
            return
            
        # Clean the code to ensure ASCII-only content
        code = self._clean_text(code)
        if not code:
            return
            
        # Save current position
        x = pdf.get_x()
        y = pdf.get_y()
        
        # Calculate dimensions
        width = 190  # Full width with margins
        line_height = 5  # Height per line
        
        # Split code into lines and limit number of lines to prevent excessive memory usage
        lines = code.split('\n')[:200]  # Limit to 200 lines max
        num_lines = len(lines)
        
        # Calculate total height needed with some padding
        total_height = (num_lines * line_height) + 10
        
        # Check if we need a page break
        if y + total_height > 270:  # Leave some margin at the bottom
            pdf.add_page()
            y = 20  # Reset Y position after page break
            x = 15
        
        try:
            # Draw code block background
            pdf.set_fill_color(240, 240, 240)  # Light gray background
            pdf.rect(x, y, width, total_height, 'F')
            
            # Draw border
            pdf.set_draw_color(200, 200, 200)
            pdf.rect(x, y, width, total_height)
            
            # Set font for code
            pdf.set_font('Courier', '', 9)  # Use monospace font for code
            
            # Add each line of code
            for i, line in enumerate(lines, 1):
                line_y = y + 5 + ((i-1) * line_height)
                
                # Skip if we're going to run off the page
                if line_y > 270:
                    pdf.add_page()
                    y = 20
                    x = 15
                    line_y = y + 5
                    
                    # Redraw background for new page
                    pdf.set_fill_color(240, 240, 240)
                    remaining_lines = num_lines - (i - 1)
                    new_height = (remaining_lines * line_height) + 10
                    pdf.rect(x, y, width, new_height, 'F')
                    pdf.rect(x, y, width, new_height)
                
                # Add line number
                pdf.set_xy(x + 2, line_y - 2)
                pdf.set_text_color(100, 100, 100)  # Gray text for line numbers
                self._safe_cell(pdf, 20, line_height, str(i).rjust(3) + ' ', 0, 0, 'R')
                
                # Add code (use safe text handling)
                pdf.set_text_color(0, 0, 0)  # Black text for code
                pdf.set_xy(x + 25, line_y - 2)
                self._safe_cell(pdf, width - 30, line_height, line, 0, 1, 'L')
            
            # Update position
            pdf.set_xy(x, y + total_height + 5)
            
        except Exception as e:
            # If anything goes wrong, add a simple text box with the error
            pdf.set_xy(x, y)
            pdf.set_fill_color(255, 230, 230)  # Light red background
            pdf.rect(x, y, width, 20, 'F')
            pdf.set_text_color(200, 0, 0)
            pdf.set_font(self.config['font_family'], 'B', 10)
            self._safe_multi_cell(pdf, width, 5, f'Error displaying code block: {str(e)[:100]}')
            pdf.set_xy(x, y + 25)
        
        # Reset font and color
        pdf.set_font(self.config['font_family'], '', self.config['normal_font_size'])
        pdf.set_text_color(0, 0, 0)
    
    def _add_solution(self, pdf: FPDF, solution: GDPRSolution) -> None:
        """Add a solution to the PDF with improved formatting
        
        Args:
            pdf: FPDF instance
            solution: Solution to add
        """
        # Save current position
        y_before = pdf.get_y()
        
        # Add solution header with text icon
        pdf.set_fill_color(217, 237, 247)  # Light blue background
        pdf.set_text_color(49, 112, 143)   # Darker blue text
        pdf.set_font(self.config['font_family'], 'B', 11)
        self._safe_cell(pdf, 0, 8, ' [TOOLS] Recommended Solution', 0, 1, 'L', 1)
        
        # Add solution description
        pdf.set_fill_color(255, 255, 255)  # White background
        pdf.set_text_color(0, 0, 0)        # Black text
        pdf.set_font(self.config['font_family'], '', 10)
        
        # Add complexity indicator
        complexity_colors = {
            'low': (92, 184, 92),      # Green
            'medium': (240, 173, 78),   # Orange
            'high': (217, 83, 79)       # Red
        }
        
        complexity_color = complexity_colors.get(solution.complexity.lower() if solution.complexity else '', (108, 117, 125))
        
        pdf.set_font(self.config['font_family'], 'B', 9)
        self._safe_cell(pdf, 25, 6, 'Complexity: ', 0, 0, 'L')
        pdf.set_text_color(*complexity_color)
        complexity_text = solution.complexity.capitalize() if solution.complexity else 'N/A'
        self._safe_cell(pdf, 0, 6, complexity_text, 0, 1, 'L')
        
        # Reset text color
        pdf.set_text_color(0, 0, 0)
        
        # Add solution description with proper formatting
        pdf.ln(3)
        pdf.set_font(self.config['font_family'], 'B', 10)
        self._safe_cell(pdf, 0, 5, 'Description:', 0, 1, 'L')
        
        # Use safe text handling for description
        pdf.set_font(self.config['font_family'], '', 9)
        description = solution.description if solution.description else 'No description available.'
        self._safe_multi_cell(pdf, 0, 5, description)
        
        # Add code snippet if available
        if solution.code_snippet and solution.language:
            pdf.ln(3)
            pdf.set_font(self.config['font_family'], 'B', 10)
            self._safe_cell(pdf, 0, 5, 'Implementation:', 0, 1, 'L')
            self._add_code_block(pdf, solution.code_snippet, solution.language)
        
        # Draw border around the solution
        y_after = pdf.get_y()
        solution_height = y_after - y_before + 5
        
        # Only draw border if we have enough space on the page
        if y_after < 270:  # Leave some margin at the bottom
            pdf.rect(10, y_before, pdf.w - 20, solution_height)
        
        pdf.ln(5)
