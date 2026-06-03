import os
import sys
from pathlib import Path

# Add the root directory to the python path just in case
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

# Import the actual WSGI application from GENZO
from GENZO.wsgi import application
