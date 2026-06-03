"""In-app interview guide for demoing the QA RAG Assistant."""

import streamlit as st

GITHUB_REPO = "https://github.com/ShashankaP06/qa-rag-assistant"


def render_interview_guide() -> None:
    st.sidebar.markdown("---")
    st.sidebar.header("Interview Guide")
    st.sidebar.caption(
        "Talking points for reviewers — architecture, demo flow, and quality signals."
    )

    with st.sidebar.expander("1. Elevator pitch", expanded=False):
        st.markdown(
            """
**Problem:** QA teams spend hours turning PRDs and specs into structured test cases.
Manual work is slow, inconsistent, and hard to trace back to source requirements.

**Solution:** A **RAG-powered assistant** that:
- Ingests `.txt` / `.pdf` requirements
- Retrieves the most relevant passages locally (no embedding API cost)
- Generates an **evidence-based test matrix** via Groq LLM (free tier)
- Shows **source chunks + similarity scores** so every case is auditable

**One-liner for interviews:**
> *"Local retrieval for cost and privacy, cloud LLM only for generation,
> with full source transparency for QA traceability."*
            """
        )

    with st.sidebar.expander("2. Architecture (RAG pipeline)", expanded=False):
        st.markdown(
            """
```
Upload PRD (.txt / .pdf)
        ↓
Load & split (1000 / 200 overlap)
        ↓
Embed locally (all-MiniLM-L6-v2)
        ↓
Store in Chroma (memory or disk)
        ↓
User query → similarity search (top-k)
        ↓
Groq LLM + retrieved context
        ↓
8-column Markdown test table + exports
```

**Modules**
| File | Role |
|------|------|
| `app.py` | Streamlit UI, chat, exports |
| `core.py` | Ingestion, validation, RAG helpers |
| `exports.py` | Jira / TestRail / Azure DevOps CSV |
| `eval/` | RAG benchmarks (Hit@k, MRR, faithfulness) |
| `tests/` | 45 pytest cases + CI |

**Session design:** Embeddings cached in session; Groq client lazy-init
so **indexing works without an API key** — only Generate requires Groq.
            """
        )

    with st.sidebar.expander("3. Tech stack", expanded=False):
        st.markdown(
            """
| Layer | Choice | Why |
|-------|--------|-----|
| UI | Streamlit | Fast demo, file upload, chat |
| Orchestration | LangChain 0.2 | Retrieval chain, document loaders |
| Embeddings | HuggingFace `all-MiniLM-L6-v2` | Free, runs locally |
| Vector DB | ChromaDB 0.5 | In-memory + disk persist |
| LLM | Groq (`llama-3.3-70b-versatile`) | Free tier, fast inference |
| Tests | pytest + GitHub Actions | Automated on every push |
| Deploy | Docker + Streamlit Cloud | Portfolio-ready |

**Cost model:** Embeddings = $0. Generation = Groq free tier only.
            """
        )

    with st.sidebar.expander("4. Demo script (5 min)", expanded=False):
        st.markdown(
            """
**Recommended flow for live demo:**

1. **Upload** a sample PRD (`.txt` or `.pdf`) → show indexing success in sidebar.
2. **Quick action** → *Generate Functional Test Cases Matrix* → click **Generate**.
3. **Source transparency** → expand *Retrieved Source Chunks* → point out
   similarity scores and requirement traceability.
4. **Export** → download Markdown, generic CSV, or Jira / TestRail / ADO format.
5. **Follow-up chat** → e.g. *"Add 5 negative test cases for payment lockout."*
6. **Sidebar settings** → show model, temperature, retrieval-k tuning.

**Talking point:** Every generated row should map to retrieved context —
this is **evidence-based QA**, not blind LLM output.
            """
        )

    with st.sidebar.expander("5. Quality & RAG evaluation", expanded=False):
        st.markdown(
            """
**Automated tests (45 cases)**
- Core validation, ingestion, exports, RAG chain wiring
- Run locally: `pytest -m "not groq" -v`

**RAG eval benchmark** (`python -m eval.run_eval`)
| Metric | What it measures |
|--------|------------------|
| Hit@k | Correct chunk in top-k results |
| Keyword recall | Expected terms appear in retrieval |
| MRR | Rank of first relevant chunk |
| Negative retrieval | Out-of-scope queries return low scores |
| Faithfulness (optional) | LLM answer grounded in context |

**CI pipeline** (GitHub Actions on every PR/push)
- Fast unit tests → RAG retrieval eval → full pytest suite
- Optional Groq generation eval when `GROQ_API_KEY` secret is set
            """
        )

    with st.sidebar.expander("6. Design decisions (talking points)", expanded=False):
        st.markdown(
            """
- **Local embeddings** — no OpenAI embedding bill; data stays on your machine.
- **Lazy Groq init** — upload/index without API key; fail gracefully at Generate.
- **Content-hash re-index** — skip rebuild if same files re-uploaded.
- **Source Reference column** — every test row ties back to a requirement chunk.
- **Upload limits** — 10 MB/file, 25 MB total (configurable via env vars).
- **Separated `core.py`** — business logic testable without Streamlit UI.
- **Free-tier only** — intentional constraint for portfolio / pilot use.
            """
        )

    with st.sidebar.expander("7. Limitations & production gaps", expanded=False):
        st.markdown(
            """
**Be honest in interviews — shows maturity:**

| Gap | Current state |
|-----|---------------|
| Auth / multi-user | Single-user demo app |
| Scale | In-memory / local Chroma, not enterprise vector DB |
| Chat on re-index | Chat history not auto-cleared |
| Cloud persist | Index may reset on Streamlit Cloud redeploy |
| Enterprise QA tools | CSV export only (no live Jira API) |

**Good follow-up if asked:** *"For production I'd add auth, managed
vector store (Pinecone/pgvector), observability (LangSmith), and
human-in-the-loop approval before export."*
            """
        )

    with st.sidebar.expander("8. Links & commands", expanded=False):
        st.markdown(
            f"""
**Repository:** [{GITHUB_REPO}]({GITHUB_REPO})

**Local run**
```bash
pip install -r requirements-dev.txt
copy .env.example .env   # add GROQ_API_KEY
streamlit run app.py
```

**Docker**
```bash
docker compose up --build
```

**Tests & eval**
```bash
pytest -m "not groq" -v
python -m eval.run_eval
python -m eval.run_eval --with-llm
```
            """
        )

    st.sidebar.markdown(
        f"[View source on GitHub]({GITHUB_REPO})",
        unsafe_allow_html=False,
    )
