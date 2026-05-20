import json
import logging
from pathlib import Path
from typing import List

import chromadb
from dotenv import load_dotenv
from langchain_core.documents import Document
from openai import OpenAI

from backend.config import (
    CHROMA_COLLECTION_NAME,
    CHUNKS_DIRECTORY,
    EMBEDDING_MODEL,
    EMBEDDINGS_DIRECTORY,
    PERSIST_DIRECTORY,
)

load_dotenv()

logger = logging.getLogger(__name__)

_openai_client = OpenAI()


def load_chunks(chunk_dir: str = CHUNKS_DIRECTORY) -> List[Document]:
    files = list(Path(chunk_dir).glob("*.json"))
    documents = []
    for file in files:
        with open(file, "r", encoding="utf-8") as f:
            data = json.load(f)
            documents.append(Document(page_content=data["content"], metadata=data["metadata"]))
    return documents


def generate_embeddings(documents: List[Document]) -> List[dict]:
    embedded = []
    for idx, doc in enumerate(documents):
        logger.info("Embedding chunk %d/%d", idx + 1, len(documents))
        response = _openai_client.embeddings.create(model=EMBEDDING_MODEL, input=doc.page_content)
        embedded.append({
            "id": f"chunk_{idx}",
            "content": doc.page_content,
            "embedding": response.data[0].embedding,
            "metadata": doc.metadata,
        })
    return embedded


def save_embeddings(embedded: List[dict], output_dir: str = EMBEDDINGS_DIRECTORY) -> None:
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    for chunk in embedded:
        with open(Path(output_dir) / f"{chunk['id']}.json", "w", encoding="utf-8") as f:
            json.dump(chunk, f)
    logger.info("Saved %d embeddings to %s", len(embedded), output_dir)


def store_in_chroma(embedded: List[dict]) -> None:
    client = chromadb.PersistentClient(path=PERSIST_DIRECTORY)
    collection = client.get_or_create_collection(name=CHROMA_COLLECTION_NAME)
    collection.upsert(
        ids=[c["id"] for c in embedded],
        embeddings=[c["embedding"] for c in embedded],
        documents=[c["content"] for c in embedded],
        metadatas=[c["metadata"] for c in embedded],
    )
    logger.info(
        "Stored %d embeddings in ChromaDB collection '%s'",
        len(embedded),
        CHROMA_COLLECTION_NAME,
    )
