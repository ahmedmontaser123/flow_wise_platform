from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from src.models.db.flow_wise.schema.hr_user import HRUser
from schema import HRUserCreate, HRUserUpdate
from pydantic import EmailStr

class HRUserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_hr_user(self, user_data: HRUserCreate) -> HRUser:
        new_user = HRUser(**user_data.model_dump())
        self.session.add(new_user)
        await self.session.commit()
        await self.session.refresh(new_user)
        return new_user

    async def get_by_email(self, email: EmailStr) -> HRUser | None:
        query = select(HRUser).where(HRUser.email == str(email))
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_all_hr_user(self) -> list[HRUser]:
        query = select(HRUser)
        result = await self.session.execute(query)
        return result.scalars().all()

    async def update_hr_user(self, hr_data:HRUser,hr_updated_data: HRUserUpdate) -> HRUser | None:
        hr_data.full_name = hr_updated_data.full_name
        hr_data.password = hr_updated_data.password

        await self.session.commit()
        await self.session.refresh(hr_data)

        return hr_data




    async def delete_hr_user(self,hr_user:HRUser) -> bool:
        await self.session.delete(hr_user)
        await self.session.commit()
        return True