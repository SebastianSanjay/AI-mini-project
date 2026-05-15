import json
import httpx
import torch
from typing import Protocol
from config import settings
from utils.logger import logger

class TranslationProvider(Protocol):
    def translate_transcript(self, transcript_path: str, target_language_code: str, source_language_code: str = None) -> str:
        ...

class SeamlessM4TProvider:
    def __init__(self):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.processor = None
        self.model = None

    def _load_model(self):
        if self.model is None:
            from transformers import AutoProcessor, SeamlessM4Tv2Model
            logger.info(f"Loading SeamlessM4T model on {self.device}...")
            # Using base model, can be upgraded to large in prod
            self.processor = AutoProcessor.from_pretrained("facebook/seamless-m4t-v2-large")
            self.model = SeamlessM4Tv2Model.from_pretrained("facebook/seamless-m4t-v2-large").to(self.device)

    def translate_transcript(self, transcript_path: str, target_language_code: str, source_language_code: str = None) -> str:
        self._load_model()

        with open(transcript_path, 'r', encoding='utf-8') as f:
            transcript = json.load(f)

        translated_segments = []
        for segment in transcript.get('segments', []):
            text = segment['text'].strip()
            if not text:
                continue

            # Process text input
            src_lang = source_language_code or transcript.get('language', 'eng')
            # Adjust lang codes for SeamlessM4T format if needed. Here we assume BCP-47 mostly works.
            inputs = self.processor(text=text, src_lang=src_lang, return_tensors="pt").to(self.device)

            with torch.no_grad():
                output_tokens = self.model.generate(**inputs, tgt_lang=target_language_code, generate_speech=False)

            translated_text = self.processor.decode(output_tokens[0].tolist()[0], skip_special_tokens=True)

            translated_segments.append({
                "start": segment["start"],
                "end": segment["end"],
                "text": translated_text
            })

        translated_transcript_path = transcript_path.replace(".json", f"_translated_{target_language_code}.json")
        with open(translated_transcript_path, 'w', encoding='utf-8') as f:
            json.dump({"segments": translated_segments}, f, ensure_ascii=False, indent=2)

        return translated_transcript_path

class GoogleTranslateProvider:
    def translate_transcript(self, transcript_path: str, target_language_code: str, source_language_code: str = None) -> str:
        # Note: In a real app, use the google-cloud-translate library.
        # This is a functional mock using a generic REST API approach for demonstration of the interface.
        if not settings.GOOGLE_TRANSLATE_API_KEY:
            raise ValueError("GOOGLE_TRANSLATE_API_KEY is not set")

        with open(transcript_path, 'r', encoding='utf-8') as f:
            transcript = json.load(f)

        translated_segments = []
        # In a real implementation, you'd batch these requests
        for segment in transcript.get('segments', []):
            text = segment['text'].strip()
            if not text:
                continue

            url = f"https://translation.googleapis.com/language/translate/v2?key={settings.GOOGLE_TRANSLATE_API_KEY}"
            data = {
                "q": text,
                "target": target_language_code
            }
            if source_language_code:
                data["source"] = source_language_code

            response = httpx.post(url, json=data).json()
            translated_text = response['data']['translations'][0]['translatedText']

            translated_segments.append({
                "start": segment["start"],
                "end": segment["end"],
                "text": translated_text
            })

        translated_transcript_path = transcript_path.replace(".json", f"_translated_{target_language_code}.json")
        with open(translated_transcript_path, 'w', encoding='utf-8') as f:
            json.dump({"segments": translated_segments}, f, ensure_ascii=False, indent=2)

        return translated_transcript_path

def get_translation_provider() -> TranslationProvider:
    if settings.TRANSLATION_PROVIDER == "seamlessm4t":
        return SeamlessM4TProvider()
    elif settings.TRANSLATION_PROVIDER == "google":
        return GoogleTranslateProvider()
    else:
        raise ValueError(f"Unknown translation provider: {settings.TRANSLATION_PROVIDER}")

def translate(transcript_path: str, target_language_code: str, source_language_code: str = None) -> str:
    provider = get_translation_provider()
    return provider.translate_transcript(transcript_path, target_language_code, source_language_code)
