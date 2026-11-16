from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from src.repositories.candidate_repository import CandidateRepository
from src.repositories.cv_file_repository import CvFileRepository
from src.repositories.cv_parsed_repository import CvParsedRepository
from src.storage.local_storage import LocalStorage
from src.schema.cv_parsed_schema import CvParsedCreateRequest
from src.schema.cv_file_schema import CvFileCreateRequest


class CvFileService:

    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

        self.candidate_repository = CandidateRepository(db_session)
        self.cv_file_repository = CvFileRepository(db_session)
        self.cv_parsed_repository = CvParsedRepository(db_session)

        self.storage = LocalStorage()

    async def upload_cv(
        self,
        candidate_id: int,
        file: UploadFile,
    ):
        saved_path = None

        try:
            # 1. Validate the candidate
            candidate = await self.candidate_repository.get_candidate_by_id(
                candidate_id
            )

            if candidate is None:
                raise ValueError("Candidate not found.")

            # 2. Validate the uploaded file
            if not file.filename:
                raise ValueError("A filename is required.")

            # 3. Save the file to local storage
            saved_path = await self.storage.save(
                file=file.file,
                filename=file.filename,
            )

            # 4. Create the CV file database record
            cv_file = await self.cv_file_repository.create_cv_file(
                    cv_file_data=CvFileCreateRequest(
                    candidate_id=candidate_id,
                    file_path=saved_path,
                    )
           )

            # 5. Create the parsing record
            await self.cv_parsed_repository.create_cv_parsed(
                cv_parsed_data=CvParsedCreateRequest(
                    cv_file_id=cv_file.id
                )
            )

            # 6. Commit all database changes
            await self.db_session.commit()

            # 7. Refresh the CV file record
            await self.db_session.refresh(cv_file)

            return cv_file

        except Exception:
            await self.db_session.rollback()

            # Remove the saved file if database operations fail
            if saved_path is not None:
                try:
                    await self.storage.delete(saved_path)
                except Exception:
                    pass

            raise

        finally:
            await file.close()