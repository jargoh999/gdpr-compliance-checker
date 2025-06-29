#!/bin/bash

# Install Chrome for Selenium
wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && echo "deb http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list \
    && apt-get update -qqy \
    && apt-get -qqy install google-chrome-stable \
    && rm /etc/apt/sources.list.d/google-chrome.list \
    && rm -rf /var/lib/apt/lists/* /var/cache/apt/*

# Set display port and dbus env to avoid hanging (issue #118)
export DISPLAY=:99.0
export DBUS_SESSION_BUS_ADDRESS=/dev/null

# Start Xvfb
Xvfb :99 -screen 0 1024x768x16 > /dev/null 2>&1 &

# Wait for Xvfb
sleep 3

# Set Chrome options
export CHROME_DRIVER_VERSION=`curl -sS https://chromedriver.storage.googleapis.com/LATEST_RELEASE`
wget -q "https://chromedriver.storage.googleapis.com/$CHROME_DRIVER_VERSION/chromedriver_linux64.zip" -O /tmp/chromedriver_linux64.zip
unzip -qq /tmp/chromedriver_linux64.zip -d /usr/local/bin/
chmod +x /usr/local/bin/chromedriver
rm /tmp/chromedriver_linux64.zip

# Install Playwright browsers
python -m playwright install
python -m playwright install-deps
