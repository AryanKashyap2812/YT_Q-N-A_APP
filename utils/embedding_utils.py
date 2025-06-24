from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import os
import pickle
import logging

EMBEDDING_MODEL_NAME = os.environ.get("EMBEDDING_MODEL_NAME", "all-mpnet-base-v2")
VECTORSTORE_PATH = "cache/vectorstore.faiss"
EMBEDDINGS_PATH = "cache/embeddings.pkl"

# Load embedding model once
try:
    embedding_model = SentenceTransformer(EMBEDDING_MODEL_NAME)
except Exception as e:
    logging.error(f"Failed to load embedding model: {e}")
    embedding_model = None

def store_embeddings(chunks):
    """
    Encodes text chunks, stores embeddings in a FAISS index, and saves both index and chunks to disk.
    """
    if embedding_model is None:
        logging.error("Embedding model is not loaded.")
        return
    try:
        embeddings = embedding_model.encode(chunks)
        dimension = embeddings.shape[1]
        index = faiss.IndexFlatL2(dimension)
        index.add(np.array(embeddings))
        os.makedirs("cache", exist_ok=True)
        faiss.write_index(index, VECTORSTORE_PATH)
        with open(EMBEDDINGS_PATH, "wb") as f:
            pickle.dump(chunks, f)
        logging.info(f"Stored {len(chunks)} embeddings and index.")
    except Exception as e:
        logging.error(f"Failed to store embeddings: {e}")

def load_vectorstore():
    """
    Loads the FAISS index and text chunks from disk. Returns (index, chunks) or (None, None) if not found.
    """
    if not os.path.exists(VECTORSTORE_PATH) or not os.path.exists(EMBEDDINGS_PATH):
        logging.warning("Vectorstore or embeddings file not found.")
        return None, None
    try:
        index = faiss.read_index(VECTORSTORE_PATH)
        with open(EMBEDDINGS_PATH, "rb") as f:
            chunks = pickle.load(f)
        return index, chunks
    except Exception as e:
        logging.error(f"Failed to load vectorstore: {e}")
        return None, None
