"""Project documentation with a visual architecture overview."""

import streamlit as st

GITHUB_REPO = "https://github.com/ShashankaP06/qa-rag-assistant"

ARCHITECTURE_HTML = """
<style>
.arch-wrap {
    font-family: "Source Sans Pro", sans-serif;
    color: #e8e8f0;
    margin: 0.5rem 0 1.5rem 0;
    overflow-x: auto;
}
.arch-canvas {
    min-width: 920px;
    padding: 1.25rem;
    border: 1px solid rgba(123, 91, 242, 0.35);
    border-radius: 12px;
    background: linear-gradient(180deg, rgba(28, 28, 60, 0.55) 0%, rgba(14, 14, 26, 0.85) 100%);
}
.arch-title-bar {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    margin-bottom: 1rem;
    padding-bottom: 0.75rem;
    border-bottom: 1px solid rgba(123, 91, 242, 0.25);
}
.arch-title-bar h3 {
    margin: 0;
    color: #fff;
    font-size: 1.1rem;
    letter-spacing: 0.04em;
}
.arch-badge {
    font-size: 0.7rem;
    font-weight: 700;
    padding: 0.2rem 0.55rem;
    border-radius: 4px;
    background: #28a745;
    color: #fff;
}
.arch-boundary {
    border: 1px dashed rgba(45, 92, 247, 0.5);
    border-radius: 10px;
    padding: 1rem;
    margin-bottom: 1rem;
    position: relative;
}
.arch-boundary-label {
    position: absolute;
    top: -0.65rem;
    left: 1rem;
    background: #12122b;
    padding: 0 0.5rem;
    font-size: 0.72rem;
    font-weight: 700;
    color: #ffc107;
    letter-spacing: 0.06em;
}
.arch-pipeline {
    display: flex;
    align-items: stretch;
    gap: 0.35rem;
    flex-wrap: nowrap;
}
.arch-zone {
    flex: 1;
    min-width: 130px;
    border: 1px solid rgba(123, 91, 242, 0.2);
    border-radius: 8px;
    padding: 0.65rem;
    background: rgba(18, 18, 43, 0.6);
}
.arch-zone-title {
    font-size: 0.62rem;
    font-weight: 700;
    color: #a0a0b8;
    letter-spacing: 0.08em;
    margin-bottom: 0.5rem;
    text-align: center;
}
.arch-card {
    border-radius: 8px;
    padding: 0.55rem 0.6rem;
    margin-bottom: 0.4rem;
    font-size: 0.78rem;
    line-height: 1.35;
    border: 1px solid transparent;
}
.arch-card strong {
    display: block;
    font-size: 0.8rem;
    color: #fff;
    margin-bottom: 0.15rem;
}
.arch-card span {
    color: #a0a0b8;
    font-size: 0.7rem;
}
.arch-card.purple {
    background: linear-gradient(180deg, rgba(123, 91, 242, 0.35) 0%, rgba(106, 75, 217, 0.2) 100%);
    border-color: rgba(123, 91, 242, 0.45);
}
.arch-card.blue {
    background: linear-gradient(180deg, rgba(45, 92, 247, 0.35) 0%, rgba(45, 92, 247, 0.15) 100%);
    border-color: rgba(45, 92, 247, 0.45);
}
.arch-card.green {
    background: linear-gradient(180deg, rgba(40, 167, 69, 0.35) 0%, rgba(40, 167, 69, 0.15) 100%);
    border-color: rgba(40, 167, 69, 0.45);
}
.arch-card.gold {
    background: linear-gradient(180deg, rgba(255, 193, 7, 0.25) 0%, rgba(255, 193, 7, 0.1) 100%);
    border-color: rgba(255, 193, 7, 0.4);
}
.arch-card.red {
    background: linear-gradient(180deg, rgba(114, 28, 36, 0.45) 0%, rgba(114, 28, 36, 0.2) 100%);
    border-color: rgba(192, 57, 43, 0.45);
}
.arch-arrow {
    display: flex;
    align-items: center;
    justify-content: center;
    color: #2d5cf7;
    font-size: 1.4rem;
    font-weight: bold;
    min-width: 1.25rem;
    padding-top: 1.5rem;
}
.arch-support {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 0.65rem;
    margin-top: 0.5rem;
}
.arch-support .arch-card { margin-bottom: 0; }
.arch-legend {
    display: flex;
    flex-wrap: wrap;
    gap: 1rem;
    margin-top: 1rem;
    font-size: 0.72rem;
    color: #a0a0b8;
}
.arch-legend i {
    display: inline-block;
    width: 12px;
    height: 12px;
    border-radius: 3px;
    margin-right: 0.35rem;
    vertical-align: middle;
}
</style>
<div class="arch-wrap">
<div class="arch-canvas">
  <div class="arch-title-bar">
    <h3>SYSTEM ARCHITECTURE</h3>
    <span class="arch-badge">RAG PIPELINE</span>
  </div>

  <div class="arch-boundary">
    <span class="arch-boundary-label">END-TO-END DATA FLOW</span>
    <div class="arch-pipeline">
      <div class="arch-zone">
        <div class="arch-zone-title">INPUT</div>
        <div class="arch-card purple">
          <strong>File Upload</strong>
          <span>.txt / .pdf · max 10 MB</span>
        </div>
        <div class="arch-card purple">
          <strong>Validation</strong>
          <span>Size & type checks</span>
        </div>
      </div>
      <div class="arch-arrow">→</div>
      <div class="arch-zone">
        <div class="arch-zone-title">INGESTION</div>
        <div class="arch-card blue">
          <strong>Document Loaders</strong>
          <span>PyPDF · TextLoader</span>
        </div>
        <div class="arch-card blue">
          <strong>Text Splitter</strong>
          <span>1000 chars · 200 overlap</span>
        </div>
        <div class="arch-card blue">
          <strong>Hash Dedup</strong>
          <span>Skip re-index if unchanged</span>
        </div>
      </div>
      <div class="arch-arrow">→</div>
      <div class="arch-zone">
        <div class="arch-zone-title">EMBEDDING</div>
        <div class="arch-card green">
          <strong>MiniLM-L6-v2</strong>
          <span>Local · no API cost</span>
        </div>
        <div class="arch-card green">
          <strong>ChromaDB</strong>
          <span>Memory or disk persist</span>
        </div>
      </div>
      <div class="arch-arrow">→</div>
      <div class="arch-zone">
        <div class="arch-zone-title">RETRIEVAL</div>
        <div class="arch-card blue">
          <strong>Similarity Search</strong>
          <span>Top-k chunks (configurable)</span>
        </div>
        <div class="arch-card blue">
          <strong>Source Scores</strong>
          <span>Transparency expander</span>
        </div>
      </div>
      <div class="arch-arrow">→</div>
      <div class="arch-zone">
        <div class="arch-zone-title">GENERATION</div>
        <div class="arch-card purple">
          <strong>LangChain RAG</strong>
          <span>Retrieval + stuff chain</span>
        </div>
        <div class="arch-card purple">
          <strong>Groq LLM</strong>
          <span>llama-3.3-70b-versatile</span>
        </div>
      </div>
      <div class="arch-arrow">→</div>
      <div class="arch-zone">
        <div class="arch-zone-title">OUTPUT</div>
        <div class="arch-card gold">
          <strong>Test Matrix</strong>
          <span>8-column Markdown table</span>
        </div>
        <div class="arch-card gold">
          <strong>Exports & Chat</strong>
          <span>CSV · Jira · TestRail · ADO</span>
        </div>
      </div>
    </div>
  </div>

  <div class="arch-boundary">
    <span class="arch-boundary-label">CODEBASE MODULES</span>
    <div class="arch-support">
      <div class="arch-card purple">
        <strong>app.py</strong>
        <span>Streamlit UI · chat · theme</span>
      </div>
      <div class="arch-card blue">
        <strong>core.py</strong>
        <span>Ingestion · RAG · validation</span>
      </div>
      <div class="arch-card green">
        <strong>exports.py</strong>
        <span>QA tool CSV formats</span>
      </div>
      <div class="arch-card gold">
        <strong>eval/</strong>
        <span>Hit@k · MRR · faithfulness</span>
      </div>
      <div class="arch-card blue">
        <strong>tests/</strong>
        <span>45 pytest cases</span>
      </div>
      <div class="arch-card red">
        <strong>.github/workflows</strong>
        <span>CI on every push</span>
      </div>
      <div class="arch-card green">
        <strong>Docker</strong>
        <span>Container deploy</span>
      </div>
      <div class="arch-card purple">
        <strong>.env / Secrets</strong>
        <span>GROQ_API_KEY only for LLM</span>
      </div>
    </div>
  </div>

  <div class="arch-legend">
    <span><i style="background:#7b5bf2"></i> UI / LLM layer</span>
    <span><i style="background:#2d5cf7"></i> Processing / retrieval</span>
    <span><i style="background:#28a745"></i> Local / free-tier storage</span>
    <span><i style="background:#ffc107"></i> Output / evaluation</span>
    <span><i style="background:#c0392b"></i> Automation / ops</span>
  </div>
</div>
</div>
"""


