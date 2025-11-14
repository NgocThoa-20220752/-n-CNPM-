"""
Authentication Service
File: app/services/auth_service.py
Xử lý logic đăng ký, đăng nhập, xác thực
"""

import logging
from datetime import datetime
from sqlalchemy.orm import Session
from typing import Tuple
import uuid

from sqlalchemy import or_
from typing import cast
from app.models.Account import Account
from app.models.Users import Users
from app.models.Customers import Customers
from app.enum.RoleEnum import RoleEnum
from app.enum.StatusAccountEnum import StatusAccountEnum
from app.enum.GenderEnum import GenderEnum
from app.core.security import password_hasher, security_utils, jwt_manager
from app.enum.VerificationMethod import VerificationMethod
from app.exception import AlreadyExistsException, DuplicateEmailException, WeakPasswordException, \
    InvalidVerificationCodeException, VerificationCodeExpiredException, NotFoundException, TooManyRequestsException, \
    InvalidCredentialsException, AccountNotActiveException, AccountLockedException, AccountSuspendedException
from app.functions import verification_manager, email_service, sms_service
from app.schemas.req.AccountRequest import CustomerRegisterRequest

logger = logging.getLogger(__name__)


class AuthService:
    """Service xử lý authentication"""

    def __init__(self, db: Session):
        self.db = db

    # ==================== Customer Registration ====================

    def register_customer(
            self,
            request: CustomerRegisterRequest
    ) -> Tuple[Users, Account, Customers, dict]:
        """
        Đăng ký tài khoản khách hàng

        Returns:
            (user, account, customer, verification_info)
        """
        logger.info(f"Registering new customer: {request.username}")

        # Check username exists
        if self.db.query(Account).filter_by(username=request.username).first():
            raise AlreadyExistsException(
                message=f"Username '{request.username}' already exists",
                resource="username"
            )

        # Check email exists
        if self.db.query(Users).filter_by(email=request.email).first():
            raise DuplicateEmailException(str(request.email))

        # Check phone exists
        if self.db.query(Users).filter_by(phone_number=request.phone_number).first():
            raise AlreadyExistsException(
                message=f"Phone number already exists",
                resource="phone"
            )

        # Validate password strength
        is_strong, errors = password_hasher.validate_password_strength(request.password)
        if not is_strong:
            raise WeakPasswordException(
                message="Password does not meet requirements",
                requirements=errors
            )

        try:
            # Create User
            user = Users(
                full_name=request.full_name,
                email=request.email,
                phone_number=request.phone_number,
                dob=request.dob,
                gender=GenderEnum[request.gender.value.upper()],
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            self.db.add(user)
            self.db.flush()

            # Create Account (INACTIVE until verified)
            hashed_password = password_hasher.hash_password(request.password)
            account = Account(
                username=request.username,
                password_hash=hashed_password,
                role=RoleEnum.CUSTOMER,
                status=StatusAccountEnum.INACTIVE,  # Chưa active cho đến khi verify
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            self.db.add(account)
            self.db.flush()

            # Link User and Account
            user.account = account

            # Create Customer
            customer_id = f"CUST{datetime.now().strftime('%Y%m%d')}{str(uuid.uuid4())[:8].upper()}"
            customer = Customers(
                customer_id=customer_id,
                user_id=user.id
            )
            self.db.add(customer)

            self.db.commit()
            self.db.refresh(user)
            self.db.refresh(account)
            self.db.refresh(customer)

            # Send verification
            verification_info = self._send_verification(
                user=user,
                method=request.verification_method,
                purpose="registration"
            )

            logger.info(f"Customer registered successfully: {request.username}")

            return user, account, customer, verification_info

        except Exception as e:
            self.db.rollback()
            logger.error(f"Error registering customer: {str(e)}", exc_info=True)
            raise

    def verify_account(
            self,
            identifier: str,
            code: str
    ) -> Tuple[Users, Account]:
        """
        Xác thực tài khoản bằng mã verification

        Args:
            identifier: Email hoặc số điện thoại
            code: Mã xác thực
        """
        logger.info(f"Verifying account: {security_utils.mask_email(identifier)}")

        # Verify code
        result = verification_manager.verify_code(
            identifier=identifier,
            code=code,
            max_attempts=3
        )

        if not result['verified']:
            if 'attempts_left' in result:
                raise InvalidVerificationCodeException(
                    message="Invalid verification code",
                    attempts_left=result['attempts_left']
                )
            else:
                error = result.get('error', '')
                if 'expired' in error.lower():
                    raise VerificationCodeExpiredException()
                else:
                    raise InvalidVerificationCodeException()

        # Find user by email or phone

        user = cast(Users, self.db.query(Users)
                    .filter(or_(Users.email == identifier, Users.phone_number == identifier))
                    .first())

        if not user:
            raise NotFoundException("User not found", resource="user")

        # Activate account
        account = user.account
        account.status = StatusAccountEnum.ACTIVE
        account.updated_at = datetime.now()

        self.db.commit()
        self.db.refresh(user)
        self.db.refresh(account)

        # Send welcome email
        try:
            email_service.send_welcome_email(
                to_email=user.email,
                user_name=user.full_name
            )
        except Exception as e:
            logger.warning(f"Failed to send welcome email: {str(e)}")

        logger.info(f"Account verified successfully: {identifier}")

        user: Users = user # khai báo rõ kiểu
        account: Account = user.account  # khai báo rõ kiểu
        return user, account

    def resend_verification(
            self,
            identifier: str,
            method: VerificationMethod
    ) -> dict:
        """
        Gửi lại mã xác thực
        """
        logger.info(f"Resending verification to: {security_utils.mask_email(identifier)}")

        # Check rate limit
        if not verification_manager.check_rate_limit(identifier, cooldown=60):
            raise TooManyRequestsException(
                message="Please wait before requesting a new code",
                retry_after=60
            )

        # Find user
        user = cast(
            Users,
            self.db.query(Users)
            .filter(or_(Users.email == identifier, Users.phone_number == identifier))
            .first()
        )

        if not user:
            raise NotFoundException("User not found", resource="user")

        # Send verification
        return self._send_verification(user, method, "resend")

    # ==================== Login ====================

    def login(
            self,
            username: str,
            password: str
    ) -> Tuple[Users, Account, dict]:
        """
        Đăng nhập cho khách hàng
        """
        logger.info(f"Login attempt: {username}")

        # Get account
        account = self.db.query(Account).filter_by(username=username).first()

        if not account:
            raise InvalidCredentialsException("Invalid username or password")

        # Verify password
        if not password_hasher.verify_password(password, account.password_hash):
            raise InvalidCredentialsException("Invalid username or password")

        # Check role (only customer can login via this endpoint)
        if account.role != RoleEnum.CUSTOMER:
            raise InvalidCredentialsException("Invalid credentials for this login interface")

        # Get user
        user = account.user

        # Check account status
        account = cast(Account, self.db.query(Account).filter_by(username=username).first())

        # Generate tokens
        tokens = self._generate_tokens(user, account)

        logger.info(f"Login successful: {username}")


        return user, account, tokens

    def admin_login(
            self,
            username: str,
            password: str,
            role: RoleEnum
    ) -> Tuple[Users, Account, dict]:
        """
        Đăng nhập cho admin/employee
        """
        logger.info(f"Admin login attempt: {username} as {role}")

        # Get account
        account = self.db.query(Account).filter_by(username=username).first()

        if not account:
            raise InvalidCredentialsException("Invalid username or password")

        # Verify password
        if not password_hasher.verify_password(password, account.password_hash):
            raise InvalidCredentialsException("Invalid username or password")

        # Check role matches
        role_enum = RoleEnum[role.value.upper()]
        if account.role != role_enum:
            raise InvalidCredentialsException(
                f"Account does not have {role.value} role"
            )

        # Get user
        user = account.user

        # Check account status
        account = cast(Account, self.db.query(Account).filter_by(username=username).first())

        # Generate tokens
        tokens = self._generate_tokens(user, account)

        logger.info(f"Admin login successful: {username}")

        return user, account, tokens

    # ==================== Password Management ====================

    def change_password(
            self,
            user_id: int,
            old_password: str,
            new_password: str
    ) -> Account:
        """
        Đổi mật khẩu
        """
        logger.info(f"Changing password for user: {user_id}")

        # Get user and account
        user = self.db.query(Users).filter_by(id=user_id).first()
        if not user or not user.account:
            raise NotFoundException("User not found", resource="user")

        account = user.account

        # Verify old password
        if not password_hasher.verify_password(old_password, account.password_hash):
            raise InvalidCredentialsException("Current password is incorrect")

        # Validate new password
        is_strong, errors = password_hasher.validate_password_strength(new_password)
        if not is_strong:
            raise WeakPasswordException(
                message="New password does not meet requirements",
                requirements=errors
            )

        # Update password
        account.password_hash = password_hasher.hash_password(new_password)
        account.updated_at = datetime.now()

        self.db.commit()
        self.db.refresh(account)

        logger.info(f"Password changed successfully for user: {user_id}")

        return account

    def forgot_password(
            self,
            identifier: str,
            method: VerificationMethod
    ) -> dict:
        """
        Quên mật khẩu - gửi mã xác thực
        """
        logger.info(f"Forgot password request: {security_utils.mask_email(identifier)}")

        # Find user
        user = cast (
            Users,
            self.db.query(Users)
            .filter( or_ (Users.email == identifier) | (Users.phone_number == identifier) )
            .first()
        )
        if not user:
            # Don't reveal if user exists or not
            logger.warning(f"User not found for forgot password: {identifier}")
            return {
                "message": "If the account exists, a verification code will be sent"
            }

        # Send verification
        return self._send_verification(user, method, "password_reset")

    def reset_password(
            self,
            identifier: str,
            code: str,
            new_password: str
    ) -> Account:
        """
        Reset mật khẩu với mã xác thực
        """
        logger.info(f"Resetting password: {security_utils.mask_email(identifier)}")

        # Verify code
        result = verification_manager.verify_code(
            identifier=identifier,
            code=code,
            max_attempts=3
        )

        if not result['verified']:
            if 'attempts_left' in result:
                raise InvalidVerificationCodeException(
                    message="Invalid verification code",
                    attempts_left=result['attempts_left']
                )
            else:
                raise VerificationCodeExpiredException()

        # Find user
        user = cast(
            Users,
            self.db.query(Users)
            .filter( or_(Users.email == identifier) | (Users.phone_number == identifier))
            .first()
            )

        if not user or not user.account:
            raise NotFoundException("User not found", resource="user")

        # Validate new password
        is_strong, errors = password_hasher.validate_password_strength(new_password)
        if not is_strong:
            raise WeakPasswordException(
                message="Password does not meet requirements",
                requirements=errors
            )

        # Update password
        account = user.account
        account.password_hash = password_hasher.hash_password(new_password)
        account.updated_at = datetime.now()

        self.db.commit()
        self.db.refresh(account)

        logger.info(f"Password reset successfully: {identifier}")

        return account

    # ==================== Helper Methods ====================

    @staticmethod
    def _send_verification(
            user: Users,
            method: VerificationMethod,
            purpose: str
    ) -> dict:
        """
        Gửi mã xác thực qua email hoặc SMS
        """
        identifier = user.email if method == VerificationMethod.EMAIL else user.phone_number

        # Create verification code
        verification = verification_manager.create_verification(
            identifier=identifier,
            code_length=6,
            expires_in=600,  # 10 minutes
            user_id=str(user.id),
            metadata={"purpose": purpose}
        )

        code = verification['code']

        # Send via email or SMS
        if method == VerificationMethod.EMAIL:
            email_service.send_verification_email(
                to_email=user.email,
                verification_code=code,
                user_name=user.full_name
            )
        else:
            sms_service.send_verification_sms(
                to_phone=user.phone_number,
                verification_code=code
            )

        return {
            "method": method.value,
            "sent_to": security_utils.mask_email(
                identifier) if method == VerificationMethod.EMAIL else security_utils.mask_phone(identifier),
            "expires_in": verification['expires_in']
        }

    @staticmethod
    def _check_account_status( account: Account):
        """
        Kiểm tra trạng thái tài khoản
        """
        if account.status == StatusAccountEnum.INACTIVE:
            raise AccountNotActiveException(
                "Account is not active. Please verify your account."
            )
        elif account.status == StatusAccountEnum.LOCKED:
            raise AccountLockedException(
                message="Account has been locked",
                reason="Security violation"
            )
        elif account.status == StatusAccountEnum.SUSPENDED:
            raise AccountSuspendedException(
                message="Account has been suspended",
                reason="Policy violation"
            )

    @staticmethod
    def _generate_tokens( user: Users, account: Account) -> dict:
        """
        Tạo JWT tokens
        """
        payload = {
            "user_id": user.id,
            "username": account.username,
            "email": user.email,
            "role": account.role.value
        }

        access_token = jwt_manager.create_access_token(data=payload)
        refresh_token = jwt_manager.create_refresh_token(data={"user_id": user.id})

        from app.core.config import get_config
        config = get_config()

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": config.JWT_ACCESS_TOKEN_EXPIRES
        }