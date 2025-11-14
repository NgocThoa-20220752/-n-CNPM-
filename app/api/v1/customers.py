"""
Customer Management Controller
API endpoints quản lý khách hàng
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.Dependencies import require_admin_or_employee, get_current_user, require_customer
from app.core import get_db

from app.models.Users import Users
from app.enum.StatusAccountEnum import StatusAccountEnum
from app.schemas.req.CustomerRequest import SearchCustomerRequest, UpdateCustomerStatusRequest, UpdateProfileRequest
from app.schemas.resp.AccountResponse import PaginatedResponse, SuccessResponse
from app.schemas.resp.UserResponse import UserResponse
from app.services.CustomerService import CustomerService

# Router cho admin/employee quản lý khách hàng
admin_router = APIRouter(prefix="/admin/customers", tags=["Customer Management (Admin)"])

# Router cho khách hàng tự quản lý
customer_router = APIRouter(prefix="/customer", tags=["Customer Profile"])


# ==================== Admin/Employee Routes ====================

@admin_router.get(
    "",
    response_model=PaginatedResponse,
    summary="Tìm kiếm khách hàng",
    dependencies=[Depends(require_admin_or_employee)]
)
async def search_customers(
        keyword: str = None,
        status: str = None,
        page: int = 1,
        page_size: int = 10,
        current_user: Users = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """
    Tìm kiếm khách hàng với phân trang (admin/employee)

    - Tìm theo username, tên, email, phone
    - Lọc theo status
    """
    request = SearchCustomerRequest(
        keyword=keyword,
        status=StatusAccountEnum(status) if status else None,
        page=page,
        page_size=page_size
    )

    service = CustomerService(db)
    customers, total = service.search_customers(request, current_user.id)

    # Convert to response
    data = []
    for user in customers:
        account = user.account
        customer = user.customer

        item = {
            "user": UserResponse(
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
            ).model_dump()
        }

        if customer:
            item["customer_id"] = customer.customer_id

        data.append(item)

    return PaginatedResponse(
        data=data,
        pagination={
            "page": request.page,
            "page_size": request.page_size,
            "total": total,
            "total_pages": (total + request.page_size - 1) // request.page_size
        }
    )


@admin_router.get(
    "/{customer_id}",
    response_model=SuccessResponse,
    summary="Lấy thông tin khách hàng",
    dependencies=[Depends(require_admin_or_employee)]
)
async def get_customer(
        customer_id: str,
        current_user: Users = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """
    Lấy thông tin chi tiết khách hàng
    """
    service = CustomerService(db)
    user, account, customer = service.get_customer_by_id(customer_id, current_user.id)

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

    return SuccessResponse(
        message="Customer retrieved successfully",
        data={
            "user": user_response.model_dump(),
            "customer_id": customer.customer_id
        }
    )


@admin_router.patch(
    "/{customer_id}/status",
    response_model=SuccessResponse,
    summary="Cập nhật trạng thái khách hàng",
    dependencies=[Depends(require_admin_or_employee)]
)
async def update_customer_status(
        customer_id: str,
        request: UpdateCustomerStatusRequest,
        current_user: Users = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """
    Cập nhật trạng thái khách hàng (admin/employee)

    - Có thể: active, inactive, suspended, locked
    - Ghi lại lý do thay đổi
    """
    service = CustomerService(db)
    user, account = service.update_customer_status(customer_id, request, current_user.id)

    return SuccessResponse(
        message=f"Customer status updated to {request.status.value}",
        data={
            "customer_id": customer_id,
            "new_status": account.status.value,
            "reason": request.reason
        }
    )


@admin_router.delete(
    "/{customer_id}",
    response_model=SuccessResponse,
    summary="Xóa khách hàng",
    dependencies=[Depends(require_admin_or_employee)]
)
async def delete_customer(
        customer_id: str,
        current_user: Users = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """
    Xóa khách hàng (soft delete - admin/employee)

    - Set status = INACTIVE
    """
    service = CustomerService(db)
    service.delete_customer(customer_id, current_user.id)

    return SuccessResponse(
        message="Customer deleted successfully"
    )


# ==================== Customer Self-Service Routes ====================

@customer_router.get(
    "/profile",
    response_model=SuccessResponse,
    summary="Lấy thông tin profile",
    dependencies=[Depends(require_customer)]
)
async def get_profile(
        current_user: Users = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """
    Khách hàng xem thông tin profile của mình
    """
    service = CustomerService(db)
    user, account, customer = service.get_profile(current_user.id)

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

    return SuccessResponse(
        message="Profile retrieved successfully",
        data={
            "user": user_response.model_dump(),
            "customer_id": customer.customer_id
        }
    )


@customer_router.put(
    "/profile",
    response_model=SuccessResponse,
    summary="Cập nhật thông tin cá nhân",
    dependencies=[Depends(require_customer)]
)
async def update_profile(
        request: UpdateProfileRequest,
        current_user: Users = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """
    Khách hàng cập nhật thông tin cá nhân

    - Có thể cập nhật: tên, email, phone, dob, gender
    - Email và phone phải unique
    """
    service = CustomerService(db)
    user, account = service.update_profile(current_user.id, request)

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

    return SuccessResponse(
        message="Profile updated successfully",
        data={"user": user_response.model_dump()}
    )


@customer_router.delete(
    "/account",
    response_model=SuccessResponse,
    summary="Xóa tài khoản",
    dependencies=[Depends(require_customer)]
)
async def delete_own_account(
        password: str,
        current_user: Users = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """
    Khách hàng xóa tài khoản của chính mình

    - Phải xác thực bằng password
    - Soft delete (set status = INACTIVE)
    """
    service = CustomerService(db)
    service.delete_own_account(current_user.id, password)

    return SuccessResponse(
        message="Account deleted successfully. We're sorry to see you go."
    )