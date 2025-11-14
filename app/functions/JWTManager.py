import jwt
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
import logging
from app.core.config import get_config

logger = logging.getLogger(__name__)
config = get_config()


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
        except jwt.ExpiredSignatureError:
            logger.warning("Token has expired")
            return None
        except jwt.InvalidTokenError as e:
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


# Singleton instance
jwt_manager = JWTManager()