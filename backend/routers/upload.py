import os
import uuid
from fastapi import APIRouter, File, UploadFile, Form, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from models.job import Job
from database import get_db
from config import LANGUAGE_MAP
from utils.logger import logger
from utils.storage import storage

router = APIRouter()

# For a 25GB file, standard multi-part is not ideal, but we use an optimized streaming approach
# where we read chunks and write directly to disk rather than holding in memory.
# In a full prod setup with tus, you'd use a dedicated tusd server or a FastAPI tus library.
# Here we implement a robust chunked streaming endpoint.

@router.post("/upload-video")
async def upload_video(
    file: UploadFile = File(...),
    target_language: str = Form(...),
    source_language: str = Form(None),
    db: AsyncSession = Depends(get_db)
):
    # Validate languages
    if target_language not in LANGUAGE_MAP and target_language not in LANGUAGE_MAP.values():
        raise HTTPException(status_code=400, detail=f"Unsupported target language: {target_language}")

    target_code = LANGUAGE_MAP.get(target_language, target_language)
    source_code = LANGUAGE_MAP.get(source_language, source_language) if source_language else None

    # Validate file type
    allowed_types = ["video/mp4", "video/quicktime", "video/x-matroska"]
    if file.content_type not in allowed_types:
        logger.warning(f"Invalid file type uploaded: {file.content_type}")
        raise HTTPException(status_code=400, detail="Invalid file format. Supported: MP4, MOV, MKV")

    job_id = str(uuid.uuid4())
    ext = os.path.splitext(file.filename)[1]
    filename = f"{job_id}{ext}"
    destination_key = os.path.join("uploads", filename)

    # Stream to storage
    try:
        upload_path = await storage.save_stream(file, destination_key)
    except Exception as e:
        logger.error(f"Failed to save file: {e}")
        raise HTTPException(status_code=500, detail="Failed to save video file")
    finally:
        await file.close()

    # Create Job Record
    new_job = Job(
        id=job_id,
        original_filename=file.filename,
        target_language=target_code,
        source_language=source_code,
        video_path=upload_path,
        status="pending",
        current_step="upload",
        progress=0.0
    )

    db.add(new_job)
    await db.commit()

    return {"job_id": job_id, "message": "Video uploaded successfully"}
