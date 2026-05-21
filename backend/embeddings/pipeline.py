import hashlib
import json
import logging
from pathlib import Path
from typing import List

from dotenv import load_dotenv
from langchain_core.documents import Document
from openai import OpenAI
from pgvector.psycopg2 import register_vector

from backend.config import (
    CHUNKS_DIRECTORY,
    DB_SECRET_NAME,
    EMBEDDING_MODEL,
)
from backend.utils import get_db_connection

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


def _chunk_id(content: str) -> str:
    return hashlib.sha256(content.encode()).hexdigest()[:16]


def generate_embeddings(documents: List[Document]) -> List[dict]:
    embedded = []
    for idx, doc in enumerate(documents):
        logger.info("Embedding chunk %d/%d", idx + 1, len(documents))
        response = _openai_client.embeddings.create(model=EMBEDDING_MODEL, input=doc.page_content)
        embedded.append({
            "id": _chunk_id(doc.page_content),
            "content": doc.page_content,
            "embedding": response.data[0].embedding,
            "metadata": doc.metadata,
        })
    return embedded


def store_in_postgres(embedded: List[dict]) -> None:
    conn = get_db_connection(DB_SECRET_NAME)
    register_vector(conn)

    with conn.cursor() as cur:
        for chunk in embedded:
            cur.execute(
                """
                INSERT INTO embeddings (id, content, embedding, metadata)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (id) DO UPDATE
                SET content = EXCLUDED.content,
                    embedding = EXCLUDED.embedding,
                    metadata = EXCLUDED.metadata
                """,
                (chunk["id"], chunk["content"], chunk["embedding"], json.dumps(chunk["metadata"])),
            )

    conn.commit()
    conn.close()
    logger.info("Stored %d embeddings in PostgreSQL", len(embedded))
