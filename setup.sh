#!/bin/bash

# Exit on error
set -e

echo "=== Setting up environment for Streamlit Cloud ==="

# Update package lists
echo "Updating package lists..."
sudo apt-get update -qq

# Install system dependencies for Chrome and Chromium
echo "Installing system dependencies..."
sudo apt-get install -y --no-install-recommends \
    wget \
    unzip \
    xvfb \
    libxss1 \
    libxtst6 \
    libnss3 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libxkbcommon0 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libasound2 \
    libatspi2.0-0 \
    libxshmfence1 \
    libx11-xcb1 \
    libxcb-dri3-0 \
    libdrm-common \
    libegl1 \
    libgl1 \
    libgl1-mesa-dri \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libglu1-mesa \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libpangoft2-1.0-0 \
    libx11-6 \
    libx11-xcb1 \
    libxcb1 \
    libxcomposite1 \
    libxcursor1 \
    libxdamage1 \
    libxi6 \
    libxrandr2 \
    libxrender1 \
    libxtst6 \
    ca-certificates \
    fonts-liberation \
    libappindicator1 \
    libnspr4 \
    libnss3 \
    lsb-release \
    xdg-utils \
    libnss3-tools \
    libgbm-dev \
    libxcb-icccm4 \
    libxcb-image0 \
    libxcb-keysyms1 \
    libxcb-randr0 \
    libxcb-render-util0 \
    libxcb-xinerama0 \
    --no-install-suggests \
    --no-install-recommends

# Install Chrome
echo "Installing Google Chrome..."
wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | sudo gpg --dearmor -o /usr/share/keyrings/google-chrome-archive-keyring.gpg
echo "deb [arch=amd64 signed-by=/usr/share/keyrings/google-chrome-archive-keyring.gpg] http://dl.google.com/linux/chrome/deb/ stable main" | sudo tee /etc/apt/sources.list.d/google-chrome.list
sudo apt-get update -qq
sudo apt-get install -y google-chrome-stable --no-install-recommends

# Install Python dependencies
echo "Installing Python dependencies..."
python -m pip install --upgrade pip
pip install -r requirements.txt

# Install Playwright and its dependencies
echo "Installing Playwright and browsers..."
pip install playwright
python -m playwright install --with-deps
python -m playwright install-deps
python -m playwright install chromium
python -m playwright install firefox
python -m playwright install webkit

# Create necessary directories
echo "Creating required directories..."
mkdir -p ~/.cache/ms-playwright
chmod -R 777 ~/.cache/ms-playwright

# Set environment variables
export DISPLAY=:99
export CHROME_BIN=/usr/bin/google-chrome
export CHROME_PATH=/usr/bin/google-chrome
export PLAYWRIGHT_BROWSERS_PATH=~/ms-playwright

# Start Xvfb in the background
echo "Starting Xvfb..."
Xvfb :99 -screen 0 1920x1080x16 &

# Verify installations
echo "=== Verifying installations... ==="
which google-chrome
echo "Chrome version:" && google-chrome --version

echo "=== ChromeDriver installation... ==="
python -c "from webdriver_manager.chrome import ChromeDriverManager; print('ChromeDriver path:', ChromeDriverManager().install())"

echo "=== Playwright browsers... ==="
python -c "from playwright.sync_api import sync_playwright; print('Playwright browsers:'); [print(browser) for browser in sync_playwright().start().browsers]"

echo "=== Environment variables... ==="
printenv | grep -E 'CHROME|PLAYWRIGHT|DISPLAY|PATH'

echo "=== Setup completed successfully! ==="