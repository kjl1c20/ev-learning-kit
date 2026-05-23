import logging
from typing import List

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

import backend.storage as storage

logger = logging.getLogger(__name__)


def load_documents(input_dir: str) -> List[Document]:
    keys = storage.list_keys(input_dir)
    logger.info("Found %d ingested documents", len(keys))
    documents = []
    for key in keys:
        data = storage.read_json(key)
        documents.append(Document(page_content=data["page_content"], metadata=data["metadata"]))
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
    for idx, chunk in enumerate(chunks):
        storage.write_json(
            f"{output_dir}/chunk_{idx}.json",
            {"content": chunk.page_content, "metadata": chunk.metadata},
        )
    logger.info("Saved %d chunks to %s", len(chunks), output_dir)
