import ffmpeg
from utils.logger import logger

def extract_audio(video_path: str, output_audio_path: str) -> None:
    try:
        (
            ffmpeg
            .input(video_path)
            .output(output_audio_path, acodec='pcm_s16le', ac=1, ar='16k')
            .overwrite_output()
            .run(capture_stdout=True, capture_stderr=True)
        )
    except ffmpeg.Error as e:
        logger.error(f"FFmpeg audio extraction error: {e.stderr.decode()}")
        raise RuntimeError(f"Failed to extract audio: {e.stderr.decode()}")

def merge_audio_video(video_path: str, audio_path: str, output_path: str) -> None:
    try:
        video = ffmpeg.input(video_path)
        audio = ffmpeg.input(audio_path)

        (
            ffmpeg
            .output(video.video, audio.audio, output_path, vcodec='libx264', acodec='aac', strict='experimental')
            .overwrite_output()
            .run(capture_stdout=True, capture_stderr=True)
        )
    except ffmpeg.Error as e:
        logger.error(f"FFmpeg merge error: {e.stderr.decode()}")
        raise RuntimeError(f"Failed to merge audio and video: {e.stderr.decode()}")
