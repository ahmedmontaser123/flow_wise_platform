from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from schema.cv_file_schema import CvFileCreateRequest
from models.db.flow_wise.schema.cv_file import CvFile

class CvFileRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_cv_file(self, cv_file_data: CvFileCreateRequest) -> CvFile:
        cv_file = CvFile(
            candidate_id=cv_file_data.candidate_id,
            file_path=cv_file_data.file_path,
            file_hash=cv_file_data.file_hash  # <-- (1) تمت إضافة البصمة هنا للحفظ
        )

        self.session.add(cv_file)
        await self.session.flush()
        await self.session.refresh(cv_file)
        return cv_file

    # <-- (2) تمت إضافة هذه الدالة الجديدة لفحص البصمة قبل الرفع
    async def get_cv_by_hash(self, candidate_id: int, file_hash: str) -> CvFile | None:
        query = select(CvFile).where(
            CvFile.candidate_id == candidate_id,
            CvFile.file_hash == file_hash
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_cv_by_id(self, cv_file_id: int) -> CvFile | None:
        query = select(CvFile).where(CvFile.id == cv_file_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_cv_files_by_candidate_id(self, candidate_id: int) -> list[CvFile]:
        query = (
            select(CvFile)
            .where(CvFile.candidate_id == candidate_id)
            .order_by(CvFile.created_at.desc())
        )
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def delete_cv_file(self, cv_file: CvFile) -> None:
        await self.session.delete(cv_file)
        await self.session.flush()