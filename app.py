import streamlit as st
from utils.youtube_utils import get_transcript_or_generate
from utils.text_processing import chunk_text
from utils.embedding_utils import store_embeddings, load_vectorstore
from utils.qa_chain import ask_question
from utils.cleanup_utils import cleanup_old_files
from utils.pdf_utils import generate_pdf
import os
import hashlib
import logging
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    handlers=[
        logging.FileHandler("app.log"),
        logging.StreamHandler()
    ]
)

st.title("YouTube Video Q&A App")

video_url = st.text_area("Enter one or more YouTube Video URLs (one per line)")
question = st.text_input("Ask a question about the videos or audio")
audio_file = st.file_uploader("Or upload a custom audio file", type=["mp3", "mp4", "wav", "m4a"])

if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

# Cleanup old cache and temp audio files daily
cleanup_old_files()

# Helper to get audio duration (in seconds)
def get_audio_duration(audio_path):
    try:
        import wave
        import contextlib
        if audio_path.endswith('.mp3') or audio_path.endswith('.m4a'):
            import mutagen
            from mutagen.mp3 import MP3
            from mutagen.mp4 import MP4
            if audio_path.endswith('.mp3'):
                return MP3(audio_path).info.length
            elif audio_path.endswith('.m4a'):
                return MP4(audio_path).info.length
        elif audio_path.endswith('.wav'):
            with contextlib.closing(wave.open(audio_path,'r')) as f:
                frames = f.getnframes()
                rate = f.getframerate()
                return frames / float(rate)
    except Exception:
        return None

if st.button("Submit") and question:
    all_chunks = []
    try:
        with st.spinner("Processing input..."):
            cache_dir = "cache"
            os.makedirs(cache_dir, exist_ok=True)
            processed_any = False

            # Process audio file if provided
            if audio_file:
                audio_path = os.path.join("temp_audio", audio_file.name)
                os.makedirs("temp_audio", exist_ok=True)
                with open(audio_path, "wb") as f:
                    f.write(audio_file.read())
                hash_id = hashlib.md5(audio_path.encode()).hexdigest()
                cache_file = os.path.join(cache_dir, f"{hash_id}.txt")

                if os.path.exists(cache_file):
                    with open(cache_file, "r") as f:
                        transcript = f.read()
                else:
                    st.info("Transcribing uploaded audio with Whisper...")
                    try:
                        duration = get_audio_duration(audio_path)
                        if duration and duration > 600:
                            st.warning(f"Uploaded audio is long ({int(duration//60)} min). Transcription may take a while.")
                        transcript = get_transcript_or_generate(None, audio_path)
                        with open(cache_file, "w") as f:
                            f.write(transcript)
                    except RuntimeError as e:
                        st.warning(f"Audio file: {e}")
                        transcript = None
                if transcript:
                    chunks = chunk_text(transcript)
                    all_chunks.extend(chunks)
                    processed_any = True

            # Process YouTube URLs if provided
            if video_url:
                urls = video_url.strip().splitlines()
                for url in urls:
                    if not url.strip():
                        continue
                    video_id = url.split("v=")[-1].split("&")[0]
                    cache_file = os.path.join(cache_dir, f"{video_id}.txt")
                    if os.path.exists(cache_file):
                        with open(cache_file, "r") as f:
                            transcript = f.read()
                    else:
                        st.info(f"Processing {url}...")
                        try:
                            transcript = get_transcript_or_generate(url)
                            # Handle Whisper/YouTube transcript errors
                            if transcript and transcript.strip().startswith('[ERROR]'):
                                st.warning(f"{url}: {transcript}")
                                transcript = None
                            else:
                                with open(cache_file, "w") as f:
                                    f.write(transcript)
                        except RuntimeError as e:
                            st.warning(f"{url}: {e}")
                            transcript = None
                    if transcript:
                        # Try to warn if video is long (if audio file exists)
                        audio_path = os.path.join("temp_audio", f"{video_id}.mp3")
                        duration = get_audio_duration(audio_path) if os.path.exists(audio_path) else None
                        if duration and duration > 900:
                            st.warning(f"Video {url} is long ({int(duration//60)} min). Transcription may take a while.")
                        chunks = chunk_text(transcript)
                        all_chunks.extend(chunks)
                        logging.info(f"Processed {url}")
                if urls:
                    processed_any = True

            if not processed_any or not all_chunks:
                st.warning("No valid transcripts found. Please provide a valid YouTube link or upload an audio file.")
                st.stop()

            st.info("Generating embeddings and answering your question...")
            store_embeddings(all_chunks)
            answer = ask_question(question)

        st.session_state.chat_history.append((question, answer))
        st.success("Answer")
        st.write(answer)

    except Exception as e:
        logging.error(f"Error: {e}")
        st.error("An error occurred while processing. Please check logs.")

if st.session_state.chat_history:
    with st.expander("Chat History"):
        for q, a in st.session_state.chat_history:
            st.markdown(f"**Q:** {q}")
            st.markdown(f"**A:** {a}")
    # Show a single download button outside the expander
    pdf_bytes = generate_pdf(st.session_state.chat_history)
    st.download_button("Download Q&A as PDF", data=pdf_bytes, file_name="youtube_qa_chat.pdf", mime="application/pdf")
