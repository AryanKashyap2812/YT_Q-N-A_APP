import os

# Directories
CACHE_DIR = os.environ.get("CACHE_DIR", "cache")  # Directory for cached files
TEMP_AUDIO_DIR = os.environ.get("TEMP_AUDIO_DIR", "temp_audio")  # Directory for temporary audio files

# Expiry
CACHE_EXPIRY_SECONDS = int(os.environ.get("CACHE_EXPIRY_SECONDS", 24 * 3600))  # Cache expiry in seconds (default: 1 day)

# Model names
EMBEDDING_MODEL_NAME = os.environ.get("EMBEDDING_MODEL_NAME", "all-mpnet-base-v2")
QA_MODEL_NAME = os.environ.get("QA_MODEL_NAME", "deepset/roberta-base-squad2")
WHISPER_MODEL_NAME = os.environ.get("WHISPER_MODEL_NAME", "small")

"""
Configuration module for the YT_Q&A_APP.
All values can be overridden by environment variables for flexible deployment.
"""
