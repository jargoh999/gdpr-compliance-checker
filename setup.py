import os
import sys
import subprocess
from setuptools import setup, find_packages
from setuptools.command.install import install

class PostInstallCommand(install):
    """Post-installation for installation mode."""
    def run(self):
        install.run(self)
        # Install Chrome and ChromeDriver
        if os.name == 'posix' and not os.path.exists('/.dockerenv'):
            try:
                subprocess.check_call([sys.executable, '-m', 'playwright', 'install', 'chromium'])
                subprocess.check_call([sys.executable, '-m', 'playwright', 'install-deps'])
            except subprocess.CalledProcessError as e:
                print(f"Warning: Failed to install Playwright browsers: {e}")

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
