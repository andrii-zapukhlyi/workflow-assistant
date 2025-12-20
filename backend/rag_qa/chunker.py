import re


def chunk_text(text: str) -> list[str]:
    chunks = re.split(r"(?=\n## )", text)
    return [chunk.strip() for chunk in chunks if chunk.strip()]


def chunk_and_prepare_metadata(documents: list[dict[str, str]]):
    chunks = []
    metadata = []

    for doc in documents:
        chunked_text = chunk_text(doc["text"])

        for idx, chunk in enumerate(chunked_text):
            chunks.append(chunk)
            metadata.append(
                {
                    "page_title": doc["title"],
                    "page_link": doc["link"],
                    "chunk_index": idx,
                    "total_chunks": len(chunked_text),
                }
            )

    return chunks, metadata
