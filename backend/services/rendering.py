import os
from utils.ffmpeg_utils import merge_audio_video
from utils.logger import logger

def render_final_video(lip_synced_video_path: str, generated_audio_path: str, output_path: str) -> str:
    """
    Renders the final video. If Wav2Lip was successful, it inherently outputs a video
    with the new audio combined. However, sometimes we need to do a final pass,
    burn subtitles, or simply move the file.

    For now, Wav2Lip output is the final merged file, but we will ensure it's properly
    formatted or remuxed using ffmpeg if necessary.
    """
    logger.info(f"Rendering final video to {output_path}")

    # In many setups, Wav2Lip's output is already merged. If so, we can just copy or remux.
    # We will do a safe remux to ensure standard MP4 compliance.
    try:
        import ffmpeg
        (
            ffmpeg
            .input(lip_synced_video_path)
            .output(output_path, vcodec='copy', acodec='copy')
            .overwrite_output()
            .run(capture_stdout=True, capture_stderr=True)
        )
        logger.info(f"Final video rendered successfully at {output_path}")
    except Exception as e:
        logger.error(f"Error rendering final video: {e}")
        # Fallback to just copying
        import shutil
        shutil.copy2(lip_synced_video_path, output_path)

    return output_path
