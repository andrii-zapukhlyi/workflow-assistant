from typing import Any
from langchain_chroma.vectorstores import Chroma
from numpy import ndarray
from embedder import chunk_and_embed_documents
from confluence_client import get_all_pages

def build_vectorstore(chunks: list[str], embeddings: ndarray, metadata: list[dict[str, Any]]) -> Chroma:
    vectordb = Chroma(
        collection_name="confluence_docs",
        persist_directory="../chroma_db"
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