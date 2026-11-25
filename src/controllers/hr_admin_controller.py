from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from models.db.flow_wise.schema import Company, HRUser
from models.enums.hr_account_status_enum import HRAccountStatus
from models.enums.hr_role_enum import HRRole
from repositories import CompanyRepository,HRUserRepository
from schema.hr_member_schema import (
    MemberCreateRequest,
    MemberOut,
    MemberUpdateRequest,
)
from schema.hr_common_schema import Page
from schema import CompanyResponse,CompanyUpdateRequest

from helpers.security import hash_password
from helpers import utcnow



class HRAdminController:
    """Company profile + full lifecycle of HR Member accounts.

    Every lookup is limited to the admin's own company and to role=MEMBER,
    so an admin can never act on another company, or on their own account,
    through these endpoints.
    """

    def __init__(self, session: AsyncSession):
        self.session = session
        self.accounts = HRUserRepository(session)
        self.companies = CompanyRepository(session)

    # ---------------- company ----------------
    async def _company_or_404(self, admin: HRUser) -> Company:
        company = await self.companies.get_company_by_id(admin.company_id)
        if company is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOTFOUND,
                detail="Not found"
            )

        return company

    async def _member_or_404(self, admin: HRUser, member_id: int) -> HRUser:
            member = await self.accounts.get_member(admin.company_id, member_id)
            if member is None:
                raise  HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="member is not found"
                       )
            return member

    async def get_company(self, admin: HRUser) -> CompanyResponse:
        return CompanyResponse.model_validate(await self._company_or_404(admin))

    
    async def update_company(
        self,
        admin: HRUser,
        data: CompanyUpdateRequest
    ) -> CompanyResponse:

        company = await self._company_or_404(admin)

        updates = data.model_dump(exclude_unset=True)

        if "company_name" in updates:
            new_name = updates["company_name"]

            if not new_name or not new_name.strip():
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail="Company name cannot be empty"
                )

            new_name = new_name.strip()

            if new_name.lower() != company.company_name.lower():
                existing = await self.companies.get_company_by_name(new_name)

                if existing:
                    raise HTTPException(
                        status_code=status.HTTP_409_CONFLICT,
                        detail="Company name is already taken"
                    )

            updates["company_name"] = new_name

        try:
            await self.companies.update_company(
                company_data=company,
                company_updated_data=data
            )

            await self.session.commit()
            await self.session.refresh(company)

        except Exception:
            await self.session.rollback()
            raise

        return CompanyResponse.model_validate(company)

    async def create_member(self, admin: HRUser, data: MemberCreateRequest) -> MemberOut:

        email = str(data.email).lower()

        if await self.accounts.get_by_email(email):
            raise HTTPException(
                        status_code=status.HTTP_409_CONFLICT,
                        detail="email is already taken"
                        )
            
        try:
            db_hr_user = HRUser(
                company_id=admin.company_id,
                full_name=data.full_name,
                email=email,
                password=hash_password(data.password),
                role=HRRole.MEMBER,
                status=HRAccountStatus.PENDING,

            )

            member = await self.accounts.create_hr_user(db_hr_user)
            await self.session.commit()
        except IntegrityError:
            await self.session.rollback()
            raise 
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
                raise HTTPException(
                        status_code=status.HTTP_404_NOTFOUND,
                        detail="not found"
                        )
                
            member.full_name = updates["full_name"]
        
        if updates.get("password"):
            member.password = hash_password(updates["password"])
            member.token_version += 1  

        try:
            await self.session.commit()
        except IntegrityError:
            await self.session.rollback()
            raise 

        return MemberOut.model_validate(member)

    async def active_member(self, admin: HRUser, member_id: int) -> MemberOut:

        member = await self._member_or_404(admin, member_id)

        if member.status == HRAccountStatus.ACTIVE:
            raise HTTPException(
                          status_code=status.HTTP_409_CONFLICT,
                          detail="account is already active"
                         )

        try :
            member.status = HRAccountStatus.ACTIVE
            member.approved_by_id = admin.id
            member.approved_at = utcnow()
            await self.session.commit()

        except IntegrityError:
                await self.session.rollback()
                raise 
       
        return MemberOut.model_validate(member)

    async def disable_member(
        self, admin: HRUser, member_id: int
    ) -> MemberOut:
        member = await self._member_or_404(admin, member_id)

        if member.status != HRAccountStatus.ACTIVE:
            raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="account is already not active"
                      )
            
        try:  
            member.status = HRAccountStatus.DISABLED
            member.token_version += 1  # signs the member out right away
            await self.session.commit()

        except IntegrityError:
                        await self.session.rollback()
                        raise 

        return  MemberOut.model_validate(member)
        
    