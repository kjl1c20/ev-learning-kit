import logging

from backend.config import INGESTED_DIRECTORY, RAW_ARTICLES_JSON, RAW_PDF_DIRECTORY
from backend.ingestion.loaders import load_html_from_json, load_pdfs
from backend.ingestion.processor import clean_documents, enrich_metadata, save_documents

logger = logging.getLogger(__name__)


def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(name)s %(levelname)s %(message)s",
    )

    all_docs = load_pdfs(RAW_PDF_DIRECTORY) + load_html_from_json(RAW_ARTICLES_JSON)
    logger.info("Total raw docs: %d", len(all_docs))

    processed = enrich_metadata(clean_documents(all_docs))
    save_documents(processed, INGESTED_DIRECTORY)
    logger.info("Ingestion complete")


if __name__ == "__main__":
    main()
