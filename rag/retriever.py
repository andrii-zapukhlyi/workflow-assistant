from langchain_chroma import Chroma
from rag.confluence_client import get_available_titles, get_public_titles

def metadata_filtering(results, space_key):
    available_pages = [page["title"] for page in get_available_titles(space_key)] + [page["title"] for page in get_public_titles()]
    filtered_docs = [doc for doc in results if doc.metadata.get("page_title") in available_pages]
    return filtered_docs

def retrieve_similar_documents(query, space_key, k=5):
    vectordb = Chroma(
        collection_name="confluence_docs",
        persist_directory="chroma_db"
    )
    results = vectordb.similarity_search(query, k=k)
    print([doc.metadata for doc in results])
    filtered_results = metadata_filtering(results, space_key)
    print([doc.metadata for doc in filtered_results])
    return filtered_results