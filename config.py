import os
from datetime import timedelta

class Config:
    # General Configuration
    SECRET_KEY = os.getenv("SECRET_KEY", "aa13c1a2d52217687bcb0832883bdd348f015a5a716e8bd8013d61b656f4f4d7")
    ITEMS_PER_PAGE = os.getenv("ITEMS_PER_PAGE", 10)

    # SQLAlchemy Database Configuration
    SQLALCHEMY_DATABASE_URI = 'sqlite:///trackdesk.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Session configuration
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=int(os.getenv("SESSION_LIFETIME_MINUTES", 60)))
    SESSION_TYPE = 'filesystem'
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SECURE = True
    REMEMBER_COOKIE_DURATION = timedelta(days=int(os.getenv("REMEMBER_COOKIE_DAYS", 7)))

    # Babel configuration for multilanguage support
    BABEL_DEFAULT_LOCALE = 'es'
    BABEL_DEFAULT_TIMEZONE = 'UTC'
    BABEL_TRANSLATION_DIRECTORIES = 'translations'
    
    # Supported languages
    LANGUAGES = {
        'en': 'English',
        'es': 'Español',
    }