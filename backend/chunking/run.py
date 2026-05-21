import logging

from backend.config import CHUNKS_DIRECTORY, INGESTED_DIRECTORY
from backend.chunking.chunker import chunk_documents, load_documents, save_chunks

logger = logging.getLogger(__name__)


def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(name)s %(levelname)s %(message)s",
    )

    documents = load_documents(INGESTED_DIRECTORY)
    logger.info("Loaded %d documents", len(documents))

    chunks = chunk_documents(documents)
    logger.info("Generated %d chunks", len(chunks))

    save_chunks(chunks, CHUNKS_DIRECTORY)


if __name__ == "__main__":
    main()
