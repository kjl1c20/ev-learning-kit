import logging

from backend.embeddings.pipeline import generate_embeddings, load_chunks, store_in_postgres

logger = logging.getLogger(__name__)


def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(name)s %(levelname)s %(message)s",
    )

    chunks = load_chunks()
    logger.info("Loaded %d chunks", len(chunks))

    embedded = generate_embeddings(chunks)
    store_in_postgres(embedded)
    logger.info("Embedding pipeline complete")


if __name__ == "__main__":
    main()
