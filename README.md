# EV Learning Kit

EV Learning Kit is a RAG (Retrieval-Augmented Generation) application that answers questions about Electric Vehicles and generates realistic DC charge curves for any vehicle class. It combines a knowledge base built from EV articles and technical reports with an LLM-driven curve engine backed by real reference profiles.

## Project Overview

The system has two core capabilities:

- **EV Q&A** — Ask any question about EV charging, battery chemistry, or powertrain technology. The system retrieves relevant knowledge chunks and generates a grounded answer via Claude.
- **Charge Curve Generator** — Provide a vehicle class, battery size, and max DC power. The system produces a native charge curve (what the vehicle can accept) and a delivered curve (clipped to your site's charger capacity), along with charging metrics and reasoning.

## Components

### RAG Pipeline

Built on OpenAI embeddings (`text-embedding-3-small`) stored in PostgreSQL via pgvector. Source material is ingested from URLs listed in `data/raw/ev_articles.json` and PDFs in `data/raw/pdfs/`. The ingestion pipeline is incremental — only new sources are fetched and embedded on each run.

### Charge Curve Engine

The curve engine queries a `vehicle_profiles` table in RDS for reference vehicles of the same class, retrieves relevant RAG context, then prompts Claude to output curve parameters (peak power, taper start/end, tail power, chemistry, voltage architecture). A deterministic math layer converts those parameters into a smooth SOC vs power curve, which is then clipped to the site charger limit.

Supported vehicle classes: **sedan**, **suv**, **truck**, **van**.

### API

FastAPI backend with two routes:

| Endpoint | Method | Description |
|---|---|---|
| `/api/v1/ask` | POST | RAG-based EV Q&A |
| `/api/v1/generate-curve` | POST | Charge curve generation |

## Project Workflow

```
ev_articles.json                data/raw/pdfs/
       │                               │
       ▼                               ▼
  loaders.py  ──────────────────► processor.py
  (fetch HTML)                   (clean + enrich)
                                        │
                                        ▼
                              data/processed/ingested/
                                        │
                                        ▼
                                   chunker.py
                                (split into chunks)
                                        │
                                        ▼
                              data/processed/chunks/
                                        │
                                        ▼
                               embeddings/pipeline.py
                              (OpenAI → pgvector RDS)
                                        │
                                        ▼
                               FastAPI  /api/v1/ask
                               FastAPI  /api/v1/generate-curve
```

## Installation

**Requirements**

- Python 3.11+
- AWS credentials with access to Secrets Manager (for RDS connection)
- OpenAI API key
- Anthropic API key

**Setup**

```bash
pip install -r requirements.txt
```

Create a `.env` file in the repo root:

```
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
DB_SECRET_NAME=your/secret/name
AWS_REGION=eu-west-2
```

## Usage

### Running the ingestion pipeline

Run once before starting the API. Subsequent runs only process new sources.

```bash
python -m backend.run_full_pipeline
```

To force a full rebuild from scratch:

```bash
python -m backend.run_full_pipeline --force
```

Individual steps can also be run separately:

```bash
python -m backend.ingestion.run     # fetch and save new docs only
python -m backend.chunking.run      # rechunk all ingested docs
python -m backend.embeddings.run    # embed and upsert new chunks only
```

### Starting the API

```bash
uvicorn backend.api.main:app --reload
```

### Example requests

**Ask a question:**

```bash
curl -X POST http://localhost:8000/api/v1/ask \
  -H "Content-Type: application/json" \
  -d '{"query": "What is the difference between NMC and LFP batteries?", "top_k": 5}'
```

**Generate a charge curve:**

```bash
curl -X POST http://localhost:8000/api/v1/generate-curve \
  -H "Content-Type: application/json" \
  -d '{
    "vehicle_class": "van",
    "battery_capacity_kwh": 75,
    "vehicle_max_dc_kw": 100,
    "site_power_kw": 50
  }'
```

### Testing retrieval

```bash
python -m backend.rag.test_retrieval
```

## Frontend

The frontend is a Next.js app located in `frontend/`.

**Install dependencies:**

```bash
cd frontend
npm install
```

**Start the dev server:**

```bash
npm run dev
```

The app will be available at `http://localhost:3000`. It expects the FastAPI backend running at `http://localhost:8000` by default.

To point to a different backend, create a `frontend/.env.local` file:

```
NEXT_PUBLIC_API_URL=http://your-backend-url
```

**Build for production:**

```bash
npm run build
npm run start
```

## Knowledge Base Sources

The RAG knowledge base is built from the following publicly available resources:

- [EVKX.net](https://evkx.net)
- [Geotab](https://www.geotab.com/blog/)
- TNO R11236 *Living Lab Heavy Duty Laadpleinen* (2025) — real-world HD truck charging data

These sources are used for personal and educational purposes only.

## License

MIT License — Copyright (c) 2026 kjl1c20

You are free to use, copy, modify, and distribute this project, provided the original copyright notice is retained.
