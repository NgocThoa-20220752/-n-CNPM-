import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Cấu hình cơ bản cho ứng dụng"""

    # Cấu hình chung
    SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-change-in-production')
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
    ENVIRONMENT = os.getenv('ENVIRONMENT', 'development')

    # Cấu hình Database MySQL
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_PORT = int(os.getenv('DB_PORT', 3306))
    DB_NAME = os.getenv('DB_NAME', 'your_database')
    DB_USER = os.getenv('DB_USER', 'root')
    DB_PASSWORD = os.getenv('DB_PASSWORD', '')
    DB_CHARSET = os.getenv('DB_CHARSET', 'utf8mb4')

    # Connection pool settings
    DB_POOL_SIZE = int(os.getenv('DB_POOL_SIZE', 10))
    DB_POOL_MAX_OVERFLOW = int(os.getenv('DB_POOL_MAX_OVERFLOW', 20))
    DB_POOL_TIMEOUT = int(os.getenv('DB_POOL_TIMEOUT', 30))
    DB_POOL_RECYCLE = int(os.getenv('DB_POOL_RECYCLE', 3600))

    # SQLAlchemy Database URI
    SQLALCHEMY_DATABASE_URI = (
        f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
        f"?charset={DB_CHARSET}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': DB_POOL_SIZE,
        'pool_pre_ping': True,
        'pool_recycle': DB_POOL_RECYCLE,
        'max_overflow': DB_POOL_MAX_OVERFLOW,
        'pool_timeout': DB_POOL_TIMEOUT
    }

    # Cấu hình bảo mật
    # JWT Settings
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', SECRET_KEY)
    JWT_ACCESS_TOKEN_EXPIRES = int(os.getenv('JWT_ACCESS_TOKEN_EXPIRES', 3600))  # 1 hour
    JWT_REFRESH_TOKEN_EXPIRES = int(os.getenv('JWT_REFRESH_TOKEN_EXPIRES', 2592000))  # 30 days
    JWT_ALGORITHM = os.getenv('JWT_ALGORITHM', 'HS256')

    # Password hashing
    BCRYPT_LOG_ROUNDS = int(os.getenv('BCRYPT_LOG_ROUNDS', 12))
    PASSWORD_MIN_LENGTH = int(os.getenv('PASSWORD_MIN_LENGTH', 8))
    PASSWORD_REQUIRE_UPPERCASE = os.getenv('PASSWORD_REQUIRE_UPPERCASE', 'True').lower() == 'true'
    PASSWORD_REQUIRE_LOWERCASE = os.getenv('PASSWORD_REQUIRE_LOWERCASE', 'True').lower() == 'true'
    PASSWORD_REQUIRE_DIGIT = os.getenv('PASSWORD_REQUIRE_DIGIT', 'True').lower() == 'true'
    PASSWORD_REQUIRE_SPECIAL = os.getenv('PASSWORD_REQUIRE_SPECIAL', 'True').lower() == 'true'

    # Rate limiting
    RATELIMIT_ENABLED = os.getenv('RATELIMIT_ENABLED', 'True').lower() == 'true'
    RATELIMIT_DEFAULT = os.getenv('RATELIMIT_DEFAULT', '100/hour')
    RATELIMIT_STORAGE_URL = os.getenv('RATELIMIT_STORAGE_URL', 'memory://')

    # CORS Settings
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', '*').split(',')
    CORS_ALLOW_CREDENTIALS = os.getenv('CORS_ALLOW_CREDENTIALS', 'True').lower() == 'true'

    # Security Headers
    SECURE_HEADERS = {
        'X-Frame-Options': 'DENY',
        'X-Content-Type-Options': 'nosniff',
        'X-XSS-Protection': '1; mode=block',
        'Strict-Transport-Security': 'max-age=31536000; includeSubDomains'
    }

    # Cấu hình Email
    MAIL_SERVER = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.getenv('MAIL_PORT', 587))
    MAIL_USE_TLS = os.getenv('MAIL_USE_TLS', 'True').lower() == 'true'
    MAIL_USE_SSL = os.getenv('MAIL_USE_SSL', 'False').lower() == 'true'
    MAIL_USERNAME = os.getenv('MAIL_USERNAME', '')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD', '')
    MAIL_DEFAULT_SENDER = os.getenv('MAIL_DEFAULT_SENDER', MAIL_USERNAME)
    MAIL_MAX_EMAILS = int(os.getenv('MAIL_MAX_EMAILS', 50))
    MAIL_ASCII_ATTACHMENTS = False

    # Email verification settings
    EMAIL_VERIFICATION_TOKEN_EXPIRES = int(os.getenv('EMAIL_VERIFICATION_TOKEN_EXPIRES', 3600))  # 1 hour
    EMAIL_VERIFICATION_CODE_LENGTH = int(os.getenv('EMAIL_VERIFICATION_CODE_LENGTH', 6))
    EMAIL_VERIFICATION_CODE_EXPIRES = int(os.getenv('EMAIL_VERIFICATION_CODE_EXPIRES', 600))  # 10 minutes

    # Cấu hình SMS (Twilio)
    SMS_PROVIDER = os.getenv('SMS_PROVIDER', 'twilio')  # twilio, vonage, aws_sns

    # Twilio settings
    TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID', '')
    TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN', '')
    TWILIO_PHONE_NUMBER = os.getenv('TWILIO_PHONE_NUMBER', '')
    TWILIO_VERIFY_SERVICE_SID = os.getenv('TWILIO_VERIFY_SERVICE_SID', '')

    # SMS verification settings
    SMS_VERIFICATION_CODE_LENGTH = int(os.getenv('SMS_VERIFICATION_CODE_LENGTH', 6))
    SMS_VERIFICATION_CODE_EXPIRES = int(os.getenv('SMS_VERIFICATION_CODE_EXPIRES', 300))  # 5 minutes
    SMS_MAX_ATTEMPTS = int(os.getenv('SMS_MAX_ATTEMPTS', 3))
    SMS_RESEND_COOLDOWN = int(os.getenv('SMS_RESEND_COOLDOWN', 60))  # 1 minute

    # OTP Settings
    OTP_SECRET_LENGTH = int(os.getenv('OTP_SECRET_LENGTH', 32))
    OTP_DIGITS = int(os.getenv('OTP_DIGITS', 6))
    OTP_INTERVAL = int(os.getenv('OTP_INTERVAL', 30))

    # Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    LOG_FILE = os.getenv('LOG_FILE', 'app.log')


class DevelopmentConfig(Config):
    """Cấu hình cho môi trường development"""
    DEBUG = True
    TESTING = False


class ProductionConfig(Config):
    """Cấu hình cho môi trường production"""
    DEBUG = False
    TESTING = False

    # Bắt buộc phải có secret key mạnh trong production
    if Config.SECRET_KEY == 'your-secret-key-change-in-production':
        raise ValueError("SECRET_KEY must be set in production environment")


class TestingConfig(Config):
    """Cấu hình cho môi trường testing"""
    DEBUG = True
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'


# Dictionary để chọn config theo môi trường
config_by_name = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig
}


def get_config():
    """Lấy cấu hình theo môi trường hiện tại"""
    env = os.getenv('ENVIRONMENT', 'development')
    return config_by_name.get(env, DevelopmentConfig)
