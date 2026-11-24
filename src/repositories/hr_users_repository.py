from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete,func,or_
from models.db.flow_wise.schema.hr_user import HRUser
from models.enums.hr_account_status_enum import HRAccountStatus
from models.enums import HRRole
from pydantic import EmailStr
from helpers import like_pattern

class HRUserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_hr_user(self, hr_user: HRUser) -> HRUser:
        self.session.add(hr_user)
        await self.session.flush()
        return hr_user


    async def get_by_email(self, email: EmailStr) -> HRUser | None:
        query = select(HRUser).where(HRUser.email == str(email))
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_by_id(self, hr_id: int) -> HRUser | None:
        query = select(HRUser).where(HRUser.id == hr_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_all_hr_user(self) -> list[HRUser]:
        query = select(HRUser)
        result = await self.session.execute(query)
        return result.scalars().all()

    async def update_hr_user(self, hr_data:HRUser,fullname:str,password:str) -> HRUser | None:
        hr_data.full_name = fullname
        hr_data.password = password

        await self.session.commit()
        await self.session.refresh(hr_data)

        return hr_data




    async def delete_hr_user(self,hr_user:HRUser) -> bool:
        await self.session.delete(hr_user)
        await self.session.commit()
        return True


    async def update_password(self,user: HRUser,password_hash: str) -> HRUser:
        user.password = password_hash
        user.token_version += 1

        await self.session.flush()
        return user
    

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
    