from dotenv import load_dotenv
import os

# Load .env file
load_dotenv()


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "your_secret_key")
    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "your_jwt_secret_key")

    # OAuth configuration
    GOOGLE_CLIENT_ID = os.getenv('GOOGLE_OAUTH_CLIENT_ID')
    GOOGLE_CLIENT_SECRET = os.getenv('GOOGLE_OAUTH_CLIENT_SECRET')


    DB_USER = os.environ.get("DB_USER", "your_db_user")
    DB_PASSWORD = os.environ.get("DB_PASSWORD", "your_db_password")
    DB_HOST = os.environ.get("DB_HOST", "localhost")
    DB_PORT = os.environ.get("DB_PORT", 5432)
    DB_NAME = os.environ.get("DB_NAME", "your_db_name")

    SQLALCHEMY_DATABASE_URI = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    

    JWT_TOKEN_LOCATION = ["cookies"]  # Store JWT in cookies
    JWT_COOKIE_SECURE = False         # Set to True in production
    JWT_COOKIE_CSRF_PROTECT = False   # CSRF protection (disable for now during development)
    JWT_ACCESS_COOKIE_NAME = "access_token"
