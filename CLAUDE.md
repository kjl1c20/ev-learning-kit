# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

EV Learning Kit is a RAG (Retrieval-Augmented Generation) system that answers questions about Electric Vehicles. It ingests EV articles/PDFs, chunks and embeds them using OpenAI, stores vectors in PostgreSQL (pgvector), and serves answers via a FastAPI endpoint backed by Claude (Anthropic). It also generates EV charge curves using an LLM guided by reference profiles stored in RDS.

## Environment Setup

Requires `.env` with:
- `OPENAI_API_KEY` — used for embeddings (`text-embedding-3-small`)
- `ANTHROPIC_API_KEY` — used for LLM responses (`claude-3-5-sonnet-latest`)
- `DB_SECRET_NAME` — AWS Secrets Manager secret name for RDS credentials
- `AWS_REGION` — defaults to `eu-west-2`

```bash
pip install -r requirements.txt
```

## Running the API

```bash
uvicorn backend.api.main:app --reload
```

Endpoints:
- `POST /api/v1/ask` — RAG Q&A, body `{"query": "...", "top_k": 5}`
- `POST /api/v1/generate-curve` — charge curve generation, body `{"vehicle_class": "sedan|suv|truck|van", "battery_capacity_kwh": 75, "vehicle_max_dc_kw": 150, "site_power_kw": 100}`

## Pipeline

Run from the repo root. The pipeline must be run once before the API works.

**All-in-one (recommended):**
```bash
python -m backend.run_full_pipeline           # incremental — only processes new sources
python -m backend.run_full_pipeline --force   # full rebuild from scratch
```

**Individual steps:**
```bash
python -m backend.ingestion.run       # fetch + clean + save docs (skips already-ingested)
python -m backend.chunking.run        # split docs into chunks
python -m backend.embeddings.run      # embed + upsert into PostgreSQL (skips existing IDs)
```

Both `ingestion.run` and `embeddings.run` accept `--force` to bypass incremental skip.

Test retrieval interactively:
```bash
python -m backend.rag.test_retrieval
```

## Architecture

All paths and constants are centralized in `backend/config.py`.

**Ingestion** (`backend/ingestion/`): `loaders.py` fetches PDFs via `pypdf` and HTML pages by scraping URLs listed in `data/raw/ev_articles.json`. Before fetching, it checks whether the output file already exists in `data/processed/ingested/` and skips if so. `processor.py` cleans text, enriches metadata with keyword-detected EV topics, and saves `Document` objects as JSON using stable filenames (`html_<url_hash>.json`, `pdf_<stem>_p<page>.json`).

**Chunking** (`backend/chunking/chunker.py`): Loads all ingested docs, splits with `RecursiveCharacterTextSplitter` (chunk_size=1200, overlap=200, markdown-aware separators), saves chunks to `data/processed/chunks/`.

**Embeddings** (`backend/embeddings/pipeline.py`): Queries the DB for existing chunk IDs (SHA256 of content) and skips those. Generates vectors via OpenAI for new chunks only, then upserts into the `embeddings` table in PostgreSQL via pgvector.

**RAG** (`backend/rag/`): `retrieval.py` embeds a query (OpenAI) and queries PostgreSQL for top-k chunks. `prompts.py` builds the grounded prompt. `generator.py` calls Claude. `pipeline.py` ties all three together.

**Curve Generation** (`backend/curve/`): `generator.py` fetches reference vehicle profiles from the `vehicle_profiles` RDS table via `profiles_repository.py`, retrieves relevant RAG chunks, then prompts Claude to output `CurveParameters`. `math.py` generates the native curve from those parameters and clips it to site power. `models.py` holds all Pydantic schemas. Supported vehicle classes: `sedan`, `suv`, `truck`, `van`.

**API** (`backend/api/`): FastAPI app in `main.py`. Routes defined in `routes.py` with Pydantic schemas in `schemas.py`.
