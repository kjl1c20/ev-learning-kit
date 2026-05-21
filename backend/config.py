import os

from dotenv import load_dotenv

load_dotenv()

EMBEDDING_MODEL = "text-embedding-3-small"

DB_SECRET_NAME = os.getenv("DB_SECRET_NAME", "")

RAW_PDF_DIRECTORY = "data/raw/pdfs"
RAW_ARTICLES_JSON = "data/raw/ev_articles.json"
INGESTED_DIRECTORY = "data/processed/ingested"
CHUNKS_DIRECTORY = "data/processed/chunks"