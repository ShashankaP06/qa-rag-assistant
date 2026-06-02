# QA RAG Assistant

Evidence-based QA test suite generator powered by **local RAG** (free-tier friendly).

Upload requirements documents (`.txt`, `.pdf`) → retrieve relevant context → generate structured test case matrices via **Groq LLM** (free tier).

## Features

- Local embeddings (`all-MiniLM-L6-v2`) — no embedding API cost
- In-memory / disk-persisted Chroma vector store
- Quick actions: functional tests, boundary/edge cases, custom inquiry
- Source chunk transparency with similarity scores
- Export to Markdown and CSV
- RAG evaluation benchmark (`eval/run_eval.py`)
- Automated CI via GitHub Actions
- **Follow-up chat** for iterative test design
- **QA tool exports** — Jira, TestRail, Azure DevOps CSV

## Quick start (local)

### 1. Clone from GitHub

```bash
git clone https://github.com/ShashankaP06/qa-rag-assistant.git
cd qa-rag-assistant
```

### 2. Create virtual environment

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

### 3. Configure secrets

```bash
copy .env.example .env   # Windows
# cp .env.example .env   # macOS/Linux
```

Edit `.env` and add your free Groq key from [console.groq.com/keys](https://console.groq.com/keys):

```
GROQ_API_KEY="gsk_your_key_here"
```

> **Never commit `.env`** — it is listed in `.gitignore`.

### 4. Run the app

```bash
streamlit run app.py
```

Open [http://localhost:8501](http://localhost:8501)

## Docker

```bash
copy .env.example .env   # add your GROQ_API_KEY
docker compose up --build
```

App available at [http://localhost:8501](http://localhost:8501)

## GitHub setup (CI/CD)

1. Push this repo to GitHub
2. CI runs automatically on push/PR to `main` (see `.github/workflows/ci.yml`)
3. **Optional:** Add `GROQ_API_KEY` as a repository secret for live generation eval on `main`:
   - GitHub repo → **Settings** → **Secrets and variables** → **Actions** → **New repository secret**
   - Name: `GROQ_API_KEY`
   - Value: your Groq API key

### What CI runs

| Step | Cost |
|------|------|
| Fast unit tests | Free |
| RAG retrieval eval | Free (local embeddings) |
| Full pytest (embeddings) | Free |
| Generation eval (optional) | Groq free tier |

## Testing

```bash
# Fast tests (~5 sec)
pytest -m "not slow and not groq" -v

# Full suite including RAG eval
pytest -m "not groq" -v

# RAG evaluation report
python -m eval.run_eval

# With Groq generation eval
python -m eval.run_eval --with-llm
```

See [TESTING.md](TESTING.md) for the full manual QA checklist.

## Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `GROQ_API_KEY` | — | Groq API key (required for generation) |
| `MAX_FILE_SIZE_MB` | `10` | Max size per uploaded file |
| `MAX_TOTAL_UPLOAD_MB` | `25` | Max combined upload size |

## Project structure

```
qa-rag-assistant/
├── app.py              # Streamlit UI
├── core.py             # Pipeline logic (testable)
├── eval/               # RAG evaluation metrics + benchmark
├── tests/              # Pytest suite
├── .github/workflows/  # CI pipeline
├── Dockerfile
└── docker-compose.yml
```

## Deployment options

| Platform | Notes |
|----------|-------|
| **Docker** | Use included `Dockerfile` / `docker-compose.yml` |
| **Streamlit Community Cloud** | Connect GitHub repo; set `GROQ_API_KEY` in Secrets |
| **Render / Railway / Fly.io** | Deploy Docker image; inject env vars |

### Streamlit Cloud (free)

1. Push repo to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. New app → select repo → main file: `app.py`
4. Add `GROQ_API_KEY` in **Advanced settings → Secrets**
5. Use **Python 3.11** in Advanced settings if offered (recommended for ChromaDB)
6. `requirements.txt` intentionally omits `streamlit` — Community Cloud provides it

## Security notes

- `.env` and `chroma_db/` are gitignored
- Use `.env.example` as the template for collaborators
- Set upload limits via env vars to prevent abuse
- Groq key is only required for generation, not indexing

## License

MIT (add a LICENSE file before public release if desired)
