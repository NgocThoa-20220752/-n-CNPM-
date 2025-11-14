import jwt
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError
import bcrypt
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any

import secrets
import re
import logging
from app.core.config import get_config

logger = logging.getLogger(__name__)
config = get_config()


class PasswordHasher:
    """Quản lý mã hóa và xác thực password"""

    @staticmethod
    def hash_password(password: str) -> str:
        """
        Mã hóa password sử dụng bcrypt

        Args:
            password: Password cần mã hóa

        Returns:
            Hashed password
        """
        try:
            salt = bcrypt.gensalt(rounds=config.BCRYPT_LOG_ROUNDS)
            hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
            return hashed.decode('utf-8')
        except Exception as e:
            logger.error(f"Error hashing password: {str(e)}")
            raise

    @staticmethod
    def verify_password(password: str, hashed_password: str) -> bool:
        """
        Xác thực password với hashed password

        Args:
            password: Password cần xác thực
            hashed_password: Hashed password từ database

        Returns:
            True nếu password đúng, False nếu sai
        """
        try:
            return bcrypt.checkpw(
                password.encode('utf-8'),
                hashed_password.encode('utf-8')
            )
        except Exception as e:
            logger.error(f"Error verifying password: {str(e)}")
            return False

    @staticmethod
    def validate_password_strength(password: str) -> tuple[bool, list[str]]:
        """
        Kiểm tra độ mạnh của password

        Args:
            password: Password cần kiểm tra

        Returns:
            (is_valid, error_messages)
        """
        errors = []

        if len(password) < config.PASSWORD_MIN_LENGTH:
            errors.append(f"Password must be at least {config.PASSWORD_MIN_LENGTH} characters long")

        if config.PASSWORD_REQUIRE_UPPERCASE and not re.search(r'[A-Z]', password):
            errors.append("Password must contain at least one uppercase letter")

        if config.PASSWORD_REQUIRE_LOWERCASE and not re.search(r'[a-z]', password):
            errors.append("Password must contain at least one lowercase letter")

        if config.PASSWORD_REQUIRE_DIGIT and not re.search(r'\d', password):
            errors.append("Password must contain at least one digit")

        if config.PASSWORD_REQUIRE_SPECIAL and not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            errors.append("Password must contain at least one special character")

        return len(errors) == 0, errors


class JWTManager:
    """Quản lý JWT tokens"""

    @staticmethod
    def create_access_token(
            data: Dict[str, Any],
            expires_delta: Optional[timedelta] = None
    ) -> str:
        """
        Tạo JWT access token

        Args:
            data: Dữ liệu cần encode vào token
            expires_delta: Thời gian hết hạn (optional)

        Returns:
            JWT access token
        """
        to_encode = data.copy()

        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(
                seconds=config.JWT_ACCESS_TOKEN_EXPIRES
            )

        to_encode.update({
            "exp": expire,
            "iat": datetime.now(timezone.utc),
            "type": "access"
        })

        try:
            encoded_jwt = jwt.encode(
                to_encode,
                config.JWT_SECRET_KEY,
                algorithm=config.JWT_ALGORITHM
            )
            return encoded_jwt
        except Exception as e:
            logger.error(f"Error creating access token: {str(e)}")
            raise

    @staticmethod
    def create_refresh_token(
            data: Dict[str, Any],
            expires_delta: Optional[timedelta] = None
    ) -> str:
        """
        Tạo JWT refresh token

        Args:
            data: Dữ liệu cần encode vào token
            expires_delta: Thời gian hết hạn (optional)

        Returns:
            JWT refresh token
        """
        to_encode = data.copy()

        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(
                seconds=config.JWT_REFRESH_TOKEN_EXPIRES
            )

        to_encode.update({
            "exp": expire,
            "iat": datetime.now(timezone.utc),
            "type": "refresh"
        })

        try:
            encoded_jwt = jwt.encode(
                to_encode,
                config.JWT_SECRET_KEY,
                algorithm=config.JWT_ALGORITHM
            )
            return encoded_jwt
        except Exception as e:
            logger.error(f"Error creating refresh token: {str(e)}")
            raise

    @staticmethod
    def decode_token(token: str) -> Optional[Dict[str, Any]]:
        """
        Giải mã JWT token

        Args:
            token: JWT token cần giải mã

        Returns:
            Decoded payload hoặc None nếu token không hợp lệ
        """
        try:
            payload = jwt.decode(
                token,
                config.JWT_SECRET_KEY,
                algorithms=[config.JWT_ALGORITHM]
            )
            return payload
        except ExpiredSignatureError:
            logger.warning("Token has expired")
            return None
        except InvalidTokenError as e:
            logger.warning(f"Invalid token: {str(e)}")
            return None

    @staticmethod
    def verify_token(token: str, token_type: str = "access") -> Optional[Dict[str, Any]]:
        """
        Xác thực JWT token

        Args:
            token: JWT token cần xác thực
            token_type: Loại token (access hoặc refresh)

        Returns:
            Decoded payload nếu token hợp lệ, None nếu không
        """
        payload = JWTManager.decode_token(token)

        if payload and payload.get("type") == token_type:
            return payload

        return None


class SecurityUtils:
    """Các tiện ích bảo mật khác"""

    @staticmethod
    def generate_random_token(length: int = 32) -> str:
        """
        Tạo random token an toàn

        Args:
            length: Độ dài token

        Returns:
            Random token hex string
        """
        return secrets.token_hex(length)

    @staticmethod
    def generate_verification_code(length: int = 6) -> str:
        """
        Tạo mã xác thực số ngẫu nhiên

        Args:
            length: Độ dài mã (default: 6)

        Returns:
            Mã xác thực số
        """
        return ''.join([str(secrets.randbelow(10)) for _ in range(length)])

    @staticmethod
    def mask_email(email: str) -> str:
        """
        Ẩn một phần email để bảo mật

        Args:
            email: Email cần ẩn

        Returns:
            Email đã được ẩn (vd: u***@example.com)
        """
        if '@' not in email:
            return email

        local, domain = email.split('@')
        if len(local) <= 2:
            masked_local = local[0] + '*'
        else:
            masked_local = local[0] + '*' * (len(local) - 2) + local[-1]

        return f"{masked_local}@{domain}"

    @staticmethod
    def mask_phone(phone: str) -> str:
        """
        Ẩn một phần số điện thoại

        Args:
            phone: Số điện thoại cần ẩn

        Returns:
            Số điện thoại đã được ẩn (vd: ***-***-1234)
        """
        if len(phone) < 4:
            return phone

        return '*' * (len(phone) - 4) + phone[-4:]

    @staticmethod
    def sanitize_input(text: str) -> str:
        """
        Làm sạch input để tránh XSS và injection

        Args:
            text: Text cần làm sạch

        Returns:
            Text đã được làm sạch
        """
        # Loại bỏ các ký tự đặc biệt nguy hiểm
        dangerous_chars = ['<', '>', '"', "'", '&', ';']
        sanitized = text

        for char in dangerous_chars:
            sanitized = sanitized.replace(char, '')

        return sanitized.strip()


# Khởi tạo instances
password_hasher = PasswordHasher()
jwt_manager = JWTManager()
security_utils = SecurityUtils()