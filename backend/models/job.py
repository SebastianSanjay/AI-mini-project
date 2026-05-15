from sqlalchemy import Column, String, Integer, DateTime, Float
from datetime import datetime
from database import Base

class Job(Base):
    __tablename__ = "jobs"

    id = Column(String, primary_key=True, index=True)
    original_filename = Column(String, nullable=False)
    target_language = Column(String, nullable=False)
    source_language = Column(String, nullable=True) # Optional

    # File paths for intermediate steps
    video_path = Column(String, nullable=True)
    extracted_audio_path = Column(String, nullable=True)
    transcript_path = Column(String, nullable=True)
    translated_audio_path = Column(String, nullable=True)
    final_video_path = Column(String, nullable=True)

    # Status tracking
    status = Column(String, default="pending")  # pending, processing, completed, failed
    current_step = Column(String, default="upload")
    progress = Column(Float, default=0.0)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    error_message = Column(String, nullable=True)
