from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from models.db.flow_wise.schema import Company


class HRCompanyRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get(self, company_id: int) -> Company | None:
        return await self.session.get(Company, company_id)

    async def name_taken(self, name: str, exclude_id: int | None = None) -> bool:
        query = select(Company.id).where(func.lower(Company.company_name) == name.lower())
        if exclude_id is not None:
            query = query.where(Company.id != exclude_id)
        return (await self.session.execute(query.limit(1))).first() is not None

    async def email_taken(self, email: str, exclude_id: int | None = None) -> bool:
        query = select(Company.id).where(func.lower(Company.email) == email.lower())
        if exclude_id is not None:
            query = query.where(Company.id != exclude_id)
        return (await self.session.execute(query.limit(1))).first() is not None

    async def add(self, company: Company) -> Company:
        self.session.add(company)
        await self.session.flush()
        return company
