from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from src.models.db.flow_wise.schema.company import Company
from schema import CompanyCreate, CompanyUpdate 

class CompanyRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_company(self, company_data: CompanyCreate) -> Company:
        new_company = Company(**company_data.model_dump())
        self.session.add(new_company)
        await self.session.commit()
        await self.session.refresh(new_company)
        return new_company

    async def get_company_by_id(self, company_id: int) -> Company | None:
        query = select(Company).where(Company.id == company_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()


    async def get_company_by_email(self, email:str) -> Company | None:
        query = select(Company).where(Company.email == email)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()
        


    async def get_all_companies(self) ->list[Company]:
        query = select(Company)
        result = await self.session.execute(query)
        return result.scalars().all()


    async def update_company(self,company_data:Company, company_updated_data: CompanyUpdate) -> Company | None:

        company_data.description = company_updated_data.description
        company_data.address = company_updated_data.address
        company_data.phone = company_updated_data.phone

        await self.session.commit()
        await self.session.refresh(company_data)
        return company_data




    async def delete_company(self, company:Company) -> bool:
        await self.session.delete(company)
        await self.session.commit()
        return True