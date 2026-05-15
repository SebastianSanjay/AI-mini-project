import json
import torch
import httpx
import os
from typing import Protocol
from config import settings
from utils.logger import logger
import ffmpeg

class TTSProvider(Protocol):
    def generate_audio(self, translated_transcript_path: str, output_audio_path: str, target_language_code: str, original_audio_path: str) -> str:
        ...

class CoquiTTSProvider:
    def __init__(self):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model = None

    def _load_model(self):
        if self.model is None:
            from TTS.api import TTS
            logger.info(f"Loading Coqui TTS model on {self.device}...")
            # Using xtts_v2 for multilingual support
            self.model = TTS("tts_models/multilingual/multi-dataset/xtts_v2").to(self.device)

    def generate_audio(self, translated_transcript_path: str, output_audio_path: str, target_language_code: str, original_audio_path: str) -> str:
        self._load_model()

        with open(translated_transcript_path, 'r', encoding='utf-8') as f:
            transcript = json.load(f)

        full_text = " ".join([seg['text'] for seg in transcript.get('segments', [])])

        # XTTS requires a speaker wav for voice cloning.
        # We will use the original extracted audio path.
        if not os.path.exists(original_audio_path):
            logger.error(f"Original audio not found at {original_audio_path}, XTTS voice cloning will fail.")
            raise FileNotFoundError(f"Original audio not found at {original_audio_path}")

        self.model.tts_to_file(
            text=full_text,
            speaker_wav=original_audio_path,
            language=target_language_code,
            file_path=output_audio_path
        )

        # Audio length adjustment logic (speedup/slowdown) using ffmpeg filter 'atempo'
        # based on transcript start/end could be added here.
        return output_audio_path

class ElevenLabsProvider:
    def generate_audio(self, translated_transcript_path: str, output_audio_path: str, target_language_code: str, original_audio_path: str) -> str:
        if not settings.ELEVENLABS_API_KEY:
            raise ValueError("ELEVENLABS_API_KEY is not set")

        with open(translated_transcript_path, 'r', encoding='utf-8') as f:
            transcript = json.load(f)

        full_text = " ".join([seg['text'] for seg in transcript.get('segments', [])])

        # Default voice ID for demonstration
        voice_id = "21m00Tcm4TlvDq8ikWAM"
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"

        headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": settings.ELEVENLABS_API_KEY
        }

        data = {
            "text": full_text,
            "model_id": "eleven_multilingual_v2",
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.5
            }
        }

        response = httpx.post(url, json=data, headers=headers, timeout=60.0)
        response.raise_for_status()

        with open(output_audio_path, 'wb') as f:
            f.write(response.content)

        return output_audio_path

def get_tts_provider() -> TTSProvider:
    if settings.TTS_PROVIDER == "coqui":
        return CoquiTTSProvider()
    elif settings.TTS_PROVIDER == "elevenlabs":
        return ElevenLabsProvider()
    else:
        raise ValueError(f"Unknown TTS provider: {settings.TTS_PROVIDER}")

def generate_voice(translated_transcript_path: str, output_audio_path: str, target_language_code: str, original_audio_path: str) -> str:
    provider = get_tts_provider()
    return provider.generate_audio(translated_transcript_path, output_audio_path, target_language_code, original_audio_path)
