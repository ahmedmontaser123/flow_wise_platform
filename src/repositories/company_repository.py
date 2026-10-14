from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from src.models.db.flow_wise.schema.company import Company
# Adjust this import path to wherever your Pydantic schemas are located
from src.schemas.company import CompanyCreate, CompanyUpdate 

class CompanyRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, company_data: CompanyCreate) -> Company:
        # .model_dump() converts the Pydantic model into a standard Python dictionary
        new_company = Company(**company_data.model_dump())
        self.session.add(new_company)
        await self.session.commit()
        await self.session.refresh(new_company)
        return new_company

    async def get_by_id(self, company_id: int) -> Company | None:
        result = await self.session.execute(select(Company).where(Company.id == company_id))
        return result.scalars().first()

    async def get_all(self) -> list[Company]:
        result = await self.session.execute(select(Company))
        return list(result.scalars().all())

    async def update(self, company_id: int, update_data: CompanyUpdate) -> Company | None:
        # exclude_unset=True is crucial here: it prevents overwriting existing database values with None 
        # if the user only provided a partial update (like changing only the email)
        query = (
            update(Company)
            .where(Company.id == company_id)
            .values(**update_data.model_dump(exclude_unset=True))
            .returning(Company)
        )
        result = await self.session.execute(query)
        await self.session.commit()
        return result.scalars().first()

    async def delete(self, company_id: int) -> bool:
        query = delete(Company).where(Company.id == company_id)
        result = await self.session.execute(query)
        await self.session.commit()
        return result.rowcount > 0