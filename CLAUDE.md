# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

EV Learning Kit is a RAG (Retrieval-Augmented Generation) pipeline that answers questions about Electric Vehicles. It ingests EV articles/PDFs, chunks and embeds them using OpenAI, stores vectors in ChromaDB, and answers user queries via Claude (Anthropic).

## Environment Setup

Requires `.env` with:
- `OPENAI_API_KEY` — used for embeddings (`text-embedding-3-small`)
- `ANTHROPIC_API_KEY` — used for LLM responses (`claude-3-5-sonnet-latest`)

Install dependencies:
```bash
pip install -r requirements.txt
```

## Pipeline Execution Order

Run each stage from the repo root (modules use relative paths like `data/...`):

```bash
# 1. Ingest raw documents (PDFs + HTML articles)
python -m backend.ingestion.run_ingestion

# 2. Chunk ingested documents
python -m backend.chunking.run_chunking

# 3. Generate and save embeddings (OpenAI)
python -m backend.embeddings.embedding_pipeline

# 4. Load embeddings into ChromaDB
python -m backend.embeddings.chroma_store

# 5. Interactive retrieval test
python -m backend.rag.test_retrieval
```

Raw data sources: `data/raw/ev_articles.json` (URL list for HTML scraping) and `data/raw/pdfs/` (PDF files).

## Architecture

The pipeline has four sequential stages, each with its own `backend/` subpackage:

**Ingestion** (`backend/ingestion/`): Loads PDFs via `pypdf` and HTML pages by fetching URLs listed in `ev_articles.json` via BeautifulSoup. Cleans text, enriches metadata, and saves `Document` objects as JSON to `data/processed/ingested/`.

**Chunking** (`backend/chunking/`): Loads ingested docs, splits with `RecursiveCharacterTextSplitter` (chunk_size=1200, overlap=200, markdown-aware separators), and saves chunks as JSON to `data/processed/chunks/`.

**Embeddings** (`backend/embeddings/`): Two steps — `embedding_pipeline.py` generates vectors via OpenAI and saves to `data/processed/embeddings/`; `chroma_store.py` reads those files and upserts into a persistent ChromaDB collection (`ev_knowledge_base`) at `data/vectordb/`. Config is centralized in `config.py`.

**RAG** (`backend/rag/`): `retrieval.py` embeds a user query (OpenAI) and queries ChromaDB for top-k chunks. `prompts.py` builds the grounded prompt from retrieved chunks. `claude_client.py` sends the composed prompt to Claude and returns the answer. `rag_pipeline.py` ties retrieval + generation together; `test_retrieval.py` provides an interactive CLI for testing retrieval only.

## Key Design Decisions

- Embeddings are stored twice: as flat JSON files (`data/processed/embeddings/`) and inside ChromaDB. The JSON files act as a local cache so embeddings can be re-indexed without re-calling OpenAI.
- All scripts must be run as modules (`python -m backend.X.Y`) from the repo root because imports use the `backend.*` package namespace without any installed package or `sys.path` manipulation.
- The `architecture.txt` file describes a planned future structure (frontend, API layer, evaluation, monitoring, Docker) that is not yet implemented.
