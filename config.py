import os
from datetime import timedelta

class Config:
    # General Configuration
    SECRET_KEY = os.getenv("SECRET_KEY", "aa13c1a2d52217687bcb0832883bdd348f015a5a716e8bd8013d61b656f4f4d7")

    # SQLAlchemy Database Configuration
    SQLALCHEMY_DATABASE_URI = 'sqlite:///trackdesk.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Session configuration
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=60)
    SESSION_TYPE = 'filesystem'
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SECURE = True
    REMEMBER_COOKIE_DURATION = timedelta(days=7)

    # Babel configuration for multilanguage support
    BABEL_DEFAULT_LOCALE = 'en'
    BABEL_DEFAULT_TIMEZONE = 'UTC'
    BABEL_TRANSLATION_DIRECTORIES = 'translations'
    
    # Supported languages
    LANGUAGES = {
        'en': 'English',
        'es': 'Español',
        'fr': 'Français',
        'pt': 'Português',
        'de': 'Deutsch'
    }