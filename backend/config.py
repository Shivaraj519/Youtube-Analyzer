import os
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-key-12345')
    raw_db_url = os.environ.get('DATABASE_URL', 'sqlite:///youtube_analyzer.db')
    if raw_db_url and raw_db_url.startswith('postgres://'):
        raw_db_url = raw_db_url.replace('postgres://', 'postgresql://', 1)
    SQLALCHEMY_DATABASE_URI = raw_db_url
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Google OAuth credentials
    GOOGLE_CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID', '')
    GOOGLE_CLIENT_SECRET = os.environ.get('GOOGLE_CLIENT_SECRET', '')
    GOOGLE_REDIRECT_URI = os.environ.get('GOOGLE_REDIRECT_URI', 'http://localhost:5000/api/auth/callback')
    
    # Gemini API key for AI generation
    GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', '')
    
    # Check if OAuth is configured
    @classmethod
    def is_oauth_configured(cls):
        return bool(cls.GOOGLE_CLIENT_ID and cls.GOOGLE_CLIENT_SECRET)
