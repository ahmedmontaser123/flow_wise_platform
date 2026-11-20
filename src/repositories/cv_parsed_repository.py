from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.db.flow_wise.schema import CvParsed
from models.enums import ParsingStatus
from schema.cv_parsed_schema import CvParsedCreateRequest, CvParsedUpdateRequest


class CvParsedRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_cv_parsed(self, cv_parsed_data: CvParsedCreateRequest,) -> CvParsed:
        cv_parsed = CvParsed(cv_file_id=cv_parsed_data.cv_file_id, 
                             status=ParsingStatus.PENDING)

        self.session.add(cv_parsed)
        await self.session.flush()
        await self.session.refresh(cv_parsed)

        return cv_parsed

    async def get_cv_parsed_by_id(self, cv_parsed_id: int) -> CvParsed | None:
        query = select(CvParsed).where(CvParsed.id == cv_parsed_id)
        result = await self.session.execute(query)

        return result.scalar_one_or_none()

    async def get_cv_parsed_by_cv_file_id(self, cv_file_id: int) -> CvParsed | None:
        query = select(CvParsed).where(CvParsed.cv_file_id == cv_file_id)
        result = await self.session.execute(query)

        return result.scalar_one_or_none()

    async def update_cv_parsed(self, cv_parsed: CvParsed, cv_parsed_data: CvParsedUpdateRequest) -> CvParsed:
        update_data = cv_parsed_data.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            setattr(cv_parsed, field, value)

        await self.session.flush()
        await self.session.refresh(cv_parsed)

        return cv_parsed