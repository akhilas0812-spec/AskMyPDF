# backend/retriever.py
import json
import numpy as np
from sentence_transformers import SentenceTransformer

MODEL_NAME = "all-MiniLM-L6-v2"  # light & fast
model = SentenceTransformer(MODEL_NAME)

def load_chunks(path="data/chunks.json"):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def embed_text_list(text_list):
    return model.encode(text_list, convert_to_numpy=True, show_progress_bar=False)

def retrieve_relevant_chunks(query, chunks, top_k=5):
    if not chunks:
        return []
    query_embedding = model.encode([query], convert_to_numpy=True)[0]
    chunk_embeddings = embed_text_list(chunks)  # (n, d)
    # cosine similarity via dot of normalized vectors
    # normalize
    def normalize(a):
        return a / np.linalg.norm(a, axis=1, keepdims=True)
    emb_norm = normalize(chunk_embeddings)
    q_norm = query_embedding / np.linalg.norm(query_embedding)
    scores = (emb_norm @ q_norm).astype(float)
    top_indices = scores.argsort()[-top_k:][::-1]
    results = []
    for idx in top_indices:
        results.append({
            "chunk": chunks[int(idx)],
            "score": float(scores[int(idx)]),
            "index": int(idx)
        })
    return results
