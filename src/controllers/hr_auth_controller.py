from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from models.db.flow_wise.schema import Company, HRUser
from models.enums.hr_account_status_enum import HRAccountStatus
from models.enums.hr_role_enum import HRRole

from helpers.hr_errors import conflict, forbidden, unauthorized
from repositories.hr_account_repository import HRAccountRepository
from repositories.hr_company_repository import HRCompanyRepository
from helpers.hr_utils import utcnow, utcnow_naive
from schema.hr_auth_schema import AdminRegisterRequest, ChangePasswordRequest, TokenResponse
from helpers.security import (
    burn_dummy_verify,
    create_access_token,
    hash_password,
    pwd_context,
    verify_password,
)
from helpers.hr_auth_settings import get_hr_auth_settings

_STATUS_MESSAGES = {
    HRAccountStatus.PENDING: "Your account is waiting for approval by the HR Admin",
    HRAccountStatus.DECLINED: "Your account request was declined by the HR Admin",
    HRAccountStatus.DISABLED: "Your account has been disabled by the HR Admin",
}


def _token_for(user: HRUser) -> TokenResponse:
    token, expires_in = create_access_token(
        user_id=user.id,
        role=user.role.value,
        company_id=user.company_id,
        token_version=user.token_version,
    )
    return TokenResponse(access_token=token, expires_in=expires_in, role=user.role)


class HRAuthController:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.accounts = HRAccountRepository(session)
        self.companies = HRCompanyRepository(session)

    async def register_admin(self, data: AdminRegisterRequest) -> TokenResponse:
        """Create a company and its HR Admin in one transaction."""
        if not get_hr_auth_settings().ALLOW_ADMIN_REGISTRATION:
            raise forbidden("Admin registration is closed")

        if await self.companies.name_taken(data.company.company_name):
            raise conflict("A company with this name already exists")
        if data.company.email and await self.companies.email_taken(str(data.company.email)):
            raise conflict("A company with this email already exists")
        if await self.accounts.email_taken(str(data.admin.email)):
            raise conflict("An account with this email already exists")

        try:
            company = await self.companies.add(
                Company(
                    company_name=data.company.company_name,
                    description=data.company.description,
                    address=data.company.address,
                    phone=data.company.phone,
                    email=str(data.company.email).lower() if data.company.email else None,
                )
            )
            admin = await self.accounts.add(
                HRUser(
                    company_id=company.id,
                    full_name=data.admin.full_name,
                    email=str(data.admin.email).lower(),
                    password=hash_password(data.admin.password),
                    role=HRRole.ADMIN,
                    status=HRAccountStatus.ACTIVE,
                    approved_at=utcnow(),
                    token_version=0,
                    created_at=utcnow_naive(),
                )
            )
            await self.session.commit()
        except IntegrityError:
            await self.session.rollback()
            raise conflict("Company or account already exists")

        return _token_for(admin)

    async def login(self, email: str, password: str) -> TokenResponse:
        user = await self.accounts.get_by_email(email)
        if user is None:
            burn_dummy_verify(password)
            raise unauthorized()
        if not verify_password(password, user.password):
            raise unauthorized()

        # The password is correct, so it is safe to say why login is refused.
        if user.status != HRAccountStatus.ACTIVE:
            raise forbidden(_STATUS_MESSAGES.get(user.status, "Account is not active"))

        if pwd_context.needs_update(user.password):
            user.password = hash_password(password)
        await self.session.commit()
        return _token_for(user)

    async def change_password(
        self, user: HRUser, data: ChangePasswordRequest
    ) -> TokenResponse:
        if not verify_password(data.current_password, user.password):
            raise unauthorized("Current password is incorrect")
        if data.current_password == data.new_password:
            raise conflict("New password must be different from the current one")

        user.password = hash_password(data.new_password)
        user.token_version += 1  # logs out every other session
        await self.session.commit()
        return _token_for(user)
