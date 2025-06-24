from youtube_transcript_api import YouTubeTranscriptApi, NoTranscriptFound, TranscriptsDisabled
from fpdf import FPDF
import io
import logging

def get_transcript_or_generate(video_id, audio_path=None, languages=['en', 'hi']):
    """
    Attempts to fetch a transcript for a YouTube video in preferred languages, falling back to Hindi if needed.
    Handles errors gracefully and logs issues. If audio_path is provided, uses audio transcription logic.
    """
    if video_id:
        try:
            transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=languages)
            return " ".join([t['text'] for t in transcript])
        except NoTranscriptFound:
            try:
                transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['hi'])
                return " ".join([t['text'] for t in transcript])
            except Exception as e:
                logging.warning(f"No transcript found for video {video_id} in preferred languages: {e}")
                return f"[ERROR] No transcript found for video {video_id} in preferred languages."
        except TranscriptsDisabled:
            logging.warning(f"Transcripts are disabled for video {video_id}.")
            return f"[ERROR] Transcripts are disabled for this video."
        except Exception as e:
            logging.error(f"Error fetching transcript for video {video_id}: {e}")
            return f"[ERROR] Error fetching transcript: {e}"
    elif audio_path:
        # Placeholder for audio transcription logic
        logging.warning("Audio transcription logic not implemented in pdf_utils.py.")
        return "[ERROR] Audio transcription not implemented."
    else:
        logging.error("No video_id or audio_path provided to get_transcript_or_generate.")
        return "[ERROR] No video_id or audio_path provided."


def generate_pdf(chat_history):
    """
    Generates a PDF from chat history (list of (question, answer) tuples) and returns it as bytes.
    """
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_font("Arial", size=12)

    for q, a in chat_history:
        pdf.set_text_color(0, 0, 128)
        pdf.multi_cell(0, 10, f"Q: {q}")
        pdf.set_text_color(0, 0, 0)
        pdf.multi_cell(0, 10, f"A: {a}")
        pdf.ln()

    pdf_bytes = pdf.output(dest='S').encode('latin1')
    pdf_output = io.BytesIO(pdf_bytes)
    pdf_output.seek(0)
    return pdf_output.read()
