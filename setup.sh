#!/bin/bash

# Exit on error
set -e

echo "🚀 Starting setup for Streamlit Cloud..."

# Install system dependencies
echo "🔧 Installing system dependencies..."
sudo apt-get update
sudo apt-get install -y \
    wget \
    gnupg \
    ca-certificates \
    curl \
    unzip \
    xvfb \
    x11-utils \
    x11-xserver-utils \
    dbus-x11 \
    libxss1 \
    libappindicator1 \
    libindicator7 \
    fonts-liberation \
    libgbm1 \
    libnss3 \
    libnspr4 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libxkbcommon0 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    libpango-1.0-0 \
    libcairo2 \
    libasound2 \
    libatspi2.0-0 \
    libxshmfence1 \
    libx11-xcb1 \
    libxcb-dri3-0 \
    libxcb1 \
    libxcb-util1 \
    libxcb-icccm4 \
    libxcb-keysyms1 \
    libxcb-randr0 \
    libxcb-render-util0 \
    libxcb-shm0 \
    libxcb-xfixes0 \
    libxcb-xinerama0 \
    libxcb-xinput0 \
    libxcb-xkb1 \
    libxcb-xtest0 \
    libxcb-shape0 \
    libxcb-xrm0

# Install Google Chrome
echo "🌐 Installing Google Chrome..."
wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | sudo apt-key add - \
    && echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" | sudo tee /etc/apt/sources.list.d/google-chrome.list \
    && sudo apt-get update \
    && sudo apt-get install -y google-chrome-stable

# Install ChromeDriver
echo "🔗 Installing ChromeDriver..."
CHROME_VERSION=$(google-chrome --version | grep -oP '\d+\.\d+\.\d+\.\d+' | cut -d. -f1-3)
CHROMEDRIVER_VERSION=$(curl -s "https://chromedriver.storage.googleapis.com/LATEST_RELEASE_${CHROME_VERSION}")
wget -q "https://chromedriver.storage.googleapis.com/${CHROMEDRIVER_VERSION}/chromedriver_linux64.zip" \
    && unzip -o chromedriver_linux64.zip \
    && sudo mv chromedriver /usr/local/bin/chromedriver \
    && sudo chmod +x /usr/local/bin/chromedriver \
    && rm chromedriver_linux64.zip

# Install Playwright and browsers
echo "🎭 Setting up Playwright..."
python -m pip install --upgrade pip
pip install playwright
playwright install-deps
playwright install chromium

# Verify installations
echo "✅ Verifying installations..."
echo "Chrome version: $(google-chrome --version || echo 'Not found')"
echo "ChromeDriver version: $(chromedriver --version || echo 'Not found')"

# Set environment variables
echo "🔧 Setting environment variables..."
export DISPLAY=:99.0
export DBUS_SESSION_BUS_ADDRESS=/dev/null

# Start Xvfb in the background
echo "🖥️  Starting Xvfb..."
Xvfb :99 -screen 0 1920x1080x24 &

# Wait for Xvfb to start
echo "⏳ Waiting for Xvfb to start..."
sleep 3

echo "✨ Setup completed successfully! ✨"

# Keep the script running to keep the container alive
# tail -f /dev/null
