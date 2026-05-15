from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from models.job import Job
from database import get_db
from workers.tasks import task_full_pipeline

router = APIRouter()

@router.post("/translate-video/{job_id}")
async def start_translation(job_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Job).filter(Job.id == job_id))
    job = result.scalars().first()

    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    if job.status not in ["pending", "failed"]:
        raise HTTPException(status_code=400, detail=f"Job is already in status: {job.status}")

    # Update status to processing
    job.status = "processing"
    job.current_step = "initializing"
    job.error_message = None
    await db.commit()

    # Enqueue pipeline
    task_full_pipeline.delay(job_id)

    return {"job_id": job_id, "status": "processing"}
