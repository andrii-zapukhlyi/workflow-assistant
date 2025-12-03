from langchain_qdrant import QdrantVectorStore
from langchain_core.vectorstores import VectorStoreRetriever
from langchain_huggingface import HuggingFaceEmbeddings
from backend.rag.confluence_client import get_available_titles, get_public_titles

def get_retriever(space_key: str, k: int = 2) -> VectorStoreRetriever:
    embedding = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

    vectordb = QdrantVectorStore.from_existing_collection(
        embedding=embedding,
        collection_name="confluence_docs",
        url="http://localhost:6333"
    )

    allowed_pages = [p["title"] for p in get_available_titles(space_key)]
    allowed_pages += [p["title"] for p in get_public_titles()]

    retriever = vectordb.as_retriever(
        search_kwargs={
            "k": k,
            "filter": {
                "must": [
                    {
                        "key": "metadata.page_title",
                        "match": {"any": allowed_pages}
                    }
                ]
            }
        }
    )
    return retriever