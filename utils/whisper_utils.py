import whisper
import logging
import os

# Load the model once (small model to save resources and speed up transcription)
try:
    model = whisper.load_model(os.environ.get("WHISPER_MODEL_SIZE", "small"))
except Exception as e:
    logging.error(f"Failed to load Whisper model: {e}")
    model = None

def generate_transcript(audio_path):
    if model is None:
        logging.error("Whisper model is not loaded.")
        return "[ERROR] Whisper model not loaded."
    try:
        logging.info(f"Transcribing audio: {audio_path}")
        result = model.transcribe(audio_path)
        return result["text"]
    except Exception as e:
        logging.error(f"Transcription failed for {audio_path}: {e}")
        return f"[ERROR] Transcription failed: {e}"
