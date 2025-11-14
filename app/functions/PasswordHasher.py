import bcrypt
import re
import logging
from typing import Tuple, List
from app.core.config import get_config

logger = logging.getLogger(__name__)
config = get_config()


class PasswordHasher:
    """Quản lý mã hóa và xác thực password"""

    @staticmethod
    def hash_password(password: str, check_strength: bool = True) -> str:
        """
        Mã hóa password sử dụng bcrypt.
        Nếu check_strength=True, sẽ validate độ mạnh trước khi hash.

        Args:
            password: Password cần mã hóa
            check_strength: Có kiểm tra độ mạnh không

        Returns:
            Hashed password

        Raises:
            ValueError nếu password yếu
        """
        if check_strength:
            valid, errors = PasswordHasher.validate_password_strength(password)
            if not valid:
                raise ValueError(f"Password too weak: {errors}")

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
    def validate_password_strength(password: str) -> Tuple[bool, List[str]]:
        """
        Kiểm tra độ mạnh của password dựa trên config

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

        # Sử dụng regex từ config nếu có, mặc định là ký tự đặc biệt phổ biến
        special_chars_pattern = getattr(config, "PASSWORD_SPECIAL_PATTERN", r'[!@#$%^&*(),.?":{}|<>]')
        if config.PASSWORD_REQUIRE_SPECIAL and not re.search(special_chars_pattern, password):
            errors.append("Password must contain at least one special character")

        return len(errors) == 0, errors
