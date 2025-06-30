# Run this script to set up and run the application locally on Windows

# Create and activate virtual environment if it doesn't exist
if (-not (Test-Path -Path ".\venv")) {
    Write-Host "Creating virtual environment..."
    python -m venv venv
}

# Activate the virtual environment
Write-Host "Activating virtual environment..."
.\venv\Scripts\Activate.ps1

# Install dependencies
Write-Host "Installing dependencies..."
pip install -r requirements.txt

# Install Playwright browsers
Write-Host "Installing Playwright browsers..."
python -m playwright install
python -m playwright install-deps

# Set environment variables
$env:FLASK_ENV = "development"
$env:FLASK_APP = "app.py"

# Run the application
Write-Host "Starting the application..."
Write-Host "Open http://localhost:8501 in your browser"
streamlit run streamlit_app.py

# Keep the window open to see any errors
Write-Host "Press any key to exit..."
$null = $Host.UI.RawUI.ReadKey('NoEcho,IncludeKeyDown')
