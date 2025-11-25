from typing import Any
from langchain_chroma.vectorstores import Chroma
from numpy import ndarray
from embedder import chunk_and_embed_documents
from confluence_client import get_all_pages
import os

def build_vectorstore(chunks: list[str], embeddings: ndarray, metadata: list[dict[str, Any]]) -> Chroma:
    chroma_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "chroma_db")
    vectordb = Chroma(
        collection_name="confluence_docs",
        persist_directory=chroma_path
    )

    vectordb.add_texts(
        texts=chunks,
        metadatas=metadata,
        embeddings=embeddings
    )

    return vectordb

def main():
    pages = get_all_pages()
    chunks, embeddings, metadata = chunk_and_embed_documents(pages)
    vectordb = build_vectorstore(chunks, embeddings, metadata)

if __name__ == "__main__":
    main()