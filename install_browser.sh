#!/bin/bash

# Exit on error
set -e

# Function to detect Linux distribution
get_linux_distro() {
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        echo "$ID"
    elif [ -f /etc/redhat-release ]; then
        echo "rhel"
    elif [ -f /etc/debian_version ]; then
        echo "debian"
    else
        echo "unknown"
    fi
}

# Install Chrome based on distribution
install_chrome() {
    local distro=$(get_linux_distro)
    
    case $distro in
        ubuntu|debian)
            echo "Installing Chrome on Ubuntu/Debian..."
            wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | sudo apt-key add - \
                && echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" | sudo tee /etc/apt/sources.list.d/google-chrome.list \
                && sudo apt-get update \
                && sudo apt-get install -y google-chrome-stable
            ;;
        centos|rhel|fedora)
            echo "Installing Chrome on CentOS/RHEL/Fedora..."
            sudo dnf install -y wget
            wget https://dl.google.com/linux/direct/google-chrome-stable_current_x86_64.rpm
            sudo dnf localinstall -y google-chrome-stable_current_x86_64.rpm
            ;;
        *)
            echo "Unsupported distribution. Trying to install Chromium..."
            if command -v apt-get &> /dev/null; then
                sudo apt-get install -y chromium-browser
            elif command -v dnf &> /dev/null; then
                sudo dnf install -y chromium
            elif command -v yum &> /dev/null; then
                sudo yum install -y chromium
            else
                echo "Could not install Chrome/Chromium. Please install manually."
                exit 1
            fi
            ;;
    esac
}

# Install system dependencies
install_dependencies() {
    local distro=$(get_linux_distro)
    
    case $distro in
        ubuntu|debian)
            echo "Installing dependencies on Ubuntu/Debian..."
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
                xfonts-100dpi \
                xfonts-75dpi \
                xfonts-scalable \
                xfonts-cyrillic \
                xauth \
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
            ;;
        centos|rhel|fedora)
            echo "Installing dependencies on CentOS/RHEL/Fedora..."
            sudo dnf install -y \
                wget \
                gtk3 \
                xorg-x11-server-Xvfb \
                xorg-x11-xauth \
                xorg-x11-utils \
                xorg-x11-fonts-100dpi \
                xorg-x11-fonts-75dpi \
                xorg-x11-fonts-cyrillic \
                xorg-x11-fonts-misc \
                xorg-x11-fonts-Type1 \
                alsa-lib \
                mesa-libgbm \
                libxcb \
                libxkbcommon \
                libxshmfence \
                libdrm \
                libX11-xcb \
                libxcb-dri3 \
                libxcb-util \
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
            ;;
        *)
            echo "Unsupported distribution. Trying to install basic dependencies..."
            if command -v apt-get &> /dev/null; then
                sudo apt-get update
                sudo apt-get install -y wget xvfb x11-utils x11-xserver-utils dbus-x11
            elif command -v dnf &> /dev/null; then
                sudo dnf install -y wget xorg-x11-server-Xvfb xorg-x11-utils xorg-x11-xauth
            elif command -v yum &> /dev/null; then
                sudo yum install -y wget xorg-x11-server-Xvfb xorg-x11-utils xorg-x11-xauth
            else
                echo "Could not install dependencies. Please install them manually."
                exit 1
            fi
            ;;
    esac
}

# Install ChromeDriver
install_chromedriver() {
    echo "Installing ChromeDriver..."
    
    # Try to get Chrome version
    if command -v google-chrome-stable &> /dev/null; then
        CHROME_VERSION=$(google-chrome-stable --version | grep -oP '\d+\.\d+\.\d+\.\d+' | cut -d. -f1-3)
    elif command -v google-chrome &> /dev/null; then
        CHROME_VERSION=$(google-chrome --version | grep -oP '\d+\.\d+\.\d+\.\d+' | cut -d. -f1-3)
    elif command -v chromium-browser &> /dev/null; then
        CHROME_VERSION=$(chromium-browser --version | grep -oP '\d+\.\d+\.\d+\.\d+' | cut -d. -f1-3)
    elif command -v chromium &> /dev/null; then
        CHROME_VERSION=$(chromium --version | grep -oP '\d+\.\d+\.\d+\.\d+' | cut -d. -f1-3)
    else
        echo "No Chrome/Chromium installation found. Using latest ChromeDriver..."
        CHROME_VERSION=""
    fi
    
    if [ -z "$CHROME_VERSION" ]; then
        # If we couldn't get Chrome version, use the latest ChromeDriver
        CHROMEDRIVER_DOWNLOAD_URL="https://chromedriver.storage.googleapis.com/LATEST_RELEASE"
        CHROMEDRIVER_VERSION=$(curl -s "$CHROMEDRIVER_DOWNLOAD_URL")
    else
        # Get the specific ChromeDriver version for the installed Chrome
        CHROMEDRIVER_DOWNLOAD_URL="https://chromedriver.storage.googleapis.com/LATEST_RELEASE_${CHROME_VERSION}"
        CHROMEDRIVER_VERSION=$(curl -s "$CHROMEDRIVER_DOWNLOAD_URL")
    fi
    
    echo "Downloading ChromeDriver version $CHROMEDRIVER_VERSION..."
    wget -q "https://chromedriver.storage.googleapis.com/${CHROMEDRIVER_VERSION}/chromedriver_linux64.zip" \
        && unzip -o chromedriver_linux64.zip \
        && sudo mv chromedriver /usr/local/bin/chromedriver \
        && sudo chmod +x /usr/local/bin/chromedriver \
        && rm chromedriver_linux64.zip
}

# Install Playwright browsers
install_playwright() {
    echo "Installing Playwright browsers..."
    
    # Install Node.js if not already installed
    if ! command -v node &> /dev/null; then
        echo "Installing Node.js..."
        curl -fsSL https://deb.nodesource.com/setup_16.x | sudo -E bash -
        sudo apt-get install -y nodejs
    fi
    
    # Install Playwright
    if ! command -v playwright &> /dev/null; then
        echo "Installing Playwright..."
        sudo npm install -g playwright
    fi
    
    # Install browsers
    echo "Installing Playwright browsers (this may take a while)..."
    npx playwright install --with-deps chromium
}

# Main installation process
echo "Starting Chrome and dependencies installation..."

# Install dependencies
install_dependencies

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
