import json
import logging
import os

from dotenv import load_dotenv
from openai import OpenAI
from pgvector.psycopg2 import register_vector

from backend.config import DB_SECRET_NAME, EMBEDDING_MODEL
from backend.utils import get_db_connection

load_dotenv()

logger = logging.getLogger(__name__)

_openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
_conn = None


def _get_conn():
    global _conn
    if _conn is None or _conn.closed:
        _conn = get_db_connection(DB_SECRET_NAME)
        register_vector(_conn)
    return _conn


def generate_query_embedding(query: str) -> list[float]:
    response = _openai_client.embeddings.create(model=EMBEDDING_MODEL, input=query)
    return response.data[0].embedding


def retrieve_relevant_chunks(query: str, top_k: int = 5) -> list[dict]:
    embedding = generate_query_embedding(query)

    with _get_conn().cursor() as cur:
        cur.execute(
            """
            SELECT content, metadata
            FROM embeddings
            ORDER BY embedding <=> %s
            LIMIT %s
            """,
            (embedding, top_k),
        )
        rows = cur.fetchall()

    return [
        {"document": content, "metadata": json.loads(metadata)}
        for content, metadata in rows
    ]
