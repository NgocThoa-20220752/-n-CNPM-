from datetime import datetime, timezone
from typing import Optional, Dict
import logging
from app.core.config import get_config
from app.functions.SecurityUtils import security_utils

logger = logging.getLogger(__name__)
config = get_config()


class VerificationManager:
    """
    Quản lý mã xác thực (OTP/Verification Code)
    Lưu trữ tạm thời trong memory (nên dùng Redis trong production)
    """

    def __init__(self):
        # Dictionary lưu trữ tạm thời
        # Format: {identifier: {code, created_at, attempts, verified}}
        self._storage = {}

    def create_verification(
            self,
            identifier: str,
            code_length: int = 6,
            expires_in: int = 300,
            user_id: Optional[str] = None,
            metadata: Optional[Dict] = None
    ) -> Dict[str, any]:
        """
        Tạo mã xác thực mới

        Args:
            identifier: Định danh (email hoặc phone)
            code_length: Độ dài mã
            expires_in: Thời gian hết hạn (seconds)
            user_id: ID người dùng (optional)
            metadata: Dữ liệu bổ sung (optional)

        Returns:
            Dict chứa code và thông tin
        """
        code = security_utils.generate_verification_code(code_length)

        self._storage[identifier] = {
            'code': code,
            'created_at': datetime.now(timezone.utc),
            'expires_in': expires_in,
            'attempts': 0,
            'verified': False,
            'user_id': user_id,
            'metadata': metadata or {}
        }

        logger.info(f"Verification code created for {identifier}")

        return {
            'code': code,
            'expires_in': expires_in,
            'created_at': datetime.now(timezone.utc).isoformat()
        }

    def verify_code(
            self,
            identifier: str,
            code: str,
            max_attempts: int = 3
    ) -> Dict[str, any]:
        """
        Xác thực mã code

        Args:
            identifier: Định danh
            code: Mã cần xác thực
            max_attempts: Số lần thử tối đa

        Returns:
            Dict chứa kết quả xác thực
        """
        verification = self._storage.get(identifier)

        if not verification:
            logger.warning(f"No verification found for {identifier}")
            return {
                'success': False,
                'verified': False,
                'error': 'No verification code found'
            }

        # Kiểm tra số lần thử
        if verification['attempts'] >= max_attempts:
            logger.warning(f"Max attempts exceeded for {identifier}")
            return {
                'success': False,
                'verified': False,
                'error': 'Maximum verification attempts exceeded'
            }

        # Kiểm tra thời gian hết hạn
        elapsed = (datetime.now(timezone.utc) - verification['created_at']).total_seconds()
        if elapsed > verification['expires_in']:
            logger.warning(f"Verification code expired for {identifier}")
            return {
                'success': False,
                'verified': False,
                'error': 'Verification code has expired'
            }

        # Tăng số lần thử
        verification['attempts'] += 1

        # Kiểm tra mã
        if verification['code'] == code:
            verification['verified'] = True
            logger.info(f"Verification successful for {identifier}")

            return {
                'success': True,
                'verified': True,
                'user_id': verification.get('user_id'),
                'metadata': verification.get('metadata')
            }
        else:
            logger.warning(f"Invalid verification code for {identifier}")
            return {
                'success': False,
                'verified': False,
                'error': 'Invalid verification code',
                'attempts_left': max_attempts - verification['attempts']
            }

    def is_verified(self, identifier: str) -> bool:
        """Kiểm tra xem đã xác thực chưa"""
        verification = self._storage.get(identifier)
        return verification and verification.get('verified', False)

    def check_rate_limit(
            self,
            identifier: str,
            cooldown: int = 60
    ) -> bool:
        """
        Kiểm tra rate limit (cooldown giữa các lần gửi)

        Args:
            identifier: Định danh
            cooldown: Thời gian chờ (seconds)

        Returns:
            True nếu có thể gửi, False nếu đang trong cooldown
        """
        verification = self._storage.get(identifier)

        if not verification:
            return True

        elapsed = (datetime.now(timezone.utc) - verification['created_at']).total_seconds()

        if elapsed < cooldown:
            logger.warning(f"Rate limit hit for {identifier}")
            return False

        return True

    def delete_verification(self, identifier: str):
        """Xóa mã xác thực"""
        if identifier in self._storage:
            del self._storage[identifier]
            logger.info(f"Verification deleted for {identifier}")

    def cleanup_expired(self):
        """
        Dọn dẹp các mã đã hết hạn
        Nên chạy định kỳ (ví dụ: mỗi giờ)
        """
        current_time = datetime.now(timezone.utc)
        expired_keys = []

        for identifier, verification in self._storage.items():
            elapsed = (current_time - verification['created_at']).total_seconds()
            if elapsed > verification['expires_in']:
                expired_keys.append(identifier)

        for key in expired_keys:
            del self._storage[key]

        if expired_keys:
            logger.info(f"Cleaned up {len(expired_keys)} expired verifications")

    def get_verification_info(self, identifier: str) -> Optional[Dict]:
        """Lấy thông tin verification (không bao gồm code)"""
        verification = self._storage.get(identifier)

        if not verification:
            return None

        elapsed = (datetime.now(timezone.utc) - verification['created_at']).total_seconds()

        return {
            'identifier': identifier,
            'created_at': verification['created_at'].isoformat(),
            'expires_in': verification['expires_in'],
            'time_remaining': max(0, verification['expires_in'] - elapsed),
            'attempts': verification['attempts'],
            'verified': verification['verified'],
            'user_id': verification.get('user_id')
        }


# Singleton instance
verification_manager = VerificationManager()