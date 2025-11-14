"""
Customer Management Service
Xử lý quản lý khách hàng và profile
"""

import logging
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, cast, String
from typing import List, Tuple
from typing import cast
from app.models.Account import Account
from app.models.Users import Users
from app.models.Customers import Customers
from app.enum.RoleEnum import RoleEnum
from app.enum.StatusAccountEnum import StatusAccountEnum
from app.enum.GenderEnum import GenderEnum

from app.exception import (
    NotFoundException,
    AlreadyExistsException,
    DuplicateEmailException,
    PermissionDeniedException
)
from app.schemas.req.CustomerRequest import SearchCustomerRequest, UpdateCustomerStatusRequest, UpdateProfileRequest

logger = logging.getLogger(__name__)


class CustomerService:
    """Service quản lý khách hàng"""

    def __init__(self, db: Session):
        self.db = db

    # ==================== Customer Management (Admin/Employee) ====================

    def search_customers(
            self,
            request: SearchCustomerRequest,
            searcher_user_id: int
    ) -> Tuple[List, int]:
        """
        Tìm kiếm khách hàng (admin/employee)

        Returns:
            (customers_list, total_count)
        """
        logger.info(f"Searching customers with keyword: {request.keyword}")

        # Verify searcher is admin or employee
        searcher = self.db.query(Users).filter_by(id=searcher_user_id).first()
        if not searcher or not searcher.account:
            raise PermissionDeniedException("Unauthorized")

        if searcher.account.role not in [RoleEnum.ADMIN, RoleEnum.EMPLOYEE]:
            raise PermissionDeniedException("Only admin and employee can search customers")

        # Build query
        query = self.db.query(Users).join(Account).filter(
            cast(Account.role, String) == RoleEnum.CUSTOMER.value
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

        if request.status:
            query = query.filter(cast(Account.status, String) == request.status.value)

        # Get total count
        total = query.count()

        # Apply pagination
        offset = (request.page - 1) * request.page_size
        customers = query.offset(offset).limit(request.page_size).all()

        logger.info(f"Found {total} customers")

        return customers, total

    def get_customer_by_id(
            self,
            customer_id: str,
            requester_user_id: int
    ) -> Tuple[Users, Account, Customers]:
        """
        Lấy thông tin chi tiết khách hàng
        """
        logger.info(f"Getting customer: {customer_id}")

        # Verify requester
        requester: Users | None = self.db.query(Users).filter_by(id=requester_user_id).first()
        if not requester or not requester.account:
            raise PermissionDeniedException("Unauthorized")

        # Find customer
        customer: Customers | None = self.db.query(Customers).filter_by(customer_id=customer_id).first()
        if not customer:
            raise NotFoundException(
                message="Customer not found",
                resource="customer",
                resource_id=customer_id
            )

        user: Users = customer.user  # khai báo rõ kiểu
        account: Account = user.account  # khai báo rõ kiểu

        return user, account, customer

    def update_customer_status(
            self,
            customer_id: str,
            request: UpdateCustomerStatusRequest,
            updater_user_id: int
    ) -> Tuple[Users, Account]:
        """
        Cập nhật trạng thái khách hàng (admin/employee)
        """
        logger.info(f"Updating customer status: {customer_id} to {request.status}")

        # Verify updater is admin or employee
        updater = self.db.query(Users).filter_by(id=updater_user_id).first()
        if not updater or not updater.account:
            raise PermissionDeniedException("Unauthorized")

        if updater.account.role not in [RoleEnum.ADMIN, RoleEnum.EMPLOYEE]:
            raise PermissionDeniedException("Only admin and employee can update customer status")

        # Find customer
        customer = self.db.query(Customers).filter_by(customer_id=customer_id).first()

        if not customer:
            raise NotFoundException(
                message="Customer not found",
                resource="customer",
                resource_id=customer_id
            )

        user = customer.user
        account = user.account

        try:
            # Update status
            old_status = account.status.value
            account.status = StatusAccountEnum[request.status.value.upper()]
            account.updated_at = datetime.now()

            self.db.commit()
            self.db.refresh(account)

            logger.info(
                f"Customer status updated: {customer_id} from {old_status} to {request.status.value}",
                extra={
                    "customer_id": customer_id,
                    "old_status": old_status,
                    "new_status": request.status.value,
                    "reason": request.reason,
                    "updated_by": updater_user_id
                }
            )

            return user, account

        except Exception as e:
            self.db.rollback()
            logger.error(f"Error updating customer status: {str(e)}", exc_info=True)
            raise

    def delete_customer(
            self,
            customer_id: str,
            deleter_user_id: int
    ):
        """
        Xóa khách hàng (soft delete - admin/employee)
        """
        logger.info(f"Deleting customer: {customer_id}")

        # Verify deleter is admin or employee
        deleter = self.db.query(Users).filter_by(id=deleter_user_id).first()
        if not deleter or not deleter.account:
            raise PermissionDeniedException("Unauthorized")

        if deleter.account.role not in [RoleEnum.ADMIN, RoleEnum.EMPLOYEE]:
            raise PermissionDeniedException("Only admin and employee can delete customer")

        # Find customer
        customer = self.db.query(Customers).filter_by(customer_id=customer_id).first()

        if not customer:
            raise NotFoundException(
                message="Customer not found",
                resource="customer",
                resource_id=customer_id
            )

        user = customer.user
        account = user.account

        try:
            # Soft delete
            account.status = StatusAccountEnum.INACTIVE
            account.updated_at = datetime.now()

            self.db.commit()

            logger.info(
                f"Customer deleted: {customer_id}",
                extra={
                    "customer_id": customer_id,
                    "deleted_by": deleter_user_id
                }
            )

        except Exception as e:
            self.db.rollback()
            logger.error(f"Error deleting customer: {str(e)}", exc_info=True)
            raise

    # ==================== Customer Self-Service ====================

    def update_profile(
            self,
            user_id: int,
            request: UpdateProfileRequest
    ) -> Tuple[Users, Account]:
        """
        Khách hàng cập nhật thông tin cá nhân
        """
        logger.info(f"Customer updating profile: {user_id}")

        # Find user
        user = cast(Users, self.db.query(Users).filter_by(id=user_id).first())

        if not user or not user.account:
            raise NotFoundException("User not found", resource="user")

        # Verify is customer
        if user.account.role != RoleEnum.CUSTOMER:
            raise PermissionDeniedException("Only customers can use this endpoint")

        try:
            # Update user info
            if request.full_name:
                user.full_name = request.full_name

            if request.email:
                # Check email not taken by others
                existing = self.db.query(Users).filter(
                    and_(
                        Users.email == request.email,
                        Users.id != user.id
                    )
                ).first()

                if existing:
                    raise DuplicateEmailException(str(request.email))
                user.email = request.email

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

            self.db.commit()
            self.db.refresh(user)

            logger.info(f"Profile updated successfully: {user_id}")

            user: Users = user

            return user, user.account

        except Exception as e:
            self.db.rollback()
            logger.error(f"Error updating profile: {str(e)}", exc_info=True)
            raise

    def delete_own_account(
            self,
            user_id: int,
            password: str
    ):
        """
        Khách hàng xóa tài khoản của chính mình
        """
        logger.info(f"Customer deleting own account: {user_id}")

        # Find user
        user = self.db.query(Users).filter_by(id=user_id).first()

        if not user or not user.account:
            raise NotFoundException("User not found", resource="user")

        # Verify is customer
        if user.account.role != RoleEnum.CUSTOMER:
            raise PermissionDeniedException("Only customers can delete their own account")

        # Verify password
        from app.functions import PasswordHasher
        if not PasswordHasher.verify_password(password, user.account.password_hash):
            from app.exception import InvalidCredentialsException
            raise InvalidCredentialsException("Password is incorrect")

        try:
            # Soft delete
            account = user.account
            account.status = StatusAccountEnum.INACTIVE
            account.updated_at = datetime.now()

            self.db.commit()

            logger.info(
                f"Account deleted by owner: {user_id}",
                extra={
                    "user_id": user_id,
                    "email": user.email
                }
            )

        except Exception as e:
            self.db.rollback()
            logger.error(f"Error deleting own account: {str(e)}", exc_info=True)
            raise

    def get_profile(
            self,
            user_id: int
    ) -> Tuple[Users, Account, Customers]:
        """
        Lấy thông tin profile của khách hàng
        """
        logger.info(f"Getting profile: {user_id}")

        user = self.db.query(Users).filter_by(id=user_id).first()

        if not user or not user.account:
            raise NotFoundException("User not found", resource="user")

        if user.account.role != RoleEnum.CUSTOMER:
            raise PermissionDeniedException("Only customers can access this endpoint")

        customer = user.customer
        if not customer:
            raise NotFoundException("Customer record not found", resource="customer")

        user = cast(Users, user)
        customer: Customers = user.customer

        return user, user.account, customer