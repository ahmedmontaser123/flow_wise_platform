from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete,func
from models.db.flow_wise.schema import Company
from schema import CompanyUpdateRequest

class CompanyRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_company(self, company: Company) -> Company:
        self.session.add(company)
        await self.session.flush()
        return company

    async def get_company_by_id(self, company_id: int) -> Company | None:
        query = select(Company).where(Company.id == company_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_company_by_email(self, email:str) -> Company | None:
        query = select(Company.email).where(Company.email == email)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()
        
    async def get_all_companies(self) ->list[Company]:
        query = select(Company)
        result = await self.session.execute(query)
        return result.scalars().all()

    async def update_company(self,company_data:Company, company_updated_data: CompanyUpdateRequest) -> Company | None:
        company_data.company_name = company_updated_data.company_name
        company_data.description = company_updated_data.description
        company_data.address = company_updated_data.address
        company_data.phone = company_updated_data.phone

        await self.self.session.flush()
        await self.session.refresh(company_data)
        return company_data

    async def delete_company(self, company:Company) -> bool:
        await self.session.delete(company)
        await self.session.commit()
        return True


    async def get_company_by_name(self,name:str):
        query = select(Company.company_name).where(
            func.lower(Company.company_name) == name.strip().lower()
            )

        result = await self.session.execute(query)
        return result.scalar_one_or_none()