def render_documentation() -> None:
    st.subheader("Documentation")
    st.caption(
        "Visual overview of the QA RAG Assistant — architecture, components, and quality pipeline."
    )

    st.markdown(ARCHITECTURE_HTML, unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        with st.expander("Overview", expanded=True):
            st.markdown(
                """
**Purpose:** Turn requirements documents into **traceable, evidence-based** test suites.

| Stage | What happens |
|-------|----------------|
| Upload | PRD / spec files ingested and validated |
| Index | Chunks embedded locally and stored in Chroma |
| Query | User picks a quick action or custom question |
| Generate | Top-k chunks + Groq LLM produce a test matrix |
| Review | Source chunks show similarity scores per requirement |
| Refine | Follow-up chat iterates on the suite |
| Export | Markdown, CSV, Jira, TestRail, or Azure DevOps formats |
                """
            )

        with st.expander("Technology stack"):
            st.markdown(
                """
| Component | Technology |
|-----------|------------|
| Frontend | Streamlit |
| Orchestration | LangChain 0.2 |
| Embeddings | HuggingFace `all-MiniLM-L6-v2` |
| Vector store | ChromaDB 0.5 |
| LLM | Groq (free tier) |
| Testing | pytest + GitHub Actions |
| Deployment | Docker · Streamlit Community Cloud |
                """
            )

    with col2:
        with st.expander("Design principles"):
            st.markdown(
                """
- **Local embeddings** — zero embedding API cost; requirements stay on-device during indexing.
- **Lazy LLM init** — indexing works without `GROQ_API_KEY`; generation fails gracefully if missing.
- **Source transparency** — every test case links back to retrieved requirement text.
- **Separated logic** — `core.py` is unit-tested independently of the UI.
- **Free-tier constraint** — deliberate scope for portfolio and pilot deployments.
                """
            )

        with st.expander("Quality assurance"):
            st.markdown(
                """
**Automated tests:** 45 pytest cases (core, ingestion, RAG chain, exports).

**RAG evaluation** (`python -m eval.run_eval`):
- Hit@k · Keyword recall · MRR
- Negative retrieval checks
- Optional faithfulness eval with `--with-llm`

**CI:** Runs on every push to `main` — fast tests, retrieval eval, full suite.
                """
            )

    st.markdown(f"**Repository:** [{GITHUB_REPO}]({GITHUB_REPO})")
