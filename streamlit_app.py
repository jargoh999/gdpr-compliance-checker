# Streamlit Cloud entry point
import os
import sys
import subprocess
from app import main

# Set environment variables for headless browser
os.environ['DISPLAY'] = ':99'
os.environ['PYTHONUNBUFFERED'] = '1'

# Start Xvfb in the background
if os.name == 'posix' and 'STREAMLIT_SERVER_RUN_ON_SAVE' in os.environ:
    subprocess.Popen(['Xvfb', ':99', '-screen', '0', '1920x1080x16'])

# Import and run the main function
if __name__ == "__main__":
    main()
