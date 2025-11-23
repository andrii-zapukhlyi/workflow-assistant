from langchain_chroma import Chroma
from langchain_core.vectorstores import VectorStoreRetriever
from rag.confluence_client import get_available_titles, get_public_titles

def get_retriever(space_key: str, k: int = 2) -> VectorStoreRetriever:
    vectordb = Chroma(
        collection_name="confluence_docs",
        persist_directory="chroma_db"
    )

    allowed_pages = [page["title"] for page in get_available_titles(space_key)]
    allowed_pages += [page["title"] for page in get_public_titles()]

    retriever = vectordb.as_retriever(
        search_kwargs={
            "k": k,
            "filter": {"page_title": {"$in": allowed_pages}},
        }
    )
    return retriever