from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from models.job import Job
from database import get_db

router = APIRouter()

@router.get("/processing-status/{job_id}")
async def get_status(job_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Job).filter(Job.id == job_id))
    job = result.scalars().first()

    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    return {
        "job_id": job.id,
        "status": job.status,
        "current_step": job.current_step,
        "progress": job.progress,
        "error": job.error_message,
        "updated_at": job.updated_at
    }
