import json
import logging
import re
from pathlib import Path
from typing import List

from langchain_core.documents import Document

logger = logging.getLogger(__name__)


def clean_documents(documents: List[Document]) -> List[Document]:
    return [
        Document(page_content=_clean_text(doc.page_content), metadata=doc.metadata)
        for doc in documents
    ]


def _clean_text(text: str) -> str:
    text = re.sub(r"\n+", "\n", text)
    text = re.sub(r"[ \t]+", " ", text)
    text = text.replace("\xa0", " ")
    text = re.sub(r"\s+([.,;:!?])", r"\1", text)
    return text.strip()


def enrich_metadata(documents: List[Document]) -> List[Document]:
    enriched = []
    for doc in documents:
        text = doc.page_content.lower()
        topics = []
        if "charge curve" in text:
            topics.append("charge_curve")
        if "battery management system" in text or "bms" in text:
            topics.append("bms")
        if "thermal" in text:
            topics.append("thermal_management")
        if "lfp" in text:
            topics.append("lfp")
        if "nmc" in text:
            topics.append("nmc")
        enriched.append(
            Document(
                page_content=doc.page_content,
                metadata={**doc.metadata, "detected_topics": topics},
            )
        )
    return enriched


def save_documents(documents: List[Document], output_dir: str) -> None:
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    for idx, doc in enumerate(documents):
        with open(output_path / f"doc_{idx}.json", "w", encoding="utf-8") as f:
            json.dump(
                {"page_content": doc.page_content, "metadata": doc.metadata},
                f,
                ensure_ascii=False,
                indent=2,
            )

    logger.info("Saved %d documents to %s", len(documents), output_dir)
