import logging

from backend.rag.generator import generate_response
from backend.rag.prompts import SYSTEM_PROMPT, build_prompt
from backend.rag.retrieval import retrieve_relevant_chunks

logger = logging.getLogger(__name__)


def run_rag_pipeline(query: str, top_k: int = 5) -> dict:
    """
    End-to-end RAG pipeline: retrieve → prompt → generate.
    Returns dict with 'answer' (str) and 'sources' (list of metadata dicts).
    """
    logger.info("Query: %s (top_k=%d)", query, top_k)

    chunks = retrieve_relevant_chunks(query, top_k=top_k)
    logger.info("Retrieved %d chunks", len(chunks))

    answer = generate_response(SYSTEM_PROMPT, build_prompt(query, chunks))

    return {
        "answer": answer,
        "sources": [chunk["metadata"] for chunk in chunks],
    }
