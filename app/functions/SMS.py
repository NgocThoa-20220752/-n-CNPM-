from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException
from typing import Optional, Dict
import logging
from datetime import datetime, timezone
from app.core.config import get_config
from app.core.security import security_utils

logger = logging.getLogger(__name__)
config = get_config()


class SMSService:
    """Service quản lý gửi SMS sử dụng Twilio"""

    def __init__(self):
        self.account_sid = config.TWILIO_ACCOUNT_SID
        self.auth_token = config.TWILIO_AUTH_TOKEN
        self.phone_number = config.TWILIO_PHONE_NUMBER
        self.verify_service_sid = config.TWILIO_VERIFY_SERVICE_SID

        # Khởi tạo Twilio client
        if self.account_sid and self.auth_token:
            try:
                self.client = Client(self.account_sid, self.auth_token)
                logger.info("Twilio SMS client initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Twilio client: {str(e)}")
                self.client = None
        else:
            logger.warning("Twilio credentials not configured")
            self.client = None

    def send_sms(
            self,
            to_phone: str,
            message: str,
            from_phone: Optional[str] = None
    ) -> Dict[str, any]:
        """
        Gửi SMS thông thường

        Args:
            to_phone: Số điện thoại người nhận (format: +84xxxxxxxxx)
            message: Nội dung tin nhắn
            from_phone: Số điện thoại gửi (optional, default từ config)

        Returns:
            Dict chứa thông tin kết quả gửi
        """
        if not self.client:
            logger.error("SMS client not initialized")
            return {
                "success": False,
                "error": "SMS service not configured"
            }

        try:
            # Chuẩn hóa số điện thoại
            to_phone = self._normalize_phone_number(to_phone)

            message_response = self.client.messages.create(
                body=message,
                from_=from_phone or self.phone_number,
                to=to_phone
            )

            logger.info(f"SMS sent successfully to {security_utils.mask_phone(to_phone)}")

            return {
                "success": True,
                "sid": message_response.sid,
                "status": message_response.status,
                "to": to_phone,
                "sent_at": datetime.now(timezone.utc).isoformat()
            }

        except TwilioRestException as e:
            logger.error(f"Twilio error sending SMS: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "error_code": e.code
            }
        except Exception as e:
            logger.error(f"Failed to send SMS: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

    def send_verification_sms(
            self,
            to_phone: str,
            verification_code: str
    ) -> Dict[str, any]:
        """
        Gửi SMS chứa mã xác thực

        Args:
            to_phone: Số điện thoại người nhận
            verification_code: Mã xác thực

        Returns:
            Dict chứa thông tin kết quả gửi
        """
        message = f"Mã xác thực của bạn là: {verification_code}. Mã có hiệu lực trong {config.SMS_VERIFICATION_CODE_EXPIRES // 60} phút."

        return self.send_sms(to_phone, message)

    def send_verification_with_twilio_verify(
            self,
            to_phone: str,
            channel: str = 'sms'
    ) -> Dict[str, any]:
        """
        Gửi mã xác thực sử dụng Twilio Verify API
        (Twilio tự động tạo và quản lý mã xác thực)

        Args:
            to_phone: Số điện thoại người nhận
            channel: Kênh gửi ('sms' hoặc 'call')

        Returns:
            Dict chứa thông tin kết quả
        """
        if not self.client or not self.verify_service_sid:
            logger.error("Twilio Verify service not configured")
            return {
                "success": False,
                "error": "Verify service not configured"
            }

        try:
            to_phone = self._normalize_phone_number(to_phone)

            verification = self.client.verify \
                .v2 \
                .services(self.verify_service_sid) \
                .verifications \
                .create(to=to_phone, channel=channel)

            logger.info(f"Verification code sent via {channel} to {security_utils.mask_phone(to_phone)}")

            return {
                "success": True,
                "sid": verification.sid,
                "status": verification.status,
                "to": to_phone,
                "channel": channel,
                "sent_at": datetime.now(timezone.utc).isoformat()
            }

        except TwilioRestException as e:
            logger.error(f"Twilio Verify error: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "error_code": e.code
            }
        except Exception as e:
            logger.error(f"Failed to send verification: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

    def verify_code_with_twilio_verify(
            self,
            to_phone: str,
            code: str
    ) -> Dict[str, any]:
        """
        Xác thực mã code với Twilio Verify API

        Args:
            to_phone: Số điện thoại
            code: Mã xác thực cần kiểm tra

        Returns:
            Dict chứa thông tin kết quả xác thực
        """
        if not self.client or not self.verify_service_sid:
            logger.error("Twilio Verify service not configured")
            return {
                "success": False,
                "error": "Verify service not configured"
            }

        try:
            to_phone = self._normalize_phone_number(to_phone)

            verification_check = self.client.verify \
                .v2 \
                .services(self.verify_service_sid) \
                .verification_checks \
                .create(to=to_phone, code=code)

            is_approved = verification_check.status == 'approved'

            if is_approved:
                logger.info(f"Verification successful for {security_utils.mask_phone(to_phone)}")
            else:
                logger.warning(f"Verification failed for {security_utils.mask_phone(to_phone)}")

            return {
                "success": True,
                "verified": is_approved,
                "status": verification_check.status,
                "to": to_phone
            }

        except TwilioRestException as e:
            logger.error(f"Twilio Verify check error: {str(e)}")
            return {
                "success": False,
                "verified": False,
                "error": str(e),
                "error_code": e.code
            }
        except Exception as e:
            logger.error(f"Failed to verify code: {str(e)}")
            return {
                "success": False,
                "verified": False,
                "error": str(e)
            }

    def send_otp_sms(
            self,
            to_phone: str,
            otp_code: str,
            purpose: str = "login"
    ) -> Dict[str, any]:
        """
        Gửi SMS OTP cho các mục đích khác nhau

        Args:
            to_phone: Số điện thoại người nhận
            otp_code: Mã OTP
            purpose: Mục đích (login, transaction, etc.)

        Returns:
            Dict chứa thông tin kết quả gửi
        """
        purpose_messages = {
            "login": f"Mã OTP đăng nhập của bạn: {otp_code}",
            "transaction": f"Mã xác thực giao dịch: {otp_code}",
            "password_reset": f"Mã đặt lại mật khẩu: {otp_code}",
            "registration": f"Mã đăng ký tài khoản: {otp_code}"
        }

        message = purpose_messages.get(
            purpose,
            f"Mã xác thực của bạn: {otp_code}"
        )
        message += f". Có hiệu lực {config.SMS_VERIFICATION_CODE_EXPIRES // 60} phút."

        return self.send_sms(to_phone, message)

    @staticmethod
    def _normalize_phone_number( phone: str) -> str:
        """
        Chuẩn hóa số điện thoại về format E.164 (+84xxxxxxxxx)

        Args:
            phone: Số điện thoại cần chuẩn hóa

        Returns:
            Số điện thoại đã chuẩn hóa
        """
        # Loại bỏ khoảng trắng và ký tự đặc biệt
        phone = ''.join(filter(lambda c: c.isdigit(), phone))

        # Nếu bắt đầu bằng 0, thay thế bằng +84 (Việt Nam)
        if phone.startswith('0'):
            phone = '+84' + phone[1:]
        elif not phone.startswith('+'):
            phone = '+84' + phone

        return phone

    def get_message_status(self, message_sid: str) -> Optional[Dict[str, any]]:
        """
        Kiểm tra trạng thái tin nhắn

        Args:
            message_sid: SID của tin nhắn

        Returns:
            Dict chứa thông tin trạng thái hoặc None
        """
        if not self.client:
            return None

        try:
            message = self.client.messages(message_sid).fetch()

            return {
                "sid": message.sid,
                "status": message.status,
                "to": message.to,
                "from": message.from_,
                "date_sent": message.date_sent.isoformat() if message.date_sent else None,
                "error_code": message.error_code,
                "error_message": message.error_message
            }

        except TwilioRestException as e:
            logger.error(f"Failed to fetch message status: {str(e)}")
            return None


class SMSVerificationManager:
    """Quản lý quy trình xác thực SMS"""

    def __init__(self):
        self.sms_service = SMSService()
        # Dictionary lưu trữ tạm thời thông tin xác thực
        # Trong production nên sử dụng Redis hoặc database
        self.verification_storage = {}

    def send_verification(
            self,
            phone: str,
            user_id: Optional[str] = None
    ) -> Dict[str, any]:
        """
        Gửi mã xác thực và lưu thông tin

        Args:
            phone: Số điện thoại
            user_id: ID người dùng (optional)

        Returns:
            Dict chứa thông tin kết quả
        """
        # Kiểm tra rate limit
        if not self._check_rate_limit(phone):
            return {
                "success": False,
                "error": "Too many attempts. Please try again later."
            }

        # Tạo mã xác thực
        code = security_utils.generate_verification_code(
            config.SMS_VERIFICATION_CODE_LENGTH
        )

        # Gửi SMS
        result = self.sms_service.send_verification_sms(phone, code)

        if result.get("success"):
            # Lưu thông tin xác thực
            self.verification_storage[phone] = {
                "code": code,
                "user_id": user_id,
                "created_at": datetime.now(timezone.utc),
                "attempts": 0,
                "verified": False
            }

        return result

    def verify_code(
            self,
            phone: str,
            code: str
    ) -> Dict[str, any]:
        """
        Xác thực mã code

        Args:
            phone: Số điện thoại
            code: Mã xác thực

        Returns:
            Dict chứa thông tin kết quả xác thực
        """
        verification = self.verification_storage.get(phone)

        if not verification:
            return {
                "success": False,
                "verified": False,
                "error": "No verification found for this phone number"
            }

        # Kiểm tra số lần thử
        if verification["attempts"] >= config.SMS_MAX_ATTEMPTS:
            return {
                "success": False,
                "verified": False,
                "error": "Maximum attempts exceeded"
            }

        # Kiểm tra thời gian hết hạn
        elapsed = (datetime.now(timezone.utc) - verification["created_at"]).total_seconds()
        if elapsed > config.SMS_VERIFICATION_CODE_EXPIRES:
            return {
                "success": False,
                "verified": False,
                "error": "Verification code expired"
            }

        # Tăng số lần thử
        verification["attempts"] += 1

        # Kiểm tra mã
        if verification["code"] == code:
            verification["verified"] = True
            return {
                "success": True,
                "verified": True,
                "user_id": verification.get("user_id")
            }
        else:
            return {
                "success": False,
                "verified": False,
                "error": "Invalid verification code",
                "attempts_left": config.SMS_MAX_ATTEMPTS - verification["attempts"]
            }

    def _check_rate_limit(self, phone: str) -> bool:
        """
        Kiểm tra rate limit cho việc gửi SMS

        Args:
            phone: Số điện thoại

        Returns:
            True nếu có thể gửi, False nếu vượt quá giới hạn
        """
        verification = self.verification_storage.get(phone)

        if not verification:
            return True

        elapsed = (datetime.now(timezone.utc) - verification["created_at"]).total_seconds()

        # Kiểm tra cooldown time
        if elapsed < config.SMS_RESEND_COOLDOWN:
            return False

        return True


# Singleton instances
sms_service = SMSService()
sms_verification_manager = SMSVerificationManager()