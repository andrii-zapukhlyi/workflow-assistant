from typing import Any
import requests
from numpy import ndarray
from backend.config.settings import HF_API_TOKEN
import re
from sentence_transformers import SentenceTransformer

def chunk_text(text: str) -> list[str]:
    chunks = re.split(r"(?=\n## )", text)
    chunks = [chunk.strip() for chunk in chunks if chunk.strip()]
    return chunks

def embed_text(texts: list, locally: bool = True) -> list[list | Any] | ndarray:
    if isinstance(texts, str):
        texts = [texts]

    if locally:
        model = SentenceTransformer('all-MiniLM-L6-v2', device='cuda:0')
        embeddings = model.encode(texts, convert_to_numpy=True, batch_size=16, show_progress_bar=True)
        return embeddings

    else:
        url = "https://router.huggingface.co/hf-inference/models/sentence-transformers/all-MiniLM-L6-v2/pipeline/feature-extraction"
        headers = {
            "Authorization": f"Bearer {HF_API_TOKEN}",
            "Content-Type": "application/json"
        }
        response = requests.post(url, headers=headers, json={"inputs": texts})
        response.raise_for_status()
        embeddings = response.json()
        return [e[0] if isinstance(e, list) and isinstance(e[0], list) else e for e in embeddings]

def chunk_and_embed_documents(documents: list[dict[str, str]]) -> tuple[list[str], list[list | Any] | ndarray, list[dict[str, Any]]]:
    chunks = []
    embeddings = []
    metadata = []

    for doc in documents:
        chunked_text = chunk_text(doc["text"])
        embedded_text = embed_text(chunked_text, locally=True)

        for idx, (chunk, embedding) in enumerate(zip(chunked_text, embedded_text)):
            chunks.append(chunk)
            embeddings.append(embedding)
            metadata.append({
                "page_title": doc["title"],
                "page_link": doc["link"],
                "chunk_index": idx,
                "total_chunks": len(chunked_text)
            })

    return chunks, embeddings, metadata