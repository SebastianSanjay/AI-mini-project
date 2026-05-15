import whisper
import torch
import json
from utils.logger import logger

# Global model cache so we don't reload it every task if workers are long-lived.
_whisper_model = None

def get_whisper_model():
    global _whisper_model
    if _whisper_model is None:
        device = "cuda" if torch.cuda.is_available() else "cpu"
        logger.info(f"Loading Whisper model on {device}...")
        _whisper_model = whisper.load_model("base", device=device)
    return _whisper_model

def transcribe(audio_path: str, transcript_path: str, source_language: str = None) -> str:
    """
    Transcribes the audio using OpenAI Whisper.
    Returns the path to the JSON transcript.
    """
    model = get_whisper_model()

    logger.info(f"Transcribing {audio_path}...")

    # Options for transcription
    options = {}
    if source_language:
        options["language"] = source_language

    result = model.transcribe(audio_path, **options)

    # Save the full result (including segments with timestamps) to JSON
    with open(transcript_path, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    logger.info(f"Transcription saved to {transcript_path}")
    return transcript_path
