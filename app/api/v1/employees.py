"""
Employee Management Controller
API endpoints quản lý nhân viên (Admin only)
"""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.Dependencies import require_admin, get_current_user
from app.core import get_db

from app.models.Users import Users
from app.enum.RoleEnum import RoleEnum
from app.enum.StatusAccountEnum import StatusAccountEnum
from app.schemas.req.EmployeeRequest import CreateEmployeeRequest, SearchEmployeeRequest, UpdateEmployeeRequest
from app.schemas.resp.AccountResponse import PaginatedResponse, SuccessResponse
from app.schemas.resp.UserResponse import UserResponse
from app.services.EmployeeService import EmployeeService

router = APIRouter(prefix="/admin/employees", tags=["Employee Management"])


@router.post(
    "",
    response_model=SuccessResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Tạo tài khoản nhân viên/admin",
    dependencies=[Depends(require_admin)]
)
async def create_employee(
        request: CreateEmployeeRequest,
        current_user: Users = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """
    Tạo tài khoản nhân viên hoặc admin (chỉ admin)

    - Tạo employee: cần salary và hire_date
    - Tạo admin: không cần salary và hire_date
    - Tài khoản ACTIVE ngay lập tức
    - Không cần verify
    """
    service = EmployeeService(db)
    user, account, employee, admin = service.create_employee(request, current_user.id)

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

    data = {"user": user_response.model_dump()}


    if employee:
        data["employee_id"] = employee.employee_id
        data["salary"] = float(employee.salary)
        data["hire_date"] = str(employee.hire_date)
    elif admin:
        data["admin_id"] = admin.admin_id

    return SuccessResponse(
        message=f"{request.role.value.capitalize()} account created successfully",
        data=data
    )


@router.get(
    "",
    response_model=PaginatedResponse,
    summary="Tìm kiếm nhân viên",
    dependencies=[Depends(require_admin)]
)

async def search_employees(
        keyword: str = None,
        role: str = None,
        account_status: str = None,
        page: int = 1,
        page_size: int = 10,
        current_user: Users = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """
    Tìm kiếm nhân viên với phân trang

    - Tìm theo username, tên, email
    - Lọc theo role (employee/admin)
    - Lọc theo status
    """

    request = SearchEmployeeRequest(
        keyword=keyword,
        role=RoleEnum(role) if role else None,
        status=StatusAccountEnum(status) if account_status  else None,
        page=page,
        page_size=page_size
    )

    service = EmployeeService(db)
    employees, total = service.search_employees(request, current_user.id)

    # Convert to response
    data = []
    for user in employees:
        account = user.account
        employee = user.employee
        admin = user.admin

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

        if employee:
            item["employee_id"] = employee.employee_id
            item["salary"] = float(employee.salary) if employee.salary else None
            item["hire_date"] = str(employee.hire_date) if employee.hire_date else None
        elif admin:
            item["admin_id"] = admin.admin_id

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


@router.get(
    "/{employee_id}",
    response_model=SuccessResponse,
    summary="Lấy thông tin nhân viên",
    dependencies=[Depends(require_admin)]
)
async def get_employee(
        employee_id: str,
        current_user: Users = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """
    Lấy thông tin chi tiết nhân viên
    """
    service = EmployeeService(db)
    user, account, employee, admin = service.get_employee_by_id(employee_id, current_user.id)

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

    data = {"user": user_response.model_dump()}

    if employee:
        data["employee_id"] = employee.employee_id
        data["salary"] = float(employee.salary) if employee.salary else None
        data["hire_date"] = str(employee.hire_date) if employee.hire_date else None
    elif admin:
        data["admin_id"] = admin.admin_id

    return SuccessResponse(
        message="Employee retrieved successfully",
        data=data
    )


@router.put(
    "/{employee_id}",
    response_model=SuccessResponse,
    summary="Cập nhật thông tin nhân viên",
    dependencies=[Depends(require_admin)]
)
async def update_employee(
        employee_id: str,
        request: UpdateEmployeeRequest,
        current_user: Users = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """
    Cập nhật thông tin nhân viên (chỉ admin)

    - Có thể cập nhật: thông tin cá nhân, salary, status
    """
    service = EmployeeService(db)
    user, account, employee = service.update_employee(employee_id, request, current_user.id)

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

    data = {"user": user_response.model_dump()}

    if employee:
        data["employee_id"] = employee.employee_id
        data["salary"] = float(employee.salary) if employee.salary else None
        data["hire_date"] = str(employee.hire_date) if employee.hire_date else None

    return SuccessResponse(
        message="Employee updated successfully",
        data=data
    )


@router.delete(
    "/{employee_id}",
    response_model=SuccessResponse,
    summary="Xóa nhân viên",
    dependencies=[Depends(require_admin)]
)
async def delete_employee(
        employee_id: str,
        current_user: Users = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """
    Xóa nhân viên (soft delete - chỉ admin)

    - Không thể xóa chính mình
    - Set status = INACTIVE
    """
    service = EmployeeService(db)
    service.delete_employee(employee_id, current_user.id)

    return SuccessResponse(
        message="Employee deleted successfully"
    )