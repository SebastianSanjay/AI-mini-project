import os
import json
import asyncio
from datetime import datetime
from celery import chain
from workers.celery_app import celery_app
from config import settings
from utils.logger import logger
from utils.storage import storage
import redis

# We need a synchronous session maker for Celery workers since Celery tasks are sync by default
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models.job import Job

# Sync DB setup for Celery
# Replace asyncpg driver with psycopg2 for sync usage
sync_db_url = settings.DATABASE_URL.replace("+asyncpg", "")
engine = create_engine(sync_db_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

redis_client = redis.Redis.from_url(settings.REDIS_URL, decode_responses=True)

def update_job_status(job_id: str, step: str, progress: float, status: str = "processing", error: str = None):
    db = SessionLocal()
    try:
        job = db.query(Job).filter(Job.id == job_id).first()
        if job:
            job.current_step = step
            job.progress = progress
            job.status = status
            job.updated_at = datetime.utcnow()
            if error:
                job.error_message = error
            db.commit()

            # Broadcast via Redis pub/sub
            msg = {
                "job_id": job_id,
                "step": step,
                "progress": progress,
                "status": status,
                "message": error if error else f"Processing {step}...",
                "timestamp": datetime.utcnow().isoformat()
            }
            redis_client.publish(f"job_progress_{job_id}", json.dumps(msg))
    except Exception as e:
        logger.error(f"Error updating job status: {e}")
    finally:
        db.close()

def get_job_info(job_id: str):
    db = SessionLocal()
    try:
        job = db.query(Job).filter(Job.id == job_id).first()
        if job:
            return {
                "video_path": job.video_path,
                "target_language": job.target_language,
                "source_language": job.source_language
            }
        return None
    finally:
        db.close()

def save_job_path(job_id: str, field: str, path: str):
    db = SessionLocal()
    try:
        job = db.query(Job).filter(Job.id == job_id).first()
        if job:
            setattr(job, field, path)
            db.commit()
    finally:
        db.close()

@celery_app.task(bind=True, name="task_extract_audio")
def task_extract_audio(self, job_id: str):
    update_job_status(job_id, "extraction", 10.0)
    try:
        from services.audio_extraction import extract_audio
        job_info = get_job_info(job_id)
        if not job_info:
            raise ValueError(f"Job {job_id} not found")

        output_audio = storage.get_file_path(os.path.join("audio", f"{job_id}.wav"))
        extract_audio(job_info["video_path"], output_audio)

        save_job_path(job_id, "extracted_audio_path", output_audio)
        update_job_status(job_id, "extraction", 20.0)
        return {"job_id": job_id, "audio_path": output_audio}
    except Exception as e:
        update_job_status(job_id, "extraction", 0.0, "failed", str(e))
        raise

@celery_app.task(bind=True, name="task_transcribe")
def task_transcribe(self, prev_result, job_id: str):
    update_job_status(job_id, "transcription", 30.0)
    try:
        from services.transcription import transcribe
        job_info = get_job_info(job_id)

        audio_path = prev_result["audio_path"]
        output_json = storage.get_file_path(os.path.join("transcripts", f"{job_id}.json"))

        transcribe(audio_path, output_json, job_info.get("source_language"))

        save_job_path(job_id, "transcript_path", output_json)
        update_job_status(job_id, "transcription", 45.0)
        return {"job_id": job_id, "transcript_path": output_json}
    except Exception as e:
        update_job_status(job_id, "transcription", 0.0, "failed", str(e))
        raise

@celery_app.task(bind=True, name="task_translate")
def task_translate(self, prev_result, job_id: str):
    update_job_status(job_id, "translation", 50.0)
    try:
        from services.translation import translate
        job_info = get_job_info(job_id)

        transcript_path = prev_result["transcript_path"]

        translated_json = translate(
            transcript_path,
            job_info["target_language"],
            job_info.get("source_language")
        )

        update_job_status(job_id, "translation", 65.0)
        return {"job_id": job_id, "translated_transcript_path": translated_json}
    except Exception as e:
        update_job_status(job_id, "translation", 0.0, "failed", str(e))
        raise

@celery_app.task(bind=True, name="task_generate_voice")
def task_generate_voice(self, prev_result, job_id: str):
    update_job_status(job_id, "voice_generation", 70.0)
    try:
        from services.voice_generation import generate_voice
        job_info = get_job_info(job_id)

        translated_json = prev_result["translated_transcript_path"]
        output_audio = storage.get_file_path(os.path.join("translated", f"{job_id}_{job_info['target_language']}.wav"))

        # We need the original audio path for Coqui TTS voice cloning
        original_audio_path = storage.get_file_path(os.path.join("audio", f"{job_id}.wav"))
        generate_voice(translated_json, output_audio, job_info["target_language"], original_audio_path)

        save_job_path(job_id, "translated_audio_path", output_audio)
        update_job_status(job_id, "voice_generation", 80.0)
        return {"job_id": job_id, "translated_audio_path": output_audio}
    except Exception as e:
        update_job_status(job_id, "voice_generation", 0.0, "failed", str(e))
        raise

@celery_app.task(bind=True, name="task_lip_sync")
def task_lip_sync(self, prev_result, job_id: str):
    update_job_status(job_id, "lip_sync", 85.0)
    try:
        from services.lip_sync import lip_sync as do_lip_sync
        job_info = get_job_info(job_id)

        translated_audio = prev_result["translated_audio_path"]
        video_path = job_info["video_path"]
        output_video = storage.get_file_path(os.path.join("outputs", f"{job_id}_lipsync.mp4"))

        do_lip_sync(video_path, translated_audio, output_video)

        update_job_status(job_id, "lip_sync", 95.0)
        return {"job_id": job_id, "lipsync_video_path": output_video, "translated_audio_path": translated_audio}
    except Exception as e:
        update_job_status(job_id, "lip_sync", 0.0, "failed", str(e))
        raise

@celery_app.task(bind=True, name="task_render_final")
def task_render_final(self, prev_result, job_id: str):
    update_job_status(job_id, "rendering", 96.0)
    try:
        from services.rendering import render_final_video

        lipsync_video = prev_result["lipsync_video_path"]
        translated_audio = prev_result["translated_audio_path"]
        final_video = storage.get_file_path(os.path.join("outputs", f"{job_id}_final.mp4"))

        render_final_video(lipsync_video, translated_audio, final_video)

        save_job_path(job_id, "final_video_path", final_video)
        update_job_status(job_id, "complete", 100.0, "completed")
        return {"job_id": job_id, "final_video_path": final_video}
    except Exception as e:
        update_job_status(job_id, "rendering", 0.0, "failed", str(e))
        raise

@celery_app.task(bind=True, name="task_full_pipeline")
def task_full_pipeline(self, job_id: str):
    # This task chains all the steps together
    pipeline = chain(
        task_extract_audio.s(job_id),
        task_transcribe.s(job_id),
        task_translate.s(job_id),
        task_generate_voice.s(job_id),
        task_lip_sync.s(job_id),
        task_render_final.s(job_id)
    )
    pipeline.apply_async()
    return f"Started pipeline for {job_id}"
