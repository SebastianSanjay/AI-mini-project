import os
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from models.job import Job
from database import get_db

router = APIRouter()

@router.get("/download/{job_id}")
async def download_video(job_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Job).filter(Job.id == job_id))
    job = result.scalars().first()

    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    if job.status != "completed" or not job.final_video_path:
        raise HTTPException(status_code=400, detail="Video is not ready for download")

    if not os.path.exists(job.final_video_path):
        raise HTTPException(status_code=404, detail="File missing on disk")

    return FileResponse(
        path=job.final_video_path,
        media_type="video/mp4",
        filename=f"translated_{job.original_filename}"
    )
