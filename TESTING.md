# QA RAG Assistant — Test Plan

## Quick run (no embedding model download)

```powershell
cd qa-rag-assistant
.\.venv\Scripts\pytest.exe -m "not slow and not groq" -v
```

## Full automated suite (includes retrieval RAG eval)

```powershell
.\.venv\Scripts\pytest.exe -m "not groq" -v
```

## RAG evaluation (retrieval only — free, no Groq)

```powershell
.\.venv\Scripts\python.exe -m eval.run_eval
```

Metrics reported:
- **Hit@k** — did retrieval find relevant chunks?
- **Keyword recall@k** — % of expected terms found in top-k chunks
- **MRR** — mean reciprocal rank of first relevant chunk
- **Negative retrieval** — out-of-scope queries must not pull hallucinated topics

## RAG evaluation (with Groq generation — uses free-tier API)

```powershell
.\.venv\Scripts\python.exe -m eval.run_eval --with-llm
```

Additional metrics:
- **Faithfulness** — % of answer tokens grounded in retrieved context
- **Insufficient context** — negative queries should not invent features
- **Forbidden terms** — payment/2FA terms must not appear when absent from doc

## Optional live Groq pytest

```powershell
.\.venv\Scripts\pytest.exe -m groq -v
```

## Manual QA checklist

| # | Test | Pass criteria |
|---|------|---------------|
| 1 | Upload `.txt` | Indexed success message, file in sidebar |
| 2 | Upload `.pdf` | Same as above |
| 3 | Generate functional matrix | 7+ column table, TC-001… IDs |
| 4 | Source expander | Chunks match doc content, relevance scores shown |
| 5 | Download CSV | Opens in Excel with correct columns |
| 6 | Browser refresh | Persisted index reloads (if enabled) |
| 7 | Clear index | Sidebar list empty, re-upload works |
| 8 | Custom inquiry | Empty → warning; valid query → output |
| 9 | Hallucination check | Ask about feature NOT in doc → "Insufficient context" |
| 10 | Change file content, same name | Re-indexes (content hash change) |

## Automated test coverage

| Module | What it tests |
|--------|---------------|
| `test_core.py` | Hash cache, API key, errors, table parser, metadata |
| `test_ingestion.py` | TXT loading, chunking, index records, vectorstore |
| `test_rag_chain.py` | Retrieval chain with mocked LLM (no Groq cost) |
| `test_rag_eval.py` | **RAG metrics + benchmark pass thresholds** |
| `eval/run_eval.py` | **CLI RAG evaluation report** |

## Eval dataset

Ground-truth cases live in `eval/rag_eval_set.json` (7 retrieval + 2 generation cases against `minimal_prd.txt`). Extend this file as you add PRD fixtures.
