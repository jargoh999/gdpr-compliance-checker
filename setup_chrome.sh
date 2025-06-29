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

# Install Chrome
install_chrome

# Install ChromeDriver
install_chromedriver

# Install Playwright browsers if needed
if [ "$1" = "--with-playwright" ]; then
    install_playwright
fi

# Verify installations
echo "Verifying installations..."

# Check Chrome/Chromium
if command -v google-chrome-stable &> /dev/null; then
    echo "Google Chrome: $(google-chrome-stable --version)"
elif command -v google-chrome &> /dev/null; then
    echo "Google Chrome: $(google-chrome --version)"
elif command -v chromium-browser &> /dev/null; then
    echo "Chromium: $(chromium-browser --version)"
elif command -v chromium &> /dev/null; then
    echo "Chromium: $(chromium --version)"
else
    echo "Warning: No Chrome/Chromium installation found"
fi

# Check ChromeDriver
if command -v chromedriver &> /dev/null; then
    echo "ChromeDriver: $(chromedriver --version)"
else
    echo "Warning: ChromeDriver not found"
fi

# Check Playwright if installed
if command -v playwright &> /dev/null; then
    echo "Playwright: $(playwright --version)"
    echo "Installed browsers:"
    npx playwright install --dry-run
fi

echo "\nSetup completed successfully!"
echo "If you need Playwright, run this script with --with-playwright"

# Set display port and dbus env to avoid hanging
export DISPLAY=:99.0
export DBUS_SESSION_BUS_ADDRESS=/dev/null

# Start Xvfb
echo "Starting Xvfb..."
Xvfb :99 -screen 0 1920x1080x24 -ac +extension RANDR +render -noreset > /dev/null 2>&1 &
# Wait for Xvfb
sleep 3

# Verify Chrome installation
echo "Chrome version: $(google-chrome --version || echo 'Chrome not found')"

# Verify installations
echo "=== Installation Summary ==="
echo "Chrome version: $(google-chrome --version)"
echo "ChromeDriver version: $(chromedriver --version)"
echo "Playwright browsers installed: $(python -m playwright install --dry-run)"
