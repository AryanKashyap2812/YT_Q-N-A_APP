from youtube_transcript_api import YouTubeTranscriptApi
import subprocess
import os
import logging
from langdetect import detect
from utils.whisper_utils import generate_transcript

LANGUAGE_MAP = {
    "en": "english",
    "hi": "hindi",
    "es": "spanish",
    "fr": "french",
    "de": "german",
    "it": "italian",
    "ru": "russian",
    "zh-cn": "chinese",
    "ja": "japanese",
    "ar": "arabic",
    # Add more as needed
}

def extract_video_id(url):
    return url.split("v=")[-1].split("&")[0]

def detect_language(text):
    try:
        lang_code = detect(text)
        return LANGUAGE_MAP.get(lang_code, "english")
    except Exception as e:
        logging.warning(f"Language detection failed: {e}")
        return "english"

def get_transcript_or_generate(url=None, audio_path=None):
    if audio_path:
        transcript = generate_transcript(audio_path)
        if transcript.strip().startswith('[ERROR]'):
            try:
                import whisper
                fallback_model = whisper.load_model("small")
                transcript_result = fallback_model.transcribe(audio_path)
                transcript = transcript_result["text"]
            except Exception as e:
                logging.error(f"Fallback Whisper model also failed: {e}")
                return f"[ERROR] Whisper fallback failed: {e}"
        lang = detect_language(transcript)
        return f"[{lang.upper()} TRANSCRIPT]\n" + transcript

    video_id = extract_video_id(url)
    transcript = None
    try:
        try:
            transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['en'])
        except Exception:
            try:
                transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['hi'])
            except Exception:
                transcript = None
        if transcript:
            text = " ".join([entry['text'] for entry in transcript])
            lang = detect_language(text)
            return f"[{lang.upper()} TRANSCRIPT]\n" + text
        else:
            logging.warning(f"No transcript found for {url}, falling back to Whisper.")
            # Fallback to Whisper for any missing transcript
            audio_dir = "temp_audio"
            os.makedirs(audio_dir, exist_ok=True)
            audio_path = os.path.join(audio_dir, f"{video_id}.mp3")
            yt_dlp_cmd = [
                "yt-dlp", "-x", "--audio-format", "mp3", "-o", audio_path, url
            ]
            result = subprocess.run(yt_dlp_cmd, capture_output=True, text=True)
            if result.returncode != 0 or not os.path.exists(audio_path):
                logging.error(f"yt-dlp failed: {result.stderr}")
                return f"[ERROR] yt-dlp failed to download audio: {result.stderr}"
            transcript = generate_transcript(audio_path)
            if transcript.strip().startswith('[ERROR]'):
                try:
                    import whisper
                    logging.warning(f"Main Whisper model failed, trying 'small' model for {url}")
                    fallback_model = whisper.load_model("small")
                    transcript_result = fallback_model.transcribe(audio_path)
                    transcript = transcript_result["text"]
                except Exception as e:
                    logging.error(f"'small' Whisper model also failed: {e}")
                    try:
                        logging.warning(f"Trying 'tiny' Whisper model for {url}")
                        tiny_model = whisper.load_model("tiny")
                        transcript_result = tiny_model.transcribe(audio_path)
                        transcript = transcript_result["text"]
                    except Exception as e2:
                        logging.error(f"'tiny' Whisper model also failed: {e2}")
                        return f"[ERROR] Whisper fallback failed: {e} | Tiny model: {e2}"
            if os.path.exists(audio_path):
                os.remove(audio_path)
            lang = detect_language(transcript)
            return f"[{lang.upper()} TRANSCRIPT]\n" + transcript
    except Exception as e:
        logging.error(f"Failed to get transcript or generate with Whisper for {url}: {e}")
        return f"[ERROR] Could not retrieve or generate transcript for this video: {e}"
