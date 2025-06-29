import os
import sys
import subprocess
from setuptools import setup, find_packages
from setuptools.command.install import install

class PostInstallCommand(install):
    """Post-installation for installation mode."""
    def run(self):
        install.run(self)
        # Install Playwright browsers
        if os.name == 'posix':
            try:
                # First install dependencies
                print("Installing Playwright system dependencies...")
                subprocess.check_call([sys.executable, '-m', 'playwright', 'install-deps'])
                
                # Then install browsers
                print("Installing Playwright browsers...")
                subprocess.check_call([sys.executable, '-m', 'playwright', 'install', 'chromium'])
                
                # Install the browser binaries
                print("Installing Playwright browser binaries...")
                subprocess.check_call([sys.executable, '-m', 'playwright', 'install'])
                
            except subprocess.CalledProcessError as e:
                print(f"Warning: Failed to install Playwright browsers: {e}")
                print("You may need to install the browsers manually with:")
                print("  python -m playwright install")

setup(
    name="gdpr-compliance-checker",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        line.strip() for line in open('requirements.txt').readlines() 
        if line.strip() and not line.startswith('#')
    ],
    python_requires='>=3.8',
    cmdclass={
        'install': PostInstallCommand,
    },
    entry_points={
        'console_scripts': [
            'gdpr-checker=app:main',
        ],
    },
    include_package_data=True,
    package_data={
        '': ['*.json', '*.md', '*.txt'],
    },
    author="Your Name",
    author_email="your.email@example.com",
    description="GDPR Compliance Checker for websites",
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url="https://github.com/yourusername/gdpr-compliance-checker",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
