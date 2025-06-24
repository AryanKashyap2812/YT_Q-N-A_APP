import os
import requests
from utils.embedding_utils import load_vectorstore
import numpy as np
import logging

def ask_question(question, top_k=5, hf_model="HuggingFaceH4/zephyr-7b-beta"):
    """
    Answers a question using the most relevant chunks from the vectorstore, via Hugging Face Inference API LLM.
    Returns a string answer or an error message if data/model is missing.
    """
    index, chunks = load_vectorstore()
    if index is None or chunks is None:
        logging.warning("No vectorstore or chunks available for QA.")
        return "No data to answer the question."
    try:
        from utils.embedding_utils import embedding_model
        q_emb = embedding_model.encode([question])
        D, I = index.search(np.array(q_emb), top_k)
        context = "\n\n".join([chunks[i] for i in I[0]])
        prompt = (
            "You are a helpful assistant. Use the following context to answer the user's question as accurately as possible.\n\n"
            f"Context:\n{context}\n\n"
            f"Question: {question}\nAnswer:"
        )
        hf_token = os.environ.get("HF_TOKEN")
        if not hf_token:
            return "[ERROR] Hugging Face API token (HF_TOKEN) not set."
        api_url = f"https://api-inference.huggingface.co/models/{hf_model}"
        headers = {"Authorization": f"Bearer {hf_token}"}
        payload = {"inputs": prompt, "parameters": {"max_new_tokens": 256, "temperature": 0.2}}
        response = requests.post(api_url, headers=headers, json=payload, timeout=60)
        if response.status_code != 200:
            logging.error(f"HF API error: {response.status_code} {response.text}")
            return f"[ERROR] Hugging Face API error: {response.status_code}"
        result = response.json()
        # The output format may vary by model; handle both 'generated_text' and list of dicts
        if isinstance(result, list) and 'generated_text' in result[0]:
            answer = result[0]['generated_text'].strip()
        elif isinstance(result, dict) and 'generated_text' in result:
            answer = result['generated_text'].strip()
        elif isinstance(result, list) and 'text' in result[0]:
            answer = result[0]['text'].strip()
        else:
            answer = str(result)
        # Optionally, remove the prompt from the answer if model echoes it
        if answer.startswith(prompt):
            answer = answer[len(prompt):].strip()
        return answer
    except Exception as e:
        logging.error(f"LLM QA failed: {e}")
        return f"[ERROR] LLM QA failed: {e}"
