from pydantic import BaseModel,Field,EmailStr,field_validator
from datetime import date
from app.enum.RoleEnum import RoleEnum
from app.enum.GenderEnum import GenderEnum
from app.enum.VerificationMethod import VerificationMethod


class CustomerRegisterRequest(BaseModel):
    """Schema cho đăng ký khách hàng"""
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=8, max_length=100)
    full_name: str = Field(..., min_length=2, max_length=255)
    email: EmailStr
    phone_number: str = Field(..., min_length=10, max_length=20)
    dob: date
    gender: GenderEnum
    verification_method: VerificationMethod = VerificationMethod.EMAIL

    @field_validator('phone_number')
    def validate_phone(self, v):
        # Remove spaces and special characters
        cleaned = ''.join(ch for ch in str(v) if ch.isdigit())
        if not cleaned.startswith('0'):
            raise ValueError('Phone number must start with 0')
        if len(cleaned) < 10 or len(cleaned) > 11:
            raise ValueError('Phone number must be 10-11 digits')
        return cleaned

    @field_validator('dob')
    def validate_age(self, v):
        today = date.today()
        age = today.year - v.year - ((today.month, today.day) < (v.month, v.day))
        if age < 13:
            raise ValueError('Must be at least 13 years old')
        if age > 120:
            raise ValueError('Invalid date of birth')
        return v

class VerifyAccountRequest(BaseModel):
    """Schema cho xác thực tài khoản"""
    identifier: str = Field(..., description="Email or phone number")
    verification_code: str = Field(..., min_length=6, max_length=6)

class LoginRequest(BaseModel):
    """Schema cho đăng nhập"""
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=8, max_length=100)

class AdminLoginRequest(BaseModel):
    """Schema cho đăng nhập admin/employee"""
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=8, max_length=100)
    role: RoleEnum = Field(..., description="Role to login as (employee or admin)")

    @field_validator('role')
    def validate_role(self, v):
        if v == RoleEnum.CUSTOMER:
            raise ValueError('Cannot login as customer on admin interface')
        return v


class ChangePasswordRequest(BaseModel):
    """Schema cho đổi mật khẩu"""
    old_password: str = Field(..., min_length=8, max_length=100)
    new_password: str = Field(..., min_length=8, max_length=100)

    @field_validator('new_password')
    def validate_new_password(self, v, values):
        if 'old_password' in values and v == values['old_password']:
            raise ValueError('New password must be different from old password')
        return v


class ForgotPasswordRequest(BaseModel):
    """Schema cho quên mật khẩu"""
    identifier: str = Field(..., description="Email or phone number")
    verification_method: VerificationMethod = VerificationMethod.EMAIL


class ResetPasswordRequest(BaseModel):
    """Schema cho reset mật khẩu"""
    identifier: str = Field(..., description="Email or phone number")
    verification_code: str = Field(..., min_length=6, max_length=6)
    new_password: str = Field(..., min_length=8, max_length=100)


class ResendVerificationRequest(BaseModel):
    """Schema cho gửi lại mã xác thực"""
    identifier: str = Field(..., description="Email or phone number")
    verification_method: VerificationMethod = VerificationMethod.EMAIL
