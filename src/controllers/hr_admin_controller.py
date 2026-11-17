from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from models.db.flow_wise.schema import Company, HRUser
from models.enums.hr_account_status_enum import HRAccountStatus
from models.enums.hr_role_enum import HRRole

from helpers.hr_errors import conflict, not_found
from repositories.hr_account_repository import HRAccountRepository
from repositories.hr_company_repository import HRCompanyRepository
from helpers.hr_utils import utcnow, utcnow_naive
from schema.hr_company_schema import CompanyOut, CompanyUpdateRequest
from schema.hr_member_schema import (
    MemberCreateRequest,
    MemberOut,
    MemberUpdateRequest,
)
from schema.hr_common_schema import Page
from helpers.security import hash_password


class HRAdminController:
    """Company profile + full lifecycle of HR Member accounts.

    Every lookup is limited to the admin's own company and to role=MEMBER,
    so an admin can never act on another company, or on their own account,
    through these endpoints.
    """

    def __init__(self, session: AsyncSession):
        self.session = session
        self.accounts = HRAccountRepository(session)
        self.companies = HRCompanyRepository(session)

    # ---------------- company ----------------
    async def _company_or_404(self, admin: HRUser) -> Company:
        company = await self.companies.get(admin.company_id)
        if company is None:
            raise not_found("Company")
        return company

    async def get_company(self, admin: HRUser) -> CompanyOut:
        return CompanyOut.model_validate(await self._company_or_404(admin))

    async def update_company(self, admin: HRUser, data: CompanyUpdateRequest) -> CompanyOut:
        company = await self._company_or_404(admin)
        updates = data.model_dump(exclude_unset=True)

        if "company_name" in updates:
            if not updates["company_name"]:
                raise conflict("Company name cannot be empty")
            if await self.companies.name_taken(updates["company_name"], exclude_id=company.id):
                raise conflict("A company with this name already exists")
        if updates.get("email"):
            updates["email"] = str(updates["email"]).lower()
            if await self.companies.email_taken(updates["email"], exclude_id=company.id):
                raise conflict("A company with this email already exists")

        for key, value in updates.items():
            setattr(company, key, value)
        try:
            await self.session.commit()
        except IntegrityError:
            await self.session.rollback()
            raise conflict("Company name or email already in use")
        await self.session.refresh(company)
        return CompanyOut.model_validate(company)

    # ---------------- members ----------------
    async def _member_or_404(self, admin: HRUser, member_id: int) -> HRUser:
        member = await self.accounts.get_member(admin.company_id, member_id)
        if member is None:
            raise not_found("HR member")
        return member

    async def create_member(self, admin: HRUser, data: MemberCreateRequest) -> MemberOut:
        email = str(data.email).lower()
        if await self.accounts.email_taken(email):
            raise conflict("An account with this email already exists")
        try:
            member = await self.accounts.add(
                HRUser(
                    company_id=admin.company_id,
                    full_name=data.full_name,
                    email=email,
                    password=hash_password(data.password),
                    role=HRRole.MEMBER,
                    status=HRAccountStatus.PENDING,
                    token_version=0,
                    created_at=utcnow_naive(),
                )
            )
            await self.session.commit()
        except IntegrityError:
            await self.session.rollback()
            raise conflict("An account with this email already exists")
        return MemberOut.model_validate(member)

    async def list_members(
        self,
        admin: HRUser,
        *,
        status: HRAccountStatus | None,
        search: str | None,
        limit: int,
        offset: int,
    ) -> Page[MemberOut]:
        items, total = await self.accounts.list_members(
            admin.company_id, status=status, search=search, limit=limit, offset=offset
        )
        return Page[MemberOut](
            items=[MemberOut.model_validate(m) for m in items],
            total=total,
            limit=limit,
            offset=offset,
        )

    async def get_member(self, admin: HRUser, member_id: int) -> MemberOut:
        return MemberOut.model_validate(await self._member_or_404(admin, member_id))

    async def update_member(
        self, admin: HRUser, member_id: int, data: MemberUpdateRequest
    ) -> MemberOut:
        member = await self._member_or_404(admin, member_id)
        updates = data.model_dump(exclude_unset=True)

        if "full_name" in updates:
            if not updates["full_name"]:
                raise conflict("Full name cannot be empty")
            member.full_name = updates["full_name"]
        if updates.get("email"):
            email = str(updates["email"]).lower()
            if await self.accounts.email_taken(email, exclude_user_id=member.id):
                raise conflict("An account with this email already exists")
            member.email = email
        if updates.get("password"):
            member.password = hash_password(updates["password"])
            member.token_version += 1  # old sessions stop working

        try:
            await self.session.commit()
        except IntegrityError:
            await self.session.rollback()
            raise conflict("An account with this email already exists")
        return MemberOut.model_validate(member)

    async def approve_member(self, admin: HRUser, member_id: int) -> MemberOut:
        member = await self._member_or_404(admin, member_id)
        if member.status == HRAccountStatus.ACTIVE:
            raise conflict("Member is already active")
        member.status = HRAccountStatus.ACTIVE
        member.approved_by_id = admin.id
        member.approved_at = utcnow()
        await self.session.commit()
        return MemberOut.model_validate(member)

    async def decline_member(
        self, admin: HRUser, member_id: int
    ) -> MemberOut:
        member = await self._member_or_404(admin, member_id)
        if member.status != HRAccountStatus.PENDING:
            raise conflict("Only a pending member can be declined. Use disable for active members")
        member.status = HRAccountStatus.DECLINED
        member.token_version += 1
        await self.session.commit()
        return MemberOut.model_validate(member)

    async def disable_member(
        self, admin: HRUser, member_id: int
    ) -> MemberOut:
        member = await self._member_or_404(admin, member_id)
        if member.status != HRAccountStatus.ACTIVE:
            raise conflict("Only an active member can be disabled")
        member.status = HRAccountStatus.DISABLED
        member.token_version += 1  # signs the member out right away
        await self.session.commit()
        return MemberOut.model_validate(member)

    async def delete_member(self, admin: HRUser, member_id: int) -> None:
        member = await self._member_or_404(admin, member_id)
        # jobs.created_by is ON DELETE CASCADE: deleting a member who owns
        # postings would silently delete those postings and their applications.
        postings = await self.accounts.count_postings_by(member.id)
        if postings > 0:
            raise conflict(
                f"This member created {postings} posting(s). Deleting them would also "
                "delete those postings and their applicants. Disable the account instead"
            )
        await self.accounts.delete(member)
        await self.session.commit()
