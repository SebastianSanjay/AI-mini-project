from utils.ffmpeg_utils import extract_audio as ffmpeg_extract_audio
from utils.logger import logger

def extract_audio(video_path: str, output_audio_path: str) -> str:
    """
    Extracts the audio track from the uploaded video.
    """
    logger.info(f"Extracting audio from {video_path} to {output_audio_path}")
    ffmpeg_extract_audio(video_path, output_audio_path)
    return output_audio_path
