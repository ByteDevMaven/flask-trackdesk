import os
from datetime import timedelta

class Config:
                           
    SECRET_KEY = os.getenv("SECRET_KEY", "aa13c1a2d52217687bcb0832883bdd348f015a5a716e8bd8013d61b656f4f4d7")
    ITEMS_PER_PAGE = os.getenv("ITEMS_PER_PAGE", 10)
    ALLOW_REGISTRATION = os.getenv("ALLOW_REGISTRATION", False)
    DEBUG = os.getenv("DEBUG", False)

                                       
    SQLALCHEMY_DATABASE_URI = os.getenv("SQLALCHEMY_DATABASE_URI", "sqlite:///trackdesk.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = os.getenv("SQLALCHEMY_TRACK_MODIFICATIONS", False)

                           
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=int(os.getenv("PERMANENT_SESSION_LIFETIME", 60)))
    SESSION_TYPE = os.getenv("SESSION_TYPE", 'filesystem')
    SESSION_COOKIE_HTTPONLY = os.getenv("SESSION_COOKIE_HTTPONLY", True)
    SESSION_COOKIE_SECURE = os.getenv("SESSION_COOKIE_SECURE", True)
    REMEMBER_COOKIE_DURATION = timedelta(days=int(os.getenv("REMEMBER_COOKIE_DURATION", 7)))

                                                   
    BABEL_DEFAULT_LOCALE = os.getenv("BABEL_DEFAULT_LOCALE", 'en')
    BABEL_DEFAULT_TIMEZONE = os.getenv("BABEL_DEFAULT_TIMEZONE", 'UTC')
    BABEL_TRANSLATION_DIRECTORIES = os.getenv("BABEL_TRANSLATION_DIRECTORIES", 'translations')

    # Flask-Mail config
    MAIL_SERVER = os.getenv("MAIL_SERVER", "smtp.googlemail.com")
    MAIL_PORT = int(os.getenv("MAIL_PORT", 587))
    MAIL_USE_TLS = os.getenv("MAIL_USE_TLS", "true").lower() in ["true", "on", "1"]
    MAIL_USERNAME = os.getenv("MAIL_USERNAME")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
    TRACKDESK_MAIL_SUBJECT_PREFIX = '[TrackDesk]'
    TRACKDESK_MAIL_SENDER = os.getenv("TRACKDESK_MAIL_SENDER", "TrackDesk Admin <admin@trackdesk.local>")
    TRACKDESK_ADMIN = os.getenv("TRACKDESK_ADMIN", "vrsanchesu@gmail.com")
    
                         
    LANGUAGES = {}
    
    # File uploads for expense receipts
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'app', 'static', 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB max
    ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg', 'webp', 'heic'}

    @staticmethod
    def init_app(app):
        langs = os.getenv("LANGUAGES", "")
        Config.LANGUAGES = dict(
            item.split(":") for item in langs.split(",") if item
        )