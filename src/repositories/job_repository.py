from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload  # الاستيراد الجديد للتحميل المسبق
from datetime import datetime, timezone

from src.models.db.flow_wise.schema import Job, JobRequirement
from src.schema.job_schema import JobCreateRequest, JobUpdateRequest

class JobRepository:

    def __init__(self, session: AsyncSession):
        self.session = session

    # === دالة إنشاء الوظيفة (لم تتغير عن التحديث الأخير) ===
    async def create_job(self, job_data: JobCreateRequest) -> Job:
        # فصل البيانات: استبعاد الحقول الخاصة بجدول المتطلبات لتجنب خطأ TypeError
        job_dict = job_data.model_dump(exclude={"schema_definition", "weight"})
        
        # إنشاء كائن الوظيفة الأساسي
        db_job = Job(**job_dict)

        # الأسطر لحل مشكلة الوقت
        now_naive = datetime.now(timezone.utc).replace(tzinfo=None)
        db_job.created_at = now_naive
        db_job.updated_at = now_naive

        try:
            # إرسال الوظيفة لقاعدة البيانات مؤقتاً للحصول على الـ ID (بدون حفظ نهائي)
            self.session.add(db_job)
            await self.session.flush() 
            
            # إنشاء كائن المتطلبات باستخدام الـ ID الجديد
            db_requirement = JobRequirement(
                job_id=db_job.id,
                schema_definition=job_data.schema_definition,
                weight=job_data.weight
            )
            self.session.add(db_requirement)

            # الحفظ الدائم للجدولين معاً في نفس اللحظة (Atomicity)
            await self.session.commit()
            await self.session.refresh(db_job)

            # حقن البيانات وهمياً في كائن الوظيفة لكي يقرأها Pydantic (JobResponse) بنجاح
            setattr(db_job, "schema_definition", db_requirement.schema_definition)
            setattr(db_job, "weight", db_requirement.weight)

            return db_job

        except Exception:
            # إذا فشل إدخال أي جدول، تراجع عن العملية بالكامل
            await self.session.rollback()
            raise

    # === دوال الجلب المعدلة لدعم العلاقة (Eager Loading) ===
    async def get_job_by_id(self, job_id: int) -> Job | None:
        query = select(Job).options(selectinload(Job.requirements)).where(Job.id == job_id)
        result = await self.session.execute(query)
        job = result.scalar_one_or_none()
        
        # حقن البيانات لكي يقرأها Pydantic
        if job and job.requirements:
            setattr(job, "schema_definition", job.requirements[0].schema_definition)
            setattr(job, "weight", job.requirements[0].weight)
            
        return job

    async def get_all_jobs(
        self,
        limit: int = 100,
        offset: int = 0,
    ) -> list[Job]:
        if not 1 <= limit <= 100:
            raise ValueError("limit must be between 1 and 100")

        if offset < 0:
            raise ValueError("offset cannot be negative")

        query = (
            select(Job)
            .options(selectinload(Job.requirements)) # الجلب المسبق
            .order_by(Job.id)
            .limit(limit)
            .offset(offset)
        )

        result = await self.session.execute(query)
        jobs = list(result.scalars().all())
        
        # حقن البيانات لكل وظيفة
        for job in jobs:
            if job.requirements:
                setattr(job, "schema_definition", job.requirements[0].schema_definition)
                setattr(job, "weight", job.requirements[0].weight)
                
        return jobs

    async def get_active_jobs(
        self,
        limit: int = 100,
        offset: int = 0,
    ) -> list[Job]:
        if not 1 <= limit <= 100:
            raise ValueError("limit must be between 1 and 100")

        if offset < 0:
            raise ValueError("offset cannot be negative")

        query = (
            select(Job)
            .options(selectinload(Job.requirements)) # الجلب المسبق
            .where(Job.status == "published")
            .order_by(Job.id)
            .limit(limit)
            .offset(offset)
        )

        result = await self.session.execute(query)
        jobs = list(result.scalars().all())
        
        # حقن البيانات لكل وظيفة
        for job in jobs:
            if job.requirements:
                setattr(job, "schema_definition", job.requirements[0].schema_definition)
                setattr(job, "weight", job.requirements[0].weight)
                
        return jobs

    # === دوال التحديث والحذف (لم تتغير) ===
    async def update_job(
        self,
        job: Job,
        job_data: JobUpdateRequest,
    ) -> Job:
        updates = job_data.model_dump(exclude_unset=True)

        for key, value in updates.items():
            setattr(job, key, value)

        job.updated_at = datetime.now(timezone.utc).replace(tzinfo=None)

        try:
            await self.session.commit()
            await self.session.refresh(job)
            return job
        except Exception:
            await self.session.rollback()
            raise

    async def delete_job(self, job: Job) -> bool:
        try:
            await self.session.delete(job)
            await self.session.commit()
            return True
        except Exception:
            await self.session.rollback()
            raise


    async def get_job_with_applications(self, job_id: int) -> Job | None:
        query = (
            select(Job)
            .options(
                selectinload(Job.requirements),
                selectinload(Job.applications) # الجلب المسبق للطلبات
            )
            .where(Job.id == job_id)
        )
        result = await self.session.execute(query)
        job = result.scalar_one_or_none()
        
        # حقن المتطلبات لكي يقرأها Pydantic
        if job and job.requirements:
            setattr(job, "schema_definition", job.requirements[0].schema_definition)
            setattr(job, "weight", job.requirements[0].weight)
            
        return job    