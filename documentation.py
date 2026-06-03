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
    align-items: center;
    justify-content: space-between;
    gap: 0.25rem;
    flex-wrap: nowrap;
    width: 100%;
}
.arch-zone {
    flex: 1 1 0;
    min-width: 0;
    display: flex;
    flex-direction: column;
    align-items: stretch;
    border: 1px solid rgba(123, 91, 242, 0.2);
    border-radius: 8px;
    padding: 0.75rem 0.5rem;
    background: rgba(18, 18, 43, 0.6);
    box-sizing: border-box;
}
.arch-zone-title {
    font-size: 0.62rem;
    font-weight: 700;
    color: #a0a0b8;
    letter-spacing: 0.08em;
    margin: 0 0 0.6rem 0;
    text-align: center;
    width: 100%;
}
.arch-zone-body {
    display: flex;
    flex-direction: column;
    align-items: stretch;
    justify-content: center;
    gap: 0.4rem;
    width: 100%;
    flex: 1;
}
.arch-card {
    width: 100%;
    max-width: 100%;
    box-sizing: border-box;
    border-radius: 8px;
    padding: 0.55rem 0.65rem;
    margin: 0;
    font-size: 0.78rem;
    line-height: 1.35;
    border: 1px solid transparent;
    text-align: center;
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
    align-self: center;
    flex: 0 0 auto;
    color: #2d5cf7;
    font-size: 1.25rem;
    font-weight: bold;
    width: 1.5rem;
    min-width: 1.5rem;
    padding: 0;
    line-height: 1;
}
.arch-support {
    display: grid;
    grid-template-columns: repeat(4, minmax(0, 1fr));
    gap: 0.65rem;
    margin-top: 0.5rem;
    width: 100%;
    align-items: stretch;
}
.arch-support .arch-card {
    margin: 0;
    height: 100%;
    min-height: 4.5rem;
    display: flex;
    flex-direction: column;
    justify-content: center;
}
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
        <div class="arch-zone-body">
          <div class="arch-card purple">
            <strong>File Upload</strong>
            <span>.txt / .pdf · max 10 MB</span>
          </div>
          <div class="arch-card purple">
            <strong>Validation</strong>
            <span>Size & type checks</span>
          </div>
        </div>
      </div>
      <div class="arch-arrow">→</div>
      <div class="arch-zone">
        <div class="arch-zone-title">INGESTION</div>
        <div class="arch-zone-body">
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
      </div>
      <div class="arch-arrow">→</div>
      <div class="arch-zone">
        <div class="arch-zone-title">EMBEDDING</div>
        <div class="arch-zone-body">
          <div class="arch-card green">
            <strong>MiniLM-L6-v2</strong>
            <span>Local · no API cost</span>
          </div>
          <div class="arch-card green">
            <strong>ChromaDB</strong>
            <span>Memory or disk persist</span>
          </div>
        </div>
      </div>
      <div class="arch-arrow">→</div>
      <div class="arch-zone">
        <div class="arch-zone-title">RETRIEVAL</div>
        <div class="arch-zone-body">
          <div class="arch-card blue">
            <strong>Similarity Search</strong>
            <span>Top-k chunks (configurable)</span>
          </div>
          <div class="arch-card blue">
            <strong>Source Scores</strong>
            <span>Transparency expander</span>
          </div>
        </div>
      </div>
      <div class="arch-arrow">→</div>
      <div class="arch-zone">
        <div class="arch-zone-title">GENERATION</div>
        <div class="arch-zone-body">
          <div class="arch-card purple">
            <strong>LangChain RAG</strong>
            <span>Retrieval + stuff chain</span>
          </div>
          <div class="arch-card purple">
            <strong>Groq LLM</strong>
            <span>llama-3.3-70b-versatile</span>
          </div>
        </div>
      </div>
      <div class="arch-arrow">→</div>
      <div class="arch-zone">
        <div class="arch-zone-title">OUTPUT</div>
        <div class="arch-zone-body">
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

DOC_PANELS_HTML = """
<style>
.doc-section {
    margin: 1.75rem 0 1rem 0;
}
.doc-section-header {
    display: flex;
    align-items: center;
    gap: 0.6rem;
    margin-bottom: 1rem;
    padding-bottom: 0.5rem;
    border-bottom: 1px solid rgba(123, 91, 242, 0.3);
}
.doc-section-header h4 {
    margin: 0;
    color: #fff;
    font-size: 0.95rem;
    letter-spacing: 0.06em;
    text-transform: uppercase;
}
.doc-section-tag {
    font-size: 0.65rem;
    padding: 0.15rem 0.45rem;
    border-radius: 4px;
    background: rgba(45, 92, 247, 0.25);
    color: #9eb8ff;
    font-weight: 600;
}
.workflow-panel {
    padding: 1.25rem 1rem 1.5rem;
    border: 1px solid rgba(123, 91, 242, 0.25);
    border-radius: 12px;
    background: rgba(18, 18, 43, 0.55);
    overflow-x: auto;
}
.workflow-track {
    display: flex;
    align-items: flex-start;
    justify-content: space-between;
    min-width: 880px;
    gap: 0;
    padding: 0.25rem 0;
}
.workflow-step {
    flex: 1;
    display: flex;
    flex-direction: column;
    align-items: center;
    text-align: center;
    position: relative;
    min-width: 100px;
    padding: 0 0.35rem;
}
.workflow-step:not(:last-child)::after {
    content: "";
    position: absolute;
    top: 1.15rem;
    left: calc(50% + 1.1rem);
    width: calc(100% - 2.2rem);
    height: 2px;
    background: linear-gradient(90deg, #2d5cf7, rgba(123, 91, 242, 0.5));
    z-index: 0;
}
.workflow-icon {
    width: 2.35rem;
    height: 2.35rem;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 0.85rem;
    font-weight: 800;
    color: #fff;
    background: linear-gradient(135deg, #7b5bf2, #2d5cf7);
    border: 2px solid rgba(157, 133, 247, 0.5);
    position: relative;
    z-index: 1;
    margin-bottom: 0.5rem;
}
.workflow-step:nth-child(5) .workflow-icon,
.workflow-step:nth-child(6) .workflow-icon {
    background: linear-gradient(135deg, #28a745, #1e7e34);
    border-color: rgba(40, 167, 69, 0.5);
}
.workflow-step:nth-child(7) .workflow-icon {
    background: linear-gradient(135deg, #ffc107, #d39e00);
    border-color: rgba(255, 193, 7, 0.5);
    color: #1a1a2e;
}
.workflow-label {
    font-size: 0.78rem;
    font-weight: 700;
    color: #fff;
    margin-bottom: 0.2rem;
}
.workflow-desc {
    font-size: 0.68rem;
    color: #a0a0b8;
    line-height: 1.35;
    max-width: 108px;
}
.doc-grid-3 {
    display: grid;
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: 1rem;
    width: 100%;
}
@media (max-width: 900px) {
    .doc-grid-3 { grid-template-columns: 1fr; }
}
.doc-panel {
    border: 1px solid rgba(45, 92, 247, 0.25);
    border-radius: 12px;
    padding: 1rem 1.1rem 1.15rem;
    background: rgba(18, 18, 43, 0.55);
    height: 100%;
    box-sizing: border-box;
}
.doc-panel h5 {
    margin: 0 0 0.85rem 0;
    color: #ffc107;
    font-size: 0.72rem;
    letter-spacing: 0.07em;
    text-transform: uppercase;
}
.tech-stack {
    display: flex;
    flex-direction: column;
    gap: 0.45rem;
}
.tech-row {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0.45rem 0.55rem;
    border-radius: 6px;
    background: rgba(45, 92, 247, 0.12);
    border: 1px solid rgba(45, 92, 247, 0.2);
}
.tech-row span:first-child {
    font-size: 0.68rem;
    color: #a0a0b8;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.04em;
}
.tech-row span:last-child {
    font-size: 0.76rem;
    color: #fff;
    font-weight: 600;
    text-align: right;
}
.principle-card {
    padding: 0.55rem 0.6rem;
    margin-bottom: 0.45rem;
    border-radius: 8px;
    border-left: 3px solid #7b5bf2;
    background: rgba(123, 91, 242, 0.1);
}
.principle-card:last-child { margin-bottom: 0; }
.principle-card strong {
    display: block;
    font-size: 0.76rem;
    color: #fff;
    margin-bottom: 0.15rem;
}
.principle-card p {
    margin: 0;
    font-size: 0.68rem;
    color: #a0a0b8;
    line-height: 1.4;
}
.kpi-row {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 0.5rem;
    margin-bottom: 0.75rem;
}
.kpi-box {
    text-align: center;
    padding: 0.55rem 0.35rem;
    border-radius: 8px;
    background: rgba(40, 167, 69, 0.15);
    border: 1px solid rgba(40, 167, 69, 0.35);
}
.kpi-box .kpi-val {
    font-size: 1.15rem;
    font-weight: 800;
    color: #28a745;
    line-height: 1.2;
}
.kpi-box .kpi-lbl {
    font-size: 0.62rem;
    color: #a0a0b8;
    text-transform: uppercase;
    letter-spacing: 0.04em;
}
.metric-pill {
    display: inline-block;
    font-size: 0.65rem;
    padding: 0.2rem 0.45rem;
    margin: 0.15rem 0.2rem 0.15rem 0;
    border-radius: 4px;
    background: rgba(255, 193, 7, 0.15);
    border: 1px solid rgba(255, 193, 7, 0.35);
    color: #ffe082;
}
.doc-footer {
    margin-top: 1.25rem;
    padding-top: 0.75rem;
    border-top: 1px solid rgba(123, 91, 242, 0.2);
    font-size: 0.8rem;
    color: #a0a0b8;
}
.doc-footer a { color: #7b5bf2; font-weight: 600; text-decoration: none; }
.doc-purpose {
    font-size: 0.85rem;
    color: #c8c8dc;
    margin: 0 0 1rem 0;
    line-height: 1.5;
}
</style>

<div class="doc-section">
  <div class="doc-section-header">
    <h4>Product workflow</h4>
    <span class="doc-section-tag">7 STAGES</span>
  </div>
  <p class="doc-purpose">
    End-to-end journey from requirements upload to exportable test artifacts —
    each stage is traceable to source documents.
  </p>
  <div class="workflow-panel">
    <div class="workflow-track">
      <div class="workflow-step">
        <div class="workflow-icon">1</div>
        <div class="workflow-label">Upload</div>
        <div class="workflow-desc">PRD / spec validated & ingested</div>
      </div>
      <div class="workflow-step">
        <div class="workflow-icon">2</div>
        <div class="workflow-label">Index</div>
        <div class="workflow-desc">Chunks embedded in Chroma</div>
      </div>
      <div class="workflow-step">
        <div class="workflow-icon">3</div>
        <div class="workflow-label">Query</div>
        <div class="workflow-desc">Quick action or custom prompt</div>
      </div>
      <div class="workflow-step">
        <div class="workflow-icon">4</div>
        <div class="workflow-label">Generate</div>
        <div class="workflow-desc">Top-k context + Groq LLM</div>
      </div>
      <div class="workflow-step">
        <div class="workflow-icon">5</div>
        <div class="workflow-label">Review</div>
        <div class="workflow-desc">Source chunks & similarity scores</div>
      </div>
      <div class="workflow-step">
        <div class="workflow-icon">6</div>
        <div class="workflow-label">Refine</div>
        <div class="workflow-desc">Follow-up chat iterations</div>
      </div>
      <div class="workflow-step">
        <div class="workflow-icon">7</div>
        <div class="workflow-label">Export</div>
        <div class="workflow-desc">MD · CSV · Jira · TestRail · ADO</div>
      </div>
    </div>
  </div>
</div>

<div class="doc-section">
  <div class="doc-section-header">
    <h4>Platform capabilities</h4>
    <span class="doc-section-tag">ENGINEERING</span>
  </div>
  <div class="doc-grid-3">
    <div class="doc-panel">
      <h5>Technology stack</h5>
      <div class="tech-stack">
        <div class="tech-row"><span>Frontend</span><span>Streamlit</span></div>
        <div class="tech-row"><span>Orchestration</span><span>LangChain 0.2</span></div>
        <div class="tech-row"><span>Embeddings</span><span>MiniLM-L6-v2</span></div>
        <div class="tech-row"><span>Vector DB</span><span>ChromaDB 0.5</span></div>
        <div class="tech-row"><span>LLM</span><span>Groq (free tier)</span></div>
        <div class="tech-row"><span>CI / Tests</span><span>pytest · GitHub Actions</span></div>
        <div class="tech-row"><span>Deploy</span><span>Docker · Streamlit Cloud</span></div>
      </div>
    </div>
    <div class="doc-panel">
      <h5>Design principles</h5>
      <div class="principle-card">
        <strong>Local embeddings</strong>
        <p>Zero embedding API cost; requirements stay on-device during indexing.</p>
      </div>
      <div class="principle-card">
        <strong>Lazy LLM initialization</strong>
        <p>Index without API key; generation fails gracefully when key is missing.</p>
      </div>
      <div class="principle-card">
        <strong>Source transparency</strong>
        <p>Every test case maps to retrieved requirement text with scores.</p>
      </div>
      <div class="principle-card">
        <strong>Testable core</strong>
        <p>Business logic in core.py, decoupled from Streamlit UI.</p>
      </div>
    </div>
    <div class="doc-panel">
      <h5>Quality & operations</h5>
      <div class="kpi-row">
        <div class="kpi-box"><div class="kpi-val">45</div><div class="kpi-lbl">Unit tests</div></div>
        <div class="kpi-box"><div class="kpi-val">100%</div><div class="kpi-lbl">RAG eval pass</div></div>
        <div class="kpi-box"><div class="kpi-val">CI</div><div class="kpi-lbl">On push</div></div>
      </div>
      <div style="font-size:0.68rem;color:#a0a0b8;line-height:1.5;">
        RAG benchmark metrics:
        <span class="metric-pill">Hit@k</span>
        <span class="metric-pill">Keyword recall</span>
        <span class="metric-pill">MRR</span>
        <span class="metric-pill">Negative retrieval</span>
        <span class="metric-pill">Faithfulness</span>
      </div>
      <p style="margin:0.65rem 0 0;font-size:0.68rem;color:#a0a0b8;">
        Run: <code style="color:#9eb8ff;">python -m eval.run_eval</code>
      </p>
    </div>
  </div>
</div>

<div class="doc-footer">
  Source repository —
  <a href="GITHUB_REPO_PLACEHOLDER" target="_blank" rel="noopener">github.com/ShashankaP06/qa-rag-assistant</a>
</div>
""".replace("GITHUB_REPO_PLACEHOLDER", GITHUB_REPO)


def render_documentation() -> None:
    st.subheader("Documentation")
    st.caption(
        "System architecture, product workflow, and engineering capabilities."
    )

    st.markdown(ARCHITECTURE_HTML, unsafe_allow_html=True)
    st.markdown(DOC_PANELS_HTML, unsafe_allow_html=True)
