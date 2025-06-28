import sys
import os

# Add your project directory to the Python path
project_home = os.path.dirname(os.path.abspath(__file__))
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# Import the Flask application
from web_app import app as application  # noqa

# Optional: Configure any additional settings
application.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-here')

# Ensure the instance folder exists
try:
    os.makedirs(os.path.join(project_home, 'instance'))
except OSError:
    pass
