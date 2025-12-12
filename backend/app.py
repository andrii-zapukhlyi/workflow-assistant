import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api import auth_router, chat_router
from rag_qa.vector_db_builder import build_vector_db
from qdrant_client import QdrantClient

qdrant_url = os.environ.get("QDRANT_URL", "http://localhost:6333")
collection_name = "confluence_docs"

@asynccontextmanager
async def lifespan(app: FastAPI):
    client = QdrantClient(url=qdrant_url)
    if not client.collection_exists(collection_name):
        build_vector_db(url=qdrant_url, collection=collection_name)
    yield

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router.router, prefix="/auth")
app.include_router(chat_router.router, prefix="/chat")