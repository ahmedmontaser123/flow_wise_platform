"""Data access for HR accounts. Repositories only flush; controllers commit."""
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from models.db.flow_wise.schema import HRUser, Job
from models.enums.hr_account_status_enum import HRAccountStatus
from models.enums.hr_role_enum import HRRole

from helpers.hr_utils import like_pattern


class HRAccountRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, user_id: int) -> HRUser | None:
        return await self.session.get(HRUser, user_id, populate_existing=True)

    async def get_by_email(self, email: str) -> HRUser | None:
        query = select(HRUser).where(func.lower(HRUser.email) == email.strip().lower())
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def email_taken(self, email: str, exclude_user_id: int | None = None) -> bool:
        query = select(HRUser.id).where(func.lower(HRUser.email) == email.strip().lower())
        if exclude_user_id is not None:
            query = query.where(HRUser.id != exclude_user_id)
        result = await self.session.execute(query.limit(1))
        return result.first() is not None

    async def get_member(self, company_id: int, member_id: int) -> HRUser | None:
        """A MEMBER of this company. Admins and other companies' users -> None."""
        query = select(HRUser).where(
            HRUser.id == member_id,
            HRUser.company_id == company_id,
            HRUser.role == HRRole.MEMBER,
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def list_members(
        self,
        company_id: int,
        *,
        status: HRAccountStatus | None = None,
        search: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> tuple[list[HRUser], int]:
        conditions = [HRUser.company_id == company_id, HRUser.role == HRRole.MEMBER]
        if status is not None:
            conditions.append(HRUser.status == status)
        if search:
            pattern = like_pattern(search.strip())
            conditions.append(
                or_(HRUser.full_name.ilike(pattern), HRUser.email.ilike(pattern))
            )

        total = await self.session.scalar(
            select(func.count()).select_from(HRUser).where(*conditions)
        )
        result = await self.session.execute(
            select(HRUser)
            .where(*conditions)
            .order_by(HRUser.created_at.desc(), HRUser.id.desc())
            .limit(limit)
            .offset(offset)
        )
        return list(result.scalars().all()), int(total or 0)

    async def count_postings_by(self, user_id: int) -> int:
        total = await self.session.scalar(
            select(func.count()).select_from(Job).where(Job.created_by == user_id)
        )
        return int(total or 0)

    async def add(self, user: HRUser) -> HRUser:
        self.session.add(user)
        await self.session.flush()
        return user

    async def delete(self, user: HRUser) -> None:
        await self.session.delete(user)
        await self.session.flush()
