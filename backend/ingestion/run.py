import argparse
import logging

from backend.config import INGESTED_DIRECTORY, RAW_ARTICLES_JSON, RAW_PDF_DIRECTORY
from backend.ingestion.loaders import load_html_from_json, load_pdfs
from backend.ingestion.processor import clean_documents, enrich_metadata, save_documents

logger = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--force",
        action="store_true",
        help="Re-ingest all sources, overwriting existing files",
    )
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(name)s %(levelname)s %(message)s",
    )

    all_docs = (
        load_pdfs(RAW_PDF_DIRECTORY, INGESTED_DIRECTORY, args.force)
        + load_html_from_json(RAW_ARTICLES_JSON, INGESTED_DIRECTORY, args.force)
    )
    logger.info("Total new docs to process: %d", len(all_docs))

    if not all_docs:
        logger.info("Nothing new to ingest. Use --force to re-ingest everything.")
        return

    processed = enrich_metadata(clean_documents(all_docs))
    save_documents(processed, INGESTED_DIRECTORY)
    logger.info("Ingestion complete")


if __name__ == "__main__":
    main()
