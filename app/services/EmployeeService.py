import logging
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import or_ , and_, cast, String
from typing import List, Tuple, Optional
import uuid
from app.models.Account import Account
from app.models.Users import Users
from app.models.Employees import Employees
from app.models.Admin import Admin
from app.enum.RoleEnum import RoleEnum
from app.enum.StatusAccountEnum import StatusAccountEnum
from app.enum.GenderEnum import GenderEnum

from app.functions import PasswordHasher
from app.exception import (
    NotFoundException,
    AlreadyExistsException,
    WeakPasswordException,
    DuplicateEmailException,
    InvalidInputException,
    PermissionDeniedException
)
from app.schemas.req.EmployeeRequest import CreateEmployeeRequest, UpdateEmployeeRequest, SearchEmployeeRequest

logger = logging.getLogger(__name__)


class EmployeeService:
    """Service quản lý nhân viên"""

    def __init__(self, db: Session):
        self.db = db

    def create_employee(
            self,
            request: CreateEmployeeRequest,
            created_by_user_id: int
    ) -> Tuple[Users, Account, Optional[Employees], Optional[Admin]]:
        """
        Tạo tài khoản nhân viên/admin (chỉ admin được phép)

        Returns:
            (user, account, employee, admin)
        """
        logger.info(f"Creating employee account: {request.username}")

        # Verify creator is admin
        creator = self.db.query(Users).filter_by(id=created_by_user_id).first()
        if not creator or not creator.account or creator.account.role != RoleEnum.ADMIN:
            raise PermissionDeniedException("Only admin can create employee accounts")

        # Check username exists
        if self.db.query(Account).filter_by(username=request.username).first():
            raise AlreadyExistsException(
                message=f"Username '{request.username}' already exists",
                resource="username"
            )

        # Check email exists
        email: str = str(request.email)
        if self.db.query(Users).filter_by(email=email).first():
            raise DuplicateEmailException(email)

        # Check phone exists
        if self.db.query(Users).filter_by(phone_number=request.phone_number).first():
            raise AlreadyExistsException(
                message=f"Phone number already exists",
                resource="phone"
            )

        # Validate password
        is_strong, errors = PasswordHasher.validate_password_strength(request.password)
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

            # Create Account (ACTIVE by default for employee/admin)
            hashed_password = PasswordHasher.hash_password(request.password)
            role_enum = RoleEnum[request.role.value.upper()]

            account = Account(
                username=request.username,
                password_hash=hashed_password,
                role=role_enum,
                status=StatusAccountEnum.ACTIVE,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            self.db.add(account)
            self.db.flush()

            # Link User and Account
            user.account = account

            employee = None
            admin = None

            # Create Employee or Admin record
            if request.role == RoleEnum.EMPLOYEE:
                employee_id = f"EMP{datetime.now().strftime('%Y%m%d')}{str(uuid.uuid4())[:8].upper()}"
                employee = Employees(
                    employee_id=employee_id,
                    user_id=user.id,
                    salary=request.salary,
                    hire_date=request.hire_date or datetime.now().date()
                )
                self.db.add(employee)
            else:  # ADMIN
                admin_id = f"ADM{datetime.now().strftime('%Y%m%d')}{str(uuid.uuid4())[:8].upper()}"
                admin = Admin(
                    admin_id=admin_id,
                    user_id=user.id
                )
                self.db.add(admin)

            self.db.commit()
            self.db.refresh(user)
            self.db.refresh(account)

            if employee:
                self.db.refresh(employee)
            if admin:
                self.db.refresh(admin)

            logger.info(f"Employee created successfully: {request.username}")

            return user, account, employee, admin

        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating employee: {str(e)}", exc_info=True)
            raise

    def update_employee(
            self,
            employee_id: str,
            request: UpdateEmployeeRequest,
            updated_by_user_id: int
    ) -> Tuple[Users, Account, Optional[Employees]]:
        """
        Cập nhật thông tin nhân viên
        """
        logger.info(f"Updating employee: {employee_id}")

        # Verify updater is admin
        updater = self.db.query(Users).filter_by(id=updated_by_user_id).first()
        if not updater or not updater.account or updater.account.role != RoleEnum.ADMIN:
            raise PermissionDeniedException("Only admin can update employee")

        # Find employee
        employee = self.db.query(Employees).filter_by(employee_id=employee_id).first()
        admin = None

        if not employee:
            # Try finding admin
            admin = self.db.query(Admin).filter_by(admin_id=employee_id).first()
            if not admin:
                raise NotFoundException(
                    message="Employee not found",
                    resource="employee",
                    resource_id=employee_id
                )

        user = employee.user if employee else admin.user
        account = user.account

        try:
            # Update user info
            if request.full_name:
                user.full_name = request.full_name
            if request.email:
                existing = (
                    self.db.query(Users)
                    .filter(
                        and_(
                            Users.email == request.email,
                            Users.id != user.id
                        )
                    )
                    .first()
                )
                email: str = str(request.email)  # ép kiểu EmailStr -> str
                if existing:
                    raise DuplicateEmailException(email)

                user.email = email

            if request.phone_number:
                # Check phone not taken by others
                existing = self.db.query(Users).filter(
                    and_(
                        Users.phone_number == request.phone_number,
                        Users.id != user.id
                    )
                ).first()
                if existing:
                    raise AlreadyExistsException(
                        message="Phone number already exists",
                        resource="phone"
                    )
                user.phone_number = request.phone_number

            if request.dob:
                user.dob = request.dob
            if request.gender:
                user.gender = GenderEnum[request.gender.value.upper()]

            user.updated_at = datetime.now()

            # Update employee specific info
            if employee and request.salary is not None:
                employee.salary = request.salary

            # Update account status
            if request.status:
                account.status = StatusAccountEnum[request.status.value.upper()]
                account.updated_at = datetime.now()

            self.db.commit()
            self.db.refresh(user)
            self.db.refresh(account)
            if employee:
                self.db.refresh(employee)

            logger.info(f"Employee updated successfully: {employee_id}")

            return user, account, employee

        except Exception as e:
            self.db.rollback()
            logger.error(f"Error updating employee: {str(e)}", exc_info=True)
            raise

    def delete_employee(
            self,
            employee_id: str,
            deleted_by_user_id: int
    ):
        """
        Xóa nhân viên (soft delete - change status to INACTIVE)
        """
        logger.info(f"Deleting employee: {employee_id}")

        # Verify deleter is admin
        deleter = self.db.query(Users).filter_by(id=deleted_by_user_id).first()
        if not deleter or not deleter.account or deleter.account.role != RoleEnum.ADMIN:
            raise PermissionDeniedException("Only admin can delete employee")

        # Find employee
        employee = self.db.query(Employees).filter_by(employee_id=employee_id).first()
        admin = None

        if not employee:
            admin = self.db.query(Admin).filter_by(admin_id=employee_id).first()
            if not admin:
                raise NotFoundException(
                    message="Employee not found",
                    resource="employee",
                    resource_id=employee_id
                )

        user = employee.user if employee else admin.user
        account = user.account

        # Cannot delete yourself
        if user.id == deleted_by_user_id:
            raise InvalidInputException("Cannot delete your own account")

        try:
            # Soft delete - set status to INACTIVE
            account.status = StatusAccountEnum.INACTIVE
            account.updated_at = datetime.now()

            self.db.commit()

            logger.info(f"Employee deleted successfully: {employee_id}")

        except Exception as e:
            self.db.rollback()
            logger.error(f"Error deleting employee: {str(e)}", exc_info=True)
            raise

    def search_employees(
            self,
            request: SearchEmployeeRequest,
            searcher_user_id: int
    ) -> Tuple[List, int]:
        """
        Tìm kiếm nhân viên với phân trang

        Returns:
            (employees_list, total_count)
        """
        logger.info(f"Searching employees with keyword: {request.keyword}")

        # Verify searcher is admin or employee
        searcher = self.db.query(Users).filter_by(id=searcher_user_id).first()
        if not searcher or not searcher.account:
            raise PermissionDeniedException("Unauthorized")

        if searcher.account.role not in [RoleEnum.ADMIN, RoleEnum.EMPLOYEE]:
            raise PermissionDeniedException("Only admin and employee can search employees")

        # Build query
        query = self.db.query(Users).join(Account).filter(
            Account.role.in_([RoleEnum.EMPLOYEE, RoleEnum.ADMIN])
        )

        # Apply filters
        if request.keyword:
            keyword = f"%{request.keyword}%"
            query = query.filter(
                or_(
                    Account.username.like(keyword),
                    Users.full_name.like(keyword),
                    Users.email.like(keyword),
                    Users.phone_number.like(keyword)
                )
            )

        if request.role:
            query = query.filter(cast(Account.role, String) == request.role.value)

        if request.status:
            query = query.filter(cast(Account.status, String) == request.status.value)

        # Get total count
        total = query.count()

        # Apply pagination
        offset = (request.page - 1) * request.page_size
        employees = query.offset(offset).limit(request.page_size).all()

        logger.info(f"Found {total} employees")

        return employees, total

    def get_employee_by_id(
            self,
            employee_id: str,
            requester_user_id: int
    ) -> Tuple[Users, Account, Optional[Employees], Optional[Admin]]:
        """
        Lấy thông tin chi tiết nhân viên
        """
        logger.info(f"Getting employee: {employee_id}")

        # Verify requester
        requester = self.db.query(Users).filter_by(id=requester_user_id).first()
        if not requester or not requester.account:
            raise PermissionDeniedException("Unauthorized")

        # Find employee
        employee = self.db.query(Employees).filter_by(employee_id=employee_id).first()
        admin = None

        if not employee:
            admin = self.db.query(Admin).filter_by(admin_id=employee_id).first()
            if not admin:
                raise NotFoundException(
                    message="Employee not found",
                    resource="employee",
                    resource_id=employee_id
                )

        user = employee.user if employee else admin.user
        account = user.account

        return user, account, employee, admin