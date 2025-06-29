#!/bin/bash
set -e

echo "=== Setting up Chrome and WebDriver ==="

# Install system dependencies
echo "Installing system dependencies..."
apt-get update -qqy
apt-get install -qqy --no-install-recommends \
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
    libx11-xcb1 \
    libxshmfence1 \
    libgl1-mesa-glx \
    x11-utils \
    xvfb \
    x11vnc \
    x11-xkb-utils \
    xfonts-100dpi \
    xfonts-75dpi \
    xfonts-scalable \
    xfonts-cyrillic \
    xserver-xorg-core \
    x11-apps \
    dbus-x11 \
    libgbm-dev \
    libxshmfence-dev \
    libasound2 \
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
    libx11-xcb1 \
    libxshmfence1 \
    libgl1-mesa-glx \
    && rm -rf /var/lib/apt/lists/*

# Install Chrome
echo "Installing Google Chrome..."
wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list \
    && apt-get update -qqy \
    && apt-get install -qqy google-chrome-stable \
    && rm /etc/apt/sources.list.d/google-chrome.list \
    && rm -rf /var/lib/apt/lists/*

# Set display port and dbus env to avoid hanging
export DISPLAY=:99.0
export DBUS_SESSION_BUS_ADDRESS=/dev/null

# Start Xvfb
echo "Starting Xvfb..."
Xvfb :99 -screen 0 1920x1080x24 -ac +extension RANDR +render -noreset > /dev/null 2>&1 &
# Wait for Xvfb
sleep 3

# Set Chrome options
echo "Setting up ChromeDriver..."
export CHROME_DRIVER_VERSION=$(curl -sS https://chromedriver.storage.googleapis.com/LATEST_RELEASE)
wget -q "https://chromedriver.storage.googleapis.com/$CHROME_DRIVER_VERSION/chromedriver_linux64.zip" -O /tmp/chromedriver_linux64.zip
unzip -qq /tmp/chromedriver_linux64.zip -d /usr/local/bin/
chmod +x /usr/local/bin/chromedriver
rm /tmp/chromedriver_linux64.zip

# Install Playwright browsers
echo "Installing Playwright browsers..."
python -m playwright install-deps
python -m playwright install chromium

# Verify installations
echo "=== Installation Summary ==="
echo "Chrome version: $(google-chrome --version)"
echo "ChromeDriver version: $(chromedriver --version)"
echo "Playwright browsers installed: $(python -m playwright install --dry-run)"
