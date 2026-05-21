# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

EV Learning Kit is a RAG (Retrieval-Augmented Generation) system that answers questions about Electric Vehicles. It ingests EV articles/PDFs, chunks and embeds them using OpenAI, stores vectors in ChromaDB, and serves answers via a FastAPI endpoint backed by Claude (Anthropic).

## Environment Setup

Requires `.env` with:
- `OPENAI_API_KEY` — used for embeddings (`text-embedding-3-small`)
- `ANTHROPIC_API_KEY` — used for LLM responses (`claude-3-5-sonnet-latest`)

```bash
pip install -r requirements.txt
```

## Running the API

```bash
uvicorn backend.api.main:app --reload
```

Endpoint: `POST /api/v1/ask` with body `{"query": "...", "top_k": 5}`

## Pipeline Execution Order

Run from the repo root. The pipeline must be run once before the API works.

```bash
python -m backend.ingestion.run    # fetch + clean + save docs
python -m backend.chunking.run     # split docs into chunks
python -m backend.embeddings.run   # embed chunks + load into ChromaDB
```

Test retrieval interactively:
```bash
python -m backend.rag.test_retrieval
```

## Architecture

All paths and constants are centralized in `backend/config.py`.

**Ingestion** (`backend/ingestion/`): `loaders.py` fetches PDFs via `pypdf` and HTML pages by scraping URLs listed in `data/raw/ev_articles.json`. `processor.py` cleans text, enriches metadata with keyword-detected EV topics, and saves `Document` objects as JSON to `data/processed/ingested/`. `run.py` is the entry point.

**Chunking** (`backend/chunking/chunker.py`): Loads ingested docs, splits with `RecursiveCharacterTextSplitter` (chunk_size=1200, overlap=200, markdown-aware separators), and saves chunks to `data/processed/chunks/`.

**Embeddings** (`backend/embeddings/pipeline.py`): Generates vectors via OpenAI, saves them as JSON to `data/processed/embeddings/` (local cache), then upserts into a persistent ChromaDB collection (`ev_knowledge_base`) at `data/vectordb/`. The JSON cache allows re-indexing without re-calling OpenAI.

**RAG** (`backend/rag/`): `retrieval.py` embeds a query (OpenAI) and queries ChromaDB for top-k chunks using lazy initialization — the collection is not opened until the first query. `prompts.py` builds the grounded prompt. `generator.py` calls Claude. `pipeline.py` ties all three together and is what the API calls.

**API** (`backend/api/`): FastAPI app in `main.py`. Single route `POST /api/v1/ask` defined in `routes.py` with Pydantic schemas in `schemas.py`.
