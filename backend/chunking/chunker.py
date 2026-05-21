import json
import logging
from pathlib import Path
from typing import List

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

logger = logging.getLogger(__name__)


def load_documents(input_dir: str) -> List[Document]:
    json_files = list(Path(input_dir).glob("*.json"))
    logger.info("Found %d ingested documents", len(json_files))

    documents = []
    for file_path in json_files:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            documents.append(
                Document(page_content=data["page_content"], metadata=data["metadata"])
            )
    return documents


def chunk_documents(documents: List[Document]) -> List[Document]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1200,
        chunk_overlap=200,
        separators=["\n## ", "\n### ", "\n\n", "\n", ". ", " "],
    )

    chunks = []
    for doc in documents:
        for idx, text in enumerate(splitter.split_text(doc.page_content)):
            chunks.append(
                Document(
                    page_content=text,
                    metadata={**doc.metadata, "chunk_id": idx, "chunk_size": len(text)},
                )
            )
    return chunks


def save_chunks(chunks: List[Document], output_dir: str) -> None:
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    for idx, chunk in enumerate(chunks):
        with open(Path(output_dir) / f"chunk_{idx}.json", "w", encoding="utf-8") as f:
            json.dump({"content": chunk.page_content, "metadata": chunk.metadata}, f, indent=2)

    logger.info("Saved %d chunks to %s", len(chunks), output_dir)
