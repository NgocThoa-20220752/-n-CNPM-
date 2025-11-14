
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.Dependencies import get_current_user
from app.core import get_db

from app.models.Users import Users
from app.schemas.req.AccountRequest import CustomerRegisterRequest, ChangePasswordRequest, ForgotPasswordRequest, \
    ResetPasswordRequest, LoginRequest, VerifyAccountRequest, AdminLoginRequest, ResendVerificationRequest
from app.schemas.resp.AccountResponse import RegisterResponse, SuccessResponse, LoginResponse, TokenResponse
from app.schemas.resp.UserResponse import UserResponse
from app.services.AuthService import AuthService

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/register",
    response_model=RegisterResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Đăng ký tài khoản khách hàng"
)
async def register_customer(
        request: CustomerRegisterRequest,
        db: Session = Depends(get_db)
):
    """
    Đăng ký tài khoản khách hàng mới

    - Mặc định role là CUSTOMER
    - Gửi mã xác thực qua email hoặc SMS
    - Tài khoản INACTIVE cho đến khi verify
    """
    service = AuthService(db)
    user, account, customer, verification_info = service.register_customer(request)

    user_response = UserResponse(
        id=user.id,
        username=account.username,
        full_name=user.full_name,
        email=user.email,
        phone_number=user.phone_number,
        dob=user.dob,
        gender=user.gender.value,
        role=account.role.value,
        status=account.status.value,
        created_at=user.created_at,
        updated_at=user.updated_at
    )

    return RegisterResponse(
        message="Registration successful. Please check your email/SMS for verification code.",
        user=user_response,
        verification_method=verification_info['method']
    )


@router.post(
    "/verify",
    response_model=SuccessResponse,
    summary="Xác thực tài khoản"
)
async def verify_account(
        request: VerifyAccountRequest,
        db: Session = Depends(get_db)
):
    """
    Xác thực tài khoản bằng mã verification

    - Mã có hiệu lực 10 phút
    - Tối đa 3 lần thử
    """
    service = AuthService(db)
    user, account = service.verify_account(request.identifier, request.verification_code)

    return SuccessResponse(
        message="Account verified successfully. You can now login.",
        data={
            "username": account.username,
            "email": user.email
        }
    )


@router.post(
    "/resend-verification",
    response_model=SuccessResponse,
    summary="Gửi lại mã xác thực"
)
async def resend_verification(
        request: ResendVerificationRequest,
        db: Session = Depends(get_db)
):
    """
    Gửi lại mã xác thực

    - Rate limit: 1 phút giữa các lần gửi
    """
    service = AuthService(db)
    verification_info = service.resend_verification(
        request.identifier,
        request.verification_method
    )

    return SuccessResponse(
        message=f"Verification code sent via {verification_info['method']}",
        data=verification_info
    )


@router.post(
    "/login",
    response_model=LoginResponse,
    summary="Đăng nhập khách hàng"
)
async def login(
        request: LoginRequest,
        db: Session = Depends(get_db)
):
    """
    Đăng nhập cho khách hàng

    - Chỉ dành cho tài khoản có role CUSTOMER
    - Tài khoản phải đã được verify
    """
    service = AuthService(db)
    user, account, tokens = service.login(request.username, request.password)

    user_response = UserResponse(
        id=user.id,
        username=account.username,
        full_name=user.full_name,
        email=user.email,
        phone_number=user.phone_number,
        dob=user.dob,
        gender=user.gender.value,
        role=account.role.value,
        status=account.status.value,
        created_at=user.created_at,
        updated_at=user.updated_at
    )

    token_response = TokenResponse(**tokens)

    return LoginResponse(
        message="Login successful",
        user=user_response,
        tokens=token_response
    )


@router.post(
    "/admin/login",
    response_model=LoginResponse,
    summary="Đăng nhập admin/employee"
)
async def admin_login(
        request: AdminLoginRequest,
        db: Session = Depends(get_db)
):
    """
    Đăng nhập cho admin hoặc employee

    - Phải chọn role (admin hoặc employee)
    - Tài khoản được tạo bởi admin
    """
    service = AuthService(db)
    user, account, tokens = service.admin_login(
        request.username,
        request.password,
        request.role
    )

    user_response = UserResponse(
        id=user.id,
        username=account.username,
        full_name=user.full_name,
        email=user.email,
        phone_number=user.phone_number,
        dob=user.dob,
        gender=user.gender.value,
        role=account.role.value,
        status=account.status.value,
        created_at=user.created_at,
        updated_at=user.updated_at
    )

    token_response = TokenResponse(**tokens)

    return LoginResponse(
        message=f"Login successful as {request.role.value}",
        user=user_response,
        tokens=token_response
    )


@router.post(
    "/change-password",
    response_model=SuccessResponse,
    summary="Đổi mật khẩu"
)
async def change_password(
        request: ChangePasswordRequest,
        current_user: Users = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """
    Đổi mật khẩu (yêu cầu đăng nhập)

    - Phải nhập đúng mật khẩu hiện tại
    - Mật khẩu mới phải khác mật khẩu cũ
    - Gửi mã xác thực qua email/SMS
    """
    service = AuthService(db)
    service.change_password(
        current_user.id,
        request.old_password,
        request.new_password
    )

    return SuccessResponse(
        message="Password changed successfully"
    )


@router.post(
    "/forgot-password",
    response_model=SuccessResponse,
    summary="Quên mật khẩu"
)
async def forgot_password(
        request: ForgotPasswordRequest,
        db: Session = Depends(get_db)
):
    """
    Quên mật khẩu - gửi mã xác thực

    - Gửi mã qua email hoặc SMS
    - Không tiết lộ user có tồn tại hay không
    """
    service = AuthService(db)
    result = service.forgot_password(request.identifier, request.verification_method)

    return SuccessResponse(
        message="If the account exists, a verification code has been sent",
        data=result
    )


@router.post(
    "/reset-password",
    response_model=SuccessResponse,
    summary="Reset mật khẩu"
)
async def reset_password(
        request: ResetPasswordRequest,
        db: Session = Depends(get_db)
):
    """
    Reset mật khẩu với mã xác thực

    - Nhập mã xác thực nhận được
    - Nhập mật khẩu mới
    """
    service = AuthService(db)
    service.reset_password(
        request.identifier,
        request.verification_code,
        request.new_password
    )

    return SuccessResponse(
        message="Password reset successfully. You can now login with new password."
    )


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Lấy thông tin user hiện tại"
)
async def get_current_user_info(
        current_user: Users = Depends(get_current_user)
):
    """
    Lấy thông tin user đang đăng nhập

    - Yêu cầu JWT token hợp lệ
    """
    account = current_user.account

    return UserResponse(
        id=current_user.id,
        username=account.username,
        full_name=current_user.full_name,
        email=current_user.email,
        phone_number=current_user.phone_number,
        dob=current_user.dob,
        gender=current_user.gender.value,
        role=account.role.value,
        status=account.status.value,
        created_at=current_user.created_at,
        updated_at=current_user.updated_at
    )