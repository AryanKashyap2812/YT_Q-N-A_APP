import re

def chunk_text(text, max_length=2000):
    """
    Splits text into chunks of up to max_length words, trying to split at sentence boundaries.
    Handles edge cases where a sentence is longer than max_length by splitting it further.
    Returns a list of non-empty, stripped chunks.
    """
    sentences = re.split(r'(?<=[.!?]) +', text)
    chunks = []
    current_chunk = []
    current_len = 0
    for sentence in sentences:
        words = sentence.split()
        if not words:
            continue
        if current_len + len(words) <= max_length:
            current_chunk.extend(words)
            current_len += len(words)
        else:
            if current_chunk:
                chunks.append(' '.join(current_chunk).strip())
            # If the sentence itself is longer than max_length, split it
            while len(words) > max_length:
                chunks.append(' '.join(words[:max_length]).strip())
                words = words[max_length:]
            current_chunk = words
            current_len = len(words)
    if current_chunk:
        chunks.append(' '.join(current_chunk).strip())
    # Remove any empty chunks
    return [chunk for chunk in chunks if chunk]
