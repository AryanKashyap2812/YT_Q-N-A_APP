import os
import time
import logging

CACHE_DIR = "cache"
TEMP_AUDIO_DIR = "temp_audio"
CACHE_EXPIRY_SECONDS = 24 * 3600  # 1 day

def cleanup_old_files():
    """
    Removes files older than CACHE_EXPIRY_SECONDS from cache and temp audio directories.
    Logs actions and errors for better traceability.
    """
    current_time = time.time()
    for folder in [CACHE_DIR, TEMP_AUDIO_DIR]:
        if not os.path.exists(folder):
            continue
        for filename in os.listdir(folder):
            filepath = os.path.join(folder, filename)
            if os.path.isfile(filepath):
                file_age = current_time - os.path.getmtime(filepath)
                if file_age > CACHE_EXPIRY_SECONDS:
                    try:
                        os.remove(filepath)
                        logging.info(f"Deleted old file: {filepath}")
                    except Exception as e:
                        logging.warning(f"Failed to delete {filepath}: {e}")
