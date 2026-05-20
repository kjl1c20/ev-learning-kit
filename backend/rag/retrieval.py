import logging
import os

import chromadb
from dotenv import load_dotenv
from openai import OpenAI

from backend.config import CHROMA_COLLECTION_NAME, EMBEDDING_MODEL, PERSIST_DIRECTORY

load_dotenv()

logger = logging.getLogger(__name__)

_openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
_collection = None


def _get_collection():
    global _collection
    if _collection is None:
        _collection = chromadb.PersistentClient(path=PERSIST_DIRECTORY).get_collection(
            name=CHROMA_COLLECTION_NAME
        )
    return _collection


def generate_query_embedding(query: str) -> list[float]:
    response = _openai_client.embeddings.create(model=EMBEDDING_MODEL, input=query)
    return response.data[0].embedding


def retrieve_relevant_chunks(query: str, top_k: int = 5) -> list[dict]:
    embedding = generate_query_embedding(query)
    results = _get_collection().query(query_embeddings=[embedding], n_results=top_k)
    return [
        {
            "document": results["documents"][0][i],
            "metadata": results["metadatas"][0][i],
        }
        for i in range(len(results["documents"][0]))
    ]
