# RAG for Financial Reports

A Retrieval-Augmented Generation (RAG) system for semantic search and question-answering over financial annual reports.

## Architecture

```
PDF Reports → Parser → Chunker → Embedder → Qdrant (Vector DB)
                                                    ↓
User Query → Query Analysis → Retriever → LLM → Answer
```

### Modules

| Module | Description |
|--------|-------------|
| `config.py` | API keys, Qdrant host/port, collection name |
| `parser.py` | Extracts text from PDFs using PyMuPDF |
| `chunker.py` | Splits pages into semantic sections using uppercase-line detection |
| `entities.py` | Regex-based extraction of revenue, operating margin, and ROE |
| `embedder.py` | Generates OpenAI embeddings and upserts vectors into Qdrant |
| `retriever.py` | Semantic similarity search with optional company/year filters |
| `llm.py` | Context formatting and GPT-powered answer generation |
| `ingest.py` | Orchestrates the full ingestion pipeline |
| `query_pipeline.py` | End-to-end query processing: analyze → retrieve → generate |

## Setup

### Prerequisites

- Python 3.10+
- An OpenAI API key

### Install dependencies

```bash
pip install openai qdrant-client pymupdf
```

### Configure

Set your OpenAI API key in `config.py`:

```python
OPENAI_API_KEY = "sk-..."
```

## Usage

### 1. Ingest reports

Place PDF annual reports in the `fin_report_analysis/` directory, then run:

```bash
python ingest.py
```

This parses the PDFs, chunks the text, extracts entities, generates embeddings, and stores everything in a local Qdrant database (`qdrant_data/`).

### 2. Query

```python
from query_pipeline import run_query

answer = run_query("What was Infosys revenue in 2024?")
print(answer)
```

The pipeline embeds the query, retrieves the top-6 most relevant chunks (with optional company/year filtering), and generates an answer using GPT with citations to source pages.

## Key Details

- **Embeddings**: OpenAI `text-embedding-3-small` (1536 dimensions)
- **Vector DB**: Qdrant (local SQLite-backed, cosine similarity)
- **LLM**: GPT-4.1-mini (temperature=0 for deterministic answers)
- **Chunking**: Section-based splitting using uppercase line detection as a heuristic delimiter
- **Retrieval filters**: Automatically extracts company name and fiscal year from the query to narrow search
