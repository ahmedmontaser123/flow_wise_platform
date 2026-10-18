from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from src.models.db.flow_wise.schema.hr_user import HRUser
from schema import HRUserCreate, HRUserUpdate

class HRUserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, user_data: HRUserCreate) -> HRUser:
        new_user = HRUser(**user_data.model_dump())
        self.session.add(new_user)
        await self.session.commit()
        await self.session.refresh(new_user)
        return new_user

    async def get_by_id(self, user_id: int) -> HRUser | None:
        result = await self.session.execute(select(HRUser).where(HRUser.id == user_id))
        return result.scalars().first()

    async def get_all(self) -> list[HRUser]:
        result = await self.session.execute(select(HRUser))
        return list(result.scalars().all())

    async def update(self, user_id: int, update_data: HRUserUpdate) -> HRUser | None:
        query = (
            update(HRUser)
            .where(HRUser.id == user_id)
            .values(**update_data.model_dump(exclude_unset=True))
            .returning(HRUser)
        )
        result = await self.session.execute(query)
        await self.session.commit()
        return result.scalars().first()

    async def delete(self, user_id: int) -> bool:
        query = delete(HRUser).where(HRUser.id == user_id)
        result = await self.session.execute(query)
        await self.session.commit()
        return result.rowcount > 0