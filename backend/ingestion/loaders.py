import hashlib
import json
import logging
from pathlib import Path
from typing import List

import requests
from bs4 import BeautifulSoup
from langchain_community.document_loaders import PyPDFLoader
from langchain_core.documents import Document

logger = logging.getLogger(__name__)


def _html_filename(url: str) -> str:
    return f"html_{hashlib.md5(url.encode()).hexdigest()[:12]}.json"


def _pdf_exists(ingested_dir: Path, stem: str) -> bool:
    return any(ingested_dir.glob(f"pdf_{stem}_p*.json"))


def load_pdfs(pdf_directory: str, ingested_dir: str = "", force: bool = False) -> List[Document]:
    pdf_path = Path(pdf_directory)
    if not pdf_path.exists():
        raise FileNotFoundError(f"Directory not found: {pdf_directory}")

    ingested_path = Path(ingested_dir) if ingested_dir else None
    documents = []
    pdf_files = list(pdf_path.glob("*.pdf"))
    logger.info("Found %d PDF files", len(pdf_files))

    for pdf_file in pdf_files:
        if not force and ingested_path and _pdf_exists(ingested_path, pdf_file.stem):
            logger.info("Skipping (already ingested): %s", pdf_file.name)
            continue
        try:
            pages = PyPDFLoader(str(pdf_file)).load()
            for page in pages:
                page.metadata["source_type"] = "pdf"
                page.metadata["file_name"] = pdf_file.name
            documents.extend(pages)
            logger.info("Loaded: %s (%d pages)", pdf_file.name, len(pages))
        except Exception as e:
            logger.warning("Error loading %s: %s", pdf_file.name, e)

    return documents


def load_html_from_json(json_path: str, ingested_dir: str = "", force: bool = False) -> List[Document]:
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    ingested_path = Path(ingested_dir) if ingested_dir else None
    metadata_map = {item["url"]: item for item in data}
    documents = []

    for item in data:
        url = item["url"]

        if not force and ingested_path and (ingested_path / _html_filename(url)).exists():
            logger.info("Skipping (already ingested): %s", url)
            continue

        try:
            response = requests.get(
                url,
                timeout=10,
                headers={"User-Agent": "Mozilla/5.0 (compatible; EVLearningKit/1.0)"},
            )
            response.raise_for_status()

            soup = BeautifulSoup(response.text, "html.parser")
            for tag in soup(["script", "style", "nav", "footer", "header"]):
                tag.decompose()

            title = soup.title.string if soup.title else "Untitled"
            cleaned_text = "\n".join(
                line.strip()
                for line in soup.get_text(separator="\n").splitlines()
                if line.strip()
            )

            meta = metadata_map[url]
            documents.append(Document(
                page_content=cleaned_text,
                metadata={
                    "url": url,
                    "title": title,
                    "source_type": "html",
                    "domain": meta.get("domain"),
                },
            ))
            logger.info("Loaded: %s", url)

        except Exception as e:
            logger.warning("Failed to load %s: %s", url, e)

    return documents
