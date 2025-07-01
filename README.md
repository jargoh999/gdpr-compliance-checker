# GDPR Compliance Checker

A comprehensive tool to check websites for GDPR compliance, built with Python, Selenium, and Streamlit.

## Features

- **Cookie Consent Check**: Verifies the presence and compliance of cookie consent banners
- **Privacy Policy Check**: Validates the existence and content of privacy policies
- **Detailed Reporting**: Generates comprehensive PDF reports with findings and recommendations
- **Interactive UI**: User-friendly web interface powered by Streamlit
- **Modular Architecture**: Easy to extend with additional compliance checks

## Installation

### Local Development

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/gdpr-compliance-checker.git
   cd gdpr-compliance-checker
   ```

2. Create and activate a virtual environment:
   ```bash
   # On Windows
   python -m venv venv
   .\venv\Scripts\activate
   
   # On macOS/Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   python -m playwright install
   python -m playwright install-deps
   ```

4. Run the application locally:
   ```bash
   streamlit run streamlit_app.py
   ```

### Deployment to Streamlit Cloud

1. Fork this repository to your GitHub account
2. Go to [Streamlit Cloud](https://share.streamlit.io/) and sign in with your GitHub account
3. Click "New app" and select your forked repository
4. Set the following configuration:
   - Repository: `yourusername/gdpr-compliance-checker`
   - Branch: `main`
   - Main file path: `streamlit_app.py`
5. Click "Deploy!"

   The app will be deployed and you'll get a public URL to access it.

#### Important Notes for Streamlit Cloud:
- The app may take a few minutes to build and start, especially the first time
- The free tier of Streamlit Cloud has resource limitations which might affect performance
- For production use, consider upgrading to a paid plan for better performance and reliability

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. Start the Streamlit application:
   ```bash
   streamlit run app.py
   ```

2. Open your web browser and navigate to `http://localhost:8501`

3. Enter the URL of the website you want to check and click "Run Compliance Check"

4. View the results and download the PDF report

## Project Structure

```
gdpr-compliance-checker/
├── components/               # Individual GDPR check modules
│   ├── base_checker.py       # Base class for all checkers
│   ├── cookie_banner_checker.py  # Cookie consent banner checks
│   └── privacy_policy_checker.py # Privacy policy checks
├── config/
│   └── constants.py        # Configuration and constants
├── models/
│   └── gdpr_check.py       # Data models for checks and results
├── services/
│   ├── pdf_generator.py    # PDF report generation
│   └── web_driver.py        # Selenium WebDriver management
├── app.py                   # Main Streamlit application
├── requirements.txt          # Python dependencies
└── README.md                # This file
```

## Adding New Checks

To add a new GDPR compliance check:

1. Create a new Python file in the `components` directory
2. Create a class that inherits from `BaseChecker`
3. Implement the required properties and methods
4. Update the `initialize_checkers` method in `app.py` to include your new checker

Example:

```python
from .base_checker import BaseChecker
from models.gdpr_check import GDPRCheckResult, CheckStatus

class MyNewChecker(BaseChecker):
    @property
    def check_id(self) -> str:
        return "my_new_check"
    
    @property
    def check_name(self) -> str:
        return "My New Check"
    
    def _execute_check(self, url: str) -> GDPRCheckResult:
        # Your check implementation here
        pass
```

## Dependencies

- Python 3.8+
- Selenium
- Streamlit
- fpdf2
- webdriver-manager
- beautifulsoup4
- requests
- tldextract

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Disclaimer

This tool is provided for informational purposes only and does not constitute legal advice. Always consult with a qualified legal professional for compliance matters.
# emenike-healthcare-privacy-system
