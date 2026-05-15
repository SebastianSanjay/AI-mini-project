import os
import subprocess
import torch
from config import settings
from utils.logger import logger

def lip_sync(video_path: str, audio_path: str, output_video_path: str) -> str:
    """
    Applies Wav2Lip to synchronize the video's lip movements with the new audio.
    Assumes Wav2Lip repository is cloned in /app/Wav2Lip inside the Docker container.
    """
    wav2lip_dir = os.environ.get("WAV2LIP_DIR", "/app/Wav2Lip")
    checkpoint_path = settings.WAV2LIP_CHECKPOINT_PATH

    if not os.path.exists(wav2lip_dir):
        logger.error(f"Wav2Lip directory not found at {wav2lip_dir}")
        raise FileNotFoundError(f"Wav2Lip directory not found at {wav2lip_dir}")

    if not os.path.exists(checkpoint_path):
        logger.error(f"Wav2Lip checkpoint not found at {checkpoint_path}")
        raise FileNotFoundError(f"Wav2Lip checkpoint not found at {checkpoint_path}")

    # Determine if we can use GPU
    device = "cuda" if torch.cuda.is_available() else "cpu"

    # We call Wav2Lip inference.py via subprocess.
    # This is often the cleanest way to integrate research code without rewriting it.
    cmd = [
        "python", os.path.join(wav2lip_dir, "inference.py"),
        "--checkpoint_path", checkpoint_path,
        "--face", video_path,
        "--audio", audio_path,
        "--outfile", output_video_path,
        "--pads", "0", "20", "0", "0"  # Typical padding for better mouth detection
    ]

    if device == "cpu":
        cmd.append("--nosmooth") # Sometimes needed on CPU

    logger.info(f"Running Wav2Lip lip-sync: {' '.join(cmd)}")

    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        logger.info("Wav2Lip completed successfully.")
        logger.debug(result.stdout)
    except subprocess.CalledProcessError as e:
        logger.error(f"Wav2Lip failed: {e.stderr}")
        raise RuntimeError(f"Wav2Lip failed: {e.stderr}")

    return output_video_path
