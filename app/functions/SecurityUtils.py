import secrets
import logging

logger = logging.getLogger(__name__)


class SecurityUtils:
    """Các tiện ích bảo mật"""

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
        dangerous_chars = ['<', '>', '"', "'", '&', ';']
        sanitized = text

        for char in dangerous_chars:
            sanitized = sanitized.replace(char, '')

        return sanitized.strip()

    @staticmethod
    def normalize_phone_number(phone: str, country_code: str = '+84') -> str:
        """
        Chuẩn hóa số điện thoại về format E.164

        Args:
            phone: Số điện thoại cần chuẩn hóa
            country_code: Mã quốc gia (default: +84 for Vietnam)

        Returns:
            Số điện thoại đã chuẩn hóa
        """
        # Loại bỏ khoảng trắng và ký tự đặc biệt
        phone = ''.join(filter(lambda c: c.isdigit(), phone))

        # Nếu bắt đầu bằng 0, thay thế bằng country code
        if phone.startswith('0'):
            phone = country_code + phone[1:]
        elif not phone.startswith('+'):
            phone = country_code + phone

        return phone


# Singleton instance
security_utils = SecurityUtils()