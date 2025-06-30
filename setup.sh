#!/bin/bash

# Exit on error
set -e

echo "=== Setting up environment for Streamlit Cloud ==="

# Install system dependencies
echo "Installing system dependencies..."
sudo apt-get update -qq
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
    libatspi2.0-0

# Install Python dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt

# Install Playwright and browsers
echo "Installing Playwright and browsers..."
python -m playwright install --with-deps
python -m playwright install-deps
python -m playwright install chromium

# Set environment variables for headless browser
export DISPLAY=:99
Xvfb :99 -screen 0 1920x1080x16 &

echo "=== Setup completed successfully! ==="