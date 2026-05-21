import argparse
import logging

from backend.chunking.chunker import chunk_documents, load_documents, save_chunks
from backend.config import CHUNKS_DIRECTORY, INGESTED_DIRECTORY, RAW_ARTICLES_JSON, RAW_PDF_DIRECTORY
from backend.embeddings.pipeline import generate_embeddings, load_chunks, store_in_postgres
from backend.ingestion.loaders import load_html_from_json, load_pdfs
from backend.ingestion.processor import clean_documents, enrich_metadata, save_documents

logger = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser(description="Run the full EV ingestion pipeline end-to-end.")
    parser.add_argument("--force", action="store_true", help="Re-ingest and re-embed everything from scratch")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

    # 1. Ingestion
    logger.info("=== Step 1/3: Ingestion ===")
    raw_docs = (
        load_pdfs(RAW_PDF_DIRECTORY, INGESTED_DIRECTORY, args.force)
        + load_html_from_json(RAW_ARTICLES_JSON, INGESTED_DIRECTORY, args.force)
    )
    if raw_docs:
        save_documents(enrich_metadata(clean_documents(raw_docs)), INGESTED_DIRECTORY)
    else:
        logger.info("Nothing new to ingest")

    # 2. Chunking
    logger.info("=== Step 2/3: Chunking ===")
    documents = load_documents(INGESTED_DIRECTORY)
    save_chunks(chunk_documents(documents), CHUNKS_DIRECTORY)

    # 3. Embeddings
    logger.info("=== Step 3/3: Embeddings ===")
    store_in_postgres(generate_embeddings(load_chunks(), force=args.force))

    logger.info("=== Pipeline complete ===")


if __name__ == "__main__":
    main()
