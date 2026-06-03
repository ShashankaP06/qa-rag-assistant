# QA RAG Assistant

[![CI](https://github.com/ShashankaP06/qa-rag-assistant/actions/workflows/ci.yml/badge.svg)](https://github.com/ShashankaP06/qa-rag-assistant/actions/workflows/ci.yml)
[![Live Demo](https://img.shields.io/badge/Live%20Demo-Streamlit-FF4B4B?logo=streamlit&logoColor=white)](https://app-rag-assistant-sysvsxop8pfbhj5xt2zgp3.streamlit.app)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.11%2B-blue.svg)](https://www.python.org/)

Evidence-based **QA test suite generator** powered by **local RAG** (free-tier friendly).

Upload requirements (`.txt`, `.pdf`) → retrieve relevant context → generate structured test matrices via **Groq LLM** — with full **source traceability**.

**[Live demo](https://app-rag-assistant-sysvsxop8pfbhj5xt2zgp3.streamlit.app)** · **[Repository](https://github.com/ShashankaP06/qa-rag-assistant)**

---

## Demo

![QA RAG Assistant — upload, generate, and source-backed test cases](docs/images/app-overview.svg)

| Tab | What to show |
|-----|----------------|
| **Application** | Upload a PRD → **Generate Test Suite** → expand **Retrieved Source Chunks** |
| **Documentation** | System architecture diagram, 7-stage workflow, tech stack & quality panels |

> Replace `docs/images/app-overview.svg` with a PNG/GIF screenshot from your live demo for an even sharper README.

---

## Features

- Local embeddings (`all-MiniLM-L6-v2`) — no embedding API cost
- In-memory / disk-persisted Chroma vector store
- Quick actions: functional tests, boundary/edge cases, custom inquiry
- Source chunk transparency with similarity scores
- Export to Markdown, CSV, Jira, TestRail, Azure DevOps
- Follow-up chat for iterative test design
- RAG evaluation benchmark (`eval/run_eval.py`)
- Automated CI via GitHub Actions
- In-app **Documentation** tab (architecture + workflow)

---

## Quick start (local)

### 1. Clone

```bash
git clone https://github.com/ShashankaP06/qa-rag-assistant.git
cd qa-rag-assistant
```

### 2. Virtual environment

```powershell
# Windows
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements-dev.txt
```

```bash
# macOS / Linux
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
```

> **Windows note:** If `chroma-hnswlib` fails to build, run `pip install chroma-hnswlib==0.7.6a9` first, then `pip install -r requirements-dev.txt`.

### 3. Secrets

```bash
copy .env.example .env   # Windows
# cp .env.example .env   # macOS/Linux
```

Add your free Groq key from [console.groq.com/keys](https://console.groq.com/keys):

```
GROQ_API_KEY="gsk_your_key_here"
```

> Never commit `.env` — it is in `.gitignore`.

### 4. Run

```bash
streamlit run app.py
```

Open [http://localhost:8501](http://localhost:8501)

---

## Docker

```bash
copy .env.example .env   # add GROQ_API_KEY
docker compose up --build
```

App at [http://localhost:8501](http://localhost:8501)

---

## Testing

```bash
pytest -m "not groq" -v
python -m eval.run_eval
python -m eval.run_eval --with-llm   # needs GROQ_API_KEY
```

See [TESTING.md](TESTING.md) for the manual QA checklist.

### CI (GitHub Actions)

| Step | Cost |
|------|------|
| Fast unit tests | Free |
| RAG retrieval eval | Free |
| Full pytest (embeddings) | Free |
| Generation eval (optional) | Groq free tier |

Add `GROQ_API_KEY` as a repository secret for generation eval on `main`.

---

## Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `GROQ_API_KEY` | — | Groq API key (required for generation) |
| `MAX_FILE_SIZE_MB` | `10` | Max size per uploaded file |
| `MAX_TOTAL_UPLOAD_MB` | `25` | Max combined upload size |

---

## Project structure

```
qa-rag-assistant/
├── app.py                 # Streamlit UI
├── core.py                # Pipeline logic (testable)
├── documentation.py       # In-app architecture & workflow
├── theme.py               # UI theme
├── exports.py             # QA tool CSV exports
├── eval/                  # RAG metrics + benchmark
├── tests/                 # Pytest suite (45 cases)
├── docs/images/           # README visuals
├── .github/workflows/     # CI
├── Dockerfile
└── docker-compose.yml
```

---

## Deployment

| Platform | Notes |
|----------|-------|
| **Streamlit Community Cloud** | [Live demo](https://app-rag-assistant-sysvsxop8pfbhj5xt2zgp3.streamlit.app) — set `GROQ_API_KEY` in Secrets; prefer **Python 3.11** |
| **Docker** | `docker compose up --build` |
| **Render / Railway / Fly.io** | Deploy image; inject env vars |

`requirements.txt` omits `streamlit` so Community Cloud uses its managed version.

---

## Security

- `.env` and `chroma_db/` are gitignored
- Upload limits configurable via env vars
- Groq key required only for generation, not indexing

---

## License

[MIT](LICENSE) — Copyright (c) 2026 Shashanka Palla
