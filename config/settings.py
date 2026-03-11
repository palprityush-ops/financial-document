# config/settings.py

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Database settings
DATABASE = {
    'ENGINE': os.getenv('DB_ENGINE', 'django.db.backends.sqlite3'),
    'NAME': os.getenv('DB_NAME', 'db.sqlite3'),
    'USER': os.getenv('DB_USER', ''),
    'PASSWORD': os.getenv('DB_PASSWORD', ''),
    'HOST': os.getenv('DB_HOST', 'localhost'),
    'PORT': os.getenv('DB_PORT', '5432'),
}

# API Configuration
API_CONFIG = {
    'API_URL': os.getenv('API_URL', 'https://api.example.com'),
    'API_KEY': os.getenv('API_KEY', ''),
}

# Additional environment configurations can be added here.