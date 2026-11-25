import os
import uuid
import hashlib
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from typing import Annotated

from models.db.connection_database import get_db_session
from models.db.flow_wise.schema.candidate import Candidate
from models.db.flow_wise.schema.cv_file import CvFile
from models.db.flow_wise.schema.application import Application
from models.db.flow_wise.schema.job import Job  
from models.enums import ApplicationStatus

DBSession = Annotated[AsyncSession, Depends(get_db_session)]

candidate_apply_router = APIRouter(prefix="/api/v1/jobs", tags=["Public - Job Application"])

@candidate_apply_router.post("/{job_id}/apply", status_code=status.HTTP_201_CREATED)
async def apply_for_job(
    job_id: int,
    session: DBSession,
    full_name: str = Form(...),
    email: str = Form(...),
    phone: str = Form(None),
    education: str = Form(None),
    portfolio: str = Form(None),
    cv_file: UploadFile = File(...)
):
    # 1. Validate Job Exists
    job = await session.get(Job, job_id)
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Job not found."
        )

    # 2. Get or Create Candidate
    query = select(Candidate).where(Candidate.email == email)
    result = await session.execute(query)
    candidate = result.scalar_one_or_none()

    if not candidate:
        candidate = Candidate(
            full_name=full_name,
            email=email,
            phone=phone,
            education=education,
            portfolio=portfolio
        )
        session.add(candidate)
        await session.flush()

    # 3. Check for Existing Application (Prevent double apply for same job)
    app_query = select(Application).join(CvFile, Application.cv_file_id == CvFile.id).where(
        and_(
            CvFile.candidate_id == candidate.id,
            Application.job_id == job_id
        )
    )
    app_result = await session.execute(app_query)
    existing_application = app_result.scalar_one_or_none()

    if existing_application:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="You have already applied for this job."
        )
    
    # 4. Handle CV File (Idempotency check via Hash & Local Storage)
    file_content = await cv_file.read()
    file_hash = hashlib.sha256(file_content).hexdigest()

    cv_query = select(CvFile).where(
        and_(
            CvFile.candidate_id == candidate.id,
            CvFile.file_hash == file_hash
        )
    )
    cv_result = await session.execute(cv_query)
    existing_cv = cv_result.scalar_one_or_none()

    if existing_cv:
        cv_id = existing_cv.id
    else:
        # إنشاء مسار التخزين إذا لم يكن موجوداً
        upload_dir = "uploads/cvs"
        os.makedirs(upload_dir, exist_ok=True)
        
        # حفظ الملف فيزيائياً باسم فريد لمنع تداخل الأسماء
        unique_filename = f"{uuid.uuid4()}_{cv_file.filename}"
        file_path = os.path.join(upload_dir, unique_filename)
        
        with open(file_path, "wb") as f:
            f.write(file_content)

        # حفظ مسار الملف فقط في قاعدة البيانات
        new_cv = CvFile(
            candidate_id=candidate.id,
            file_path=file_path,
            file_hash=file_hash
        )
        session.add(new_cv)
        await session.flush()
        cv_id = new_cv.id

    # 5. Create the Application Record
    new_application = Application(
        job_id=job_id,
        cv_file_id=cv_id,
        status=ApplicationStatus.RECEIVED  # التعديل تم هنا بنجاح
    )
    
    session.add(new_application)
    await session.commit()

    return {
        "message": "Application submitted successfully.",
        "application_id": new_application.id,
        "candidate_id": candidate.id,
        "cv_file_id": cv_id
    }