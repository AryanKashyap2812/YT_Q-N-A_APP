# YouTube Video Q&A App

This app lets you ask questions about YouTube videos or audio files by extracting or generating transcripts (even for videos without official transcripts) and leveraging embeddings for context-aware answers.

## Features
- Input multiple YouTube URLs or upload audio files (mp3, mp4, wav, m4a).
- Fetch official YouTube transcripts or generate them robustly using Whisper (with automatic fallback to smaller models if needed).
- Uses `yt-dlp` and `ffmpeg` to extract audio from YouTube videos for transcription.
- Automatic language detection and transcript chunking.
- Embedding-based semantic search with FAISS.
- Contextual question answering using Hugging Face LLMs.
- Chat history tracking and PDF download of Q&A.
- Automatic cache and temporary audio cleanup to save space.
- Detailed logging to both terminal and `app.log` for debugging and transparency.

## Setup
1. **Clone the repo:**
   ```bash
   git clone <repo-url>
   cd YT_Q&A_APP
   ```
2. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
3. **Install system dependencies:**
   - [yt-dlp](https://github.com/yt-dlp/yt-dlp):
     ```bash
     pip install yt-dlp
     ```
   - [ffmpeg](https://ffmpeg.org/download.html):
     - On Ubuntu: `sudo apt install ffmpeg`
     - On Mac: `brew install ffmpeg`
     - On Windows: [Download and add to PATH](https://ffmpeg.org/download.html)
4. **Install Whisper (if not already):**
   ```bash
   pip install openai-whisper
   ```
5. **Set your Hugging Face API token:**
   - Get a token from https://huggingface.co/settings/tokens
   - Set it in your environment:
     ```bash
     export HF_TOKEN=your_huggingface_token
     ```
6. **(Optional) Set Whisper model size:**
   - By default, the app uses the `medium` model. To use a different size (e.g., `small` or `tiny`), set:
     ```bash
     export WHISPER_MODEL_SIZE=small
     ```
7. **Run the app:**
   ```bash
   streamlit run app.py
   ```
8. **Provide YouTube URLs or upload audio and ask questions!**

## How It Works
- For each YouTube URL:
  - Tries to fetch the official transcript (English, then Hindi).
  - If unavailable, downloads audio using `yt-dlp` and `ffmpeg`, then transcribes with Whisper.
  - If the main Whisper model fails, automatically falls back to `small` and then `tiny` models.
  - All steps and errors are logged to `app.log` and the terminal.
- For uploaded audio files:
  - Transcribes directly with Whisper (with fallback logic).
- All transcripts are cached for faster future access.
- Embeddings are generated and stored with FAISS for semantic search.
- Questions are answered using a Hugging Face LLM (via API).

## Troubleshooting
- **Transcript not generated?**
  - Check `app.log` for detailed error messages and processing steps.
  - Ensure `yt-dlp` and `ffmpeg` are installed and available in your PATH.
  - Try running `yt-dlp` and Whisper manually on the problematic video/audio for debugging.
- **App says 'No valid transcripts found'?**
  - The video may be restricted, private, or have download/transcript disabled.
  - Try a different video or check your network connection.
- **Whisper runs out of memory?**
  - Use a smaller model: `export WHISPER_MODEL_SIZE=small` or `tiny`.
- **Hugging Face API errors?**
  - Make sure your `HF_TOKEN` is set and valid.
  - Check your API usage limits.

## Notes
- Cache and temporary files are stored in `cache/` and `temp_audio/` folders.
- Cached files older than 1 day are deleted automatically.
- All logs are written to `app.log` for easy debugging.
- The app uses the Hugging Face Inference API for LLM-based question answering.
- You must set the `HF_TOKEN` environment variable for the app to work.

## License
MIT License
