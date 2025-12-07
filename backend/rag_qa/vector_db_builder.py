from langchain_qdrant import QdrantVectorStore
from langchain_huggingface.embeddings import HuggingFaceEndpointEmbeddings
from langchain_core.documents import Document
from chunker import chunk_and_prepare_metadata
from confluence_client import get_all_pages
from config.settings import HF_API_TOKEN
from qdrant_client import QdrantClient

def delete_old_vector_db(url: str, collection: str) -> None:
    client = QdrantClient(url=url)
    if client.collection_exists(collection):
        client.delete_collection(collection_name=collection)

def build_vector_db(url: str, collection: str) -> None:
    embedding = HuggingFaceEndpointEmbeddings(
        model="sentence-transformers/all-MiniLM-L6-v2",
        task="feature-extraction",
        huggingfacehub_api_token=HF_API_TOKEN,
    )

    documents = get_all_pages()
    chunks, metadata = chunk_and_prepare_metadata(documents)

    docs = [Document(page_content=chunk, metadata=meta) for chunk, meta in zip(chunks, metadata)]

    QdrantVectorStore.from_documents(
        docs,
        embedding=embedding,
        url=url,
        collection_name=collection,
    )

def main() -> None:
    collection_name = "confluence_docs"
    qdrant_url = "http://localhost:6333"
    delete_old_vector_db(url=qdrant_url, collection=collection_name)
    build_vector_db(url=qdrant_url, collection=collection_name)

if __name__ == "__main__":
    main()