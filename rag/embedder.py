import requests
from config.settings import HF_API_TOKEN
import re
from sentence_transformers import SentenceTransformer

def chunk_text(text):
    chunks = re.split(r"(?=\n## )", text)
    chunks = [chunk.strip() for chunk in chunks if chunk.strip()]
    return chunks

def embed_text(texts):
    if isinstance(texts, str):
        texts = [texts]

    url = "https://router.huggingface.co/hf-inference/models/sentence-transformers/all-MiniLM-L6-v2/pipeline/feature-extraction"
    headers = {
        "Authorization": f"Bearer {HF_API_TOKEN}",
        "Content-Type": "application/json"
    }
    response = requests.post(url, headers=headers, json={"inputs": texts})
    response.raise_for_status()
    embeddings = response.json()
    return [e[0] if isinstance(e, list) and isinstance(e[0], list) else e for e in embeddings]

def embed_text_local(texts):
    if isinstance(texts, str):
        texts = [texts]
    model = SentenceTransformer('all-MiniLM-L6-v2', device='cuda:0')
    embeddings = model.encode(texts, convert_to_numpy=True, batch_size=16, show_progress_bar=True)
    return embeddings

def chunk_and_embed_documents(documents):
    chunked_pages = []

    for doc in documents:
        chunks = chunk_text(doc["text"])
        embeddings = embed_text_local(chunks)

        page_context = []
        for idx, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
            page_context.append({
                "chunk_text": chunk,
                "embedding": embedding,
                "chunk_index": idx
            })

        chunked_pages.append({
            "page_title": doc["title"],
            "page_context": page_context
        })

    return chunked_pages