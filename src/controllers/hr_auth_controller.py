from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from models.db.flow_wise.schema import Company, HRUser
from models.enums.hr_account_status_enum import HRAccountStatus
from models.enums.hr_role_enum import HRRole
from helpers import create_access_token

from repositories import HRUserRepository,CompanyRepository
from helpers import Settings, burn_dummy_verify,hash_password, pwd_context, verify_password
from schema import AdminRegisterRequest,TokenResponse,PasswordField,ChangePasswordRequest
import logging 


class HRAuthController:
    def __init__(self, session: AsyncSession,settings:Settings):
        self.session = session
        self.hr_accounts = HRUserRepository(session)
        self.companies = CompanyRepository(session)
        self.settings = settings



    def _token_for(self, user: HRUser) -> TokenResponse:
        token, expires_in = create_access_token(
            hr_id=user.id,
            role=user.role,
            company_id=user.company_id,
            token_version=user.token_version,
        )
        return TokenResponse(access_token=token, expires_in=expires_in, role=user.role)

    async def register_admin(self,data: AdminRegisterRequest) -> TokenResponse:
        """Create a company and its HR Admin in one transaction."""

        # Check whether admin registration is enabled
        print(data)
        if not self.settings.ALLOW_ADMIN_REGISTRATION:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin registration is closed"
            )

        # Normalize emails
        admin_email = str(data.admin.email).strip().lower()

        company_email = (
            str(data.company.email).strip().lower()
            if data.company.email
            else None
        )

        # Check for existing company and accounts
        company_name = await self.companies.get_company_by_name(data.company.company_name)
        if company_name:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="A company with this name already exists"
            )

        
        if company_email and await self.companies.get_company_by_email(company_email):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="A company with this email already exists"
            )

        if await self.hr_accounts.get_by_email(admin_email):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="An account with this email already exists"
            )

        # Hash password
        password_hash = hash_password(data.admin.password)

        try:
            # Create company
            company = await self.companies.create_company(
                Company(
                    company_name=data.company.company_name,
                    description=data.company.description,
                    address=data.company.address,
                    phone=data.company.phone,
                    email=company_email,
                )
            )

            # Create HR Admin
            admin = await self.hr_accounts.create_hr_user(
                HRUser(
                    company_id=company.id,
                    full_name=data.admin.full_name,
                    email=admin_email,
                    password=password_hash,
                    role=HRRole.ADMIN,
                    status=HRAccountStatus.ACTIVE,
                    token_version=0
                )
            )

            await self.session.commit()

        except Exception:
            await self.session.rollback()
            raise 

        return self._token_for(admin)

    async def login(self,email: str,password: str) -> TokenResponse:
        email = email.strip().lower()
        user = await self.hr_accounts.get_by_email(email)

        if user is None:
            burn_dummy_verify(password)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )

        if not verify_password(password, user.password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )

        # The password is correct, so we can safely explain the account status.
        if user.status != HRAccountStatus.ACTIVE:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Your account is not active"
            )

        # Upgrade the password hash only when necessary.
        if pwd_context.needs_update(user.password):
            user.password = hash_password(password)
            await self.session.commit()

        return self._token_for(user)

    async def change_password(self, user: HRUser,password:ChangePasswordRequest) -> TokenResponse:
        if not verify_password(password.current_password.password, user.password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        if  password.current_password.password == password.new_password.password:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="A company with this name already exists"
            )

        try:
            await self.hr_accounts.update_password(user,hash_password(password.new_password.password))
            await self.session.commit()

        except Exception:
            await self.session.rollback()
            raise

        return self._token_for(user)

