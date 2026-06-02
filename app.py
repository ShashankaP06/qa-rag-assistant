try:
    __import__("pysqlite3")
    import sys

    sys.modules["sqlite3"] = sys.modules.pop("pysqlite3")
except ImportError:
    pass

import os
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_community.vectorstores import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
from langchain_huggingface import HuggingFaceEmbeddings

from core import (
    CHROMA_PERSIST_DIR,
    DEFAULT_LLM_MODEL,
    DEFAULT_LLM_TEMPERATURE,
    DEFAULT_RETRIEVAL_K,
    EMBEDDING_MODEL,
    GROQ_MODELS,
    QUICK_ACTIONS,
    SYSTEM_PROMPT,
    batch_hash_signature,
    build_indexed_file_records,
    build_query_with_history,
    build_vectorstore,
    friendly_api_error,
    get_groq_api_key,
    load_documents,
    load_index_metadata,
    parse_markdown_table,
    relevance_score,
    save_index_metadata,
    split_documents,
    validate_groq_env,
    validate_uploads,
)
from exports import EXPORT_FORMATS, export_test_suite
from theme import inject_forge_theme

load_dotenv(Path(__file__).parent / ".env", override=True)


def _sync_streamlit_secrets_to_env() -> None:
    """Local .streamlit/secrets.toml; Cloud also sets root secrets as env vars."""
    if os.getenv("GROQ_API_KEY"):
        return
    try:
        if "GROQ_API_KEY" not in st.secrets:
            return
        key = st.secrets["GROQ_API_KEY"]
    except Exception:
        return
    if key:
        os.environ["GROQ_API_KEY"] = str(key).strip().strip('"').strip("'")


# ---------------------------------------------------------------------------
# Session & persistence helpers
# ---------------------------------------------------------------------------


def init_session_state() -> None:
    defaults = {
        "vectorstore": None,
        "retrieval_chain": None,
        "processed_hash_signature": None,
        "indexed_files": [],
        "last_context_docs": [],
        "last_answer": "",
        "last_query": "",
        "embeddings_model": None,
        "chain_settings": None,
        "persist_index": True,
        "chat_messages": [],
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def get_embeddings() -> HuggingFaceEmbeddings:
    if st.session_state.embeddings_model is None:
        st.session_state.embeddings_model = HuggingFaceEmbeddings(
            model_name=EMBEDDING_MODEL
        )
    return st.session_state.embeddings_model


def clear_index() -> None:
    import shutil

    st.session_state.vectorstore = None
    st.session_state.retrieval_chain = None
    st.session_state.processed_hash_signature = None
    st.session_state.indexed_files = []
    st.session_state.last_context_docs = []
    st.session_state.last_answer = ""
    st.session_state.last_query = ""
    st.session_state.chain_settings = None
    st.session_state.chat_messages = []
    if CHROMA_PERSIST_DIR.exists():
        shutil.rmtree(CHROMA_PERSIST_DIR, ignore_errors=True)


def try_load_persisted_index() -> None:
    if (
        st.session_state.vectorstore is not None
        or not st.session_state.persist_index
        or not CHROMA_PERSIST_DIR.exists()
    ):
        return

    metadata = load_index_metadata()
    if metadata is None:
        return

    try:
        st.session_state.vectorstore = Chroma(
            persist_directory=str(CHROMA_PERSIST_DIR),
            embedding_function=get_embeddings(),
            collection_name="qa_rag_docs",
        )
        st.session_state.indexed_files = metadata.get("files", [])
        sig = metadata.get("signature")
        st.session_state.processed_hash_signature = (
            tuple(tuple(item) for item in sig) if sig else None
        )
    except Exception:
        clear_index()


# ---------------------------------------------------------------------------
# Document ingestion
# ---------------------------------------------------------------------------


def ingest_files(uploaded_files: list, persist: bool) -> None:
    signature = batch_hash_signature(uploaded_files)
    if signature == st.session_state.processed_hash_signature:
        return

    with st.spinner("Processing documents and building vector store..."):
        documents = load_documents(uploaded_files)
        if not documents:
            st.warning("No readable content found in the uploaded files.")
            return

        chunks = split_documents(documents)
        vectorstore = build_vectorstore(
            chunks,
            get_embeddings(),
            persist=persist,
        )
        indexed_files = build_indexed_file_records(uploaded_files, chunks)

        st.session_state.vectorstore = vectorstore
        st.session_state.retrieval_chain = None
        st.session_state.chain_settings = None
        st.session_state.processed_hash_signature = signature
        st.session_state.indexed_files = indexed_files

        if persist:
            save_index_metadata(indexed_files, signature)


# ---------------------------------------------------------------------------
# LLM & retrieval chain
# ---------------------------------------------------------------------------


def require_groq_api_key() -> str:
    api_key = get_groq_api_key()
    if api_key is None:
        st.error(
            "GROQ_API_KEY is missing or still set to the placeholder. "
            "Add your free key to `qa-rag-assistant/.env`, then refresh this page. "
            "Get one at [console.groq.com/keys](https://console.groq.com/keys)."
        )
        st.stop()
    return api_key


def build_retrieval_chain(vectorstore: Chroma, model: str, temperature: float, k: int):
    groq_api_key = require_groq_api_key()

    llm = ChatGroq(
        groq_api_key=groq_api_key,
        model_name=model,
        temperature=temperature,
    )

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", SYSTEM_PROMPT),
            ("human", "{input}"),
        ]
    )

    document_chain = create_stuff_documents_chain(llm, prompt)
    retriever = vectorstore.as_retriever(search_kwargs={"k": k})
    return create_retrieval_chain(retriever, document_chain)


def invalidate_chain_if_settings_changed(model: str, temperature: float, k: int) -> None:
    settings = (model, temperature, k)
    if st.session_state.chain_settings != settings:
        st.session_state.retrieval_chain = None
        st.session_state.chain_settings = settings


def run_generation(
    query: str,
    model: str,
    temperature: float,
    retrieval_k: int,
    *,
    use_history: bool = False,
) -> tuple[str, list] | None:
    if st.session_state.vectorstore is None:
        st.warning("Please upload and index at least one document first.")
        return None

    if st.session_state.retrieval_chain is None:
        st.session_state.retrieval_chain = build_retrieval_chain(
            st.session_state.vectorstore,
            model=model,
            temperature=temperature,
            k=retrieval_k,
        )

    final_query = (
        build_query_with_history(query, st.session_state.chat_messages)
        if use_history
        else query
    )

    with st.spinner("Generating test suite from retrieved context..."):
        try:
            result = st.session_state.retrieval_chain.invoke({"input": final_query})
            answer = result.get("answer", "No response generated.")
            context_docs = result.get("context", [])
        except Exception as exc:
            st.error(friendly_api_error(exc))
            st.session_state.retrieval_chain = None
            return None

    st.session_state.chat_messages.append({"role": "user", "content": query})
    st.session_state.chat_messages.append({"role": "assistant", "content": answer})
    st.session_state.last_answer = answer
    st.session_state.last_query = query
    st.session_state.last_context_docs = context_docs
    return answer, context_docs


# ---------------------------------------------------------------------------
# UI components
# ---------------------------------------------------------------------------


def render_test_suite_output(answer: str) -> None:
    df = parse_markdown_table(answer)
    if df is not None and not df.empty:
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.markdown(answer)


def render_export_buttons(answer: str) -> None:
    if not answer.strip():
        return

    df = parse_markdown_table(answer)
    st.markdown("**Export test suite**")

    row1 = st.columns(2)
    with row1[0]:
        st.download_button(
            label="Markdown",
            data=answer,
            file_name="test_suite.md",
            mime="text/markdown",
            use_container_width=True,
        )
    with row1[1]:
        csv_data = df.to_csv(index=False) if df is not None else answer
        st.download_button(
            label="CSV",
            data=csv_data,
            file_name="test_suite.csv",
            mime="text/csv",
            use_container_width=True,
        )

    if df is not None and not df.empty:
        row2 = st.columns(3)
        tool_exports = list(EXPORT_FORMATS.items())
        for col, (label, _) in zip(row2, tool_exports):
            with col:
                tool_csv = export_test_suite(df, label)
                st.download_button(
                    label=label,
                    data=tool_csv or "",
                    file_name=f"test_suite_{label.lower().replace(' ', '_')}.csv",
                    mime="text/csv",
                    use_container_width=True,
                )


def render_sidebar() -> tuple[str, float, int]:
    st.sidebar.header("Settings")
    st.sidebar.caption("All settings are free — no extra API cost.")

    model = st.sidebar.selectbox(
        "Groq model",
        options=GROQ_MODELS,
        index=GROQ_MODELS.index(DEFAULT_LLM_MODEL),
    )
    temperature = st.sidebar.slider(
        "Temperature",
        min_value=0.0,
        max_value=1.0,
        value=DEFAULT_LLM_TEMPERATURE,
        step=0.1,
        help="Lower = more deterministic test cases.",
    )
    retrieval_k = st.sidebar.slider(
        "Retrieval depth (k)",
        min_value=1,
        max_value=10,
        value=DEFAULT_RETRIEVAL_K,
        help="Number of document chunks sent to the LLM as context.",
    )
    persist_index = st.sidebar.checkbox(
        "Persist index to disk",
        value=st.session_state.persist_index,
        help="Survives browser refresh. Stored locally in chroma_db/.",
    )
    st.session_state.persist_index = persist_index

    env_status = validate_groq_env()
    if env_status["groq_key_set"]:
        st.sidebar.success("Groq API key loaded")
    else:
        st.sidebar.warning("Groq API key missing — indexing works; generation disabled.")

    st.sidebar.caption(
        f"Upload limits: {env_status['max_file_mb']} MB/file, "
        f"{env_status['max_total_mb']} MB total"
    )

    st.sidebar.divider()
    st.sidebar.subheader("Indexed Documents")
    if st.session_state.indexed_files:
        for file_info in st.session_state.indexed_files:
            st.sidebar.text(
                f"{file_info['name']}\n"
                f"  {file_info['size_kb']} KB · {file_info['chunks']} chunks · "
                f"#{file_info['hash']}"
            )
    else:
        st.sidebar.info("No documents indexed yet.")

    if st.sidebar.button("Clear index & start over", use_container_width=True):
        clear_index()
        st.sidebar.success("Index cleared.")
        st.rerun()

    if st.session_state.chat_messages and st.sidebar.button(
        "Clear chat history", use_container_width=True
    ):
        st.session_state.chat_messages = []
        st.session_state.last_answer = ""
        st.session_state.last_query = ""
        st.session_state.last_context_docs = []
        st.sidebar.success("Chat cleared.")
        st.rerun()

    return model, temperature, retrieval_k


def render_source_expander(
    context_docs: list,
    query: str,
    vectorstore: Chroma | None,
    k: int,
) -> None:
    with st.expander("Retrieved Source Chunks (RAG Transparency)", expanded=False):
        if query:
            st.markdown(f"**Query sent:** {query}")

        if not context_docs and not vectorstore:
            st.info("No source chunks were retrieved for this query.")
            return

        scored_docs: list[tuple] = []
        if vectorstore and query:
            try:
                scored_docs = vectorstore.similarity_search_with_score(query, k=k)
            except Exception:
                scored_docs = []

        if scored_docs:
            st.caption(
                "Similarity scores: higher = more relevant (0–1 scale). "
                "Chunks used by the LLM are listed first."
            )
            for idx, (doc, distance) in enumerate(scored_docs, start=1):
                score = relevance_score(distance)
                source = doc.metadata.get("original_filename") or doc.metadata.get(
                    "source", "Unknown"
                )
                page = doc.metadata.get("page")
                header = (
                    f"Chunk {idx} — `{source}` — "
                    f"Relevance: **{score}** (distance: {distance:.4f})"
                )
                if page is not None:
                    header += f" — Page {page + 1}"
                st.markdown(header)
                st.text(doc.page_content)
                if idx < len(scored_docs):
                    st.divider()
        else:
            for idx, doc in enumerate(context_docs, start=1):
                source = doc.metadata.get("original_filename") or doc.metadata.get(
                    "source", "Unknown"
                )
                page = doc.metadata.get("page")
                header = f"Chunk {idx} — Source: `{source}`"
                if page is not None:
                    header += f" (Page {page + 1})"
                st.markdown(f"**{header}**")
                st.text(doc.page_content)
                if idx < len(context_docs):
                    st.divider()


def main() -> None:
    st.set_page_config(
        page_title="QA RAG Assistant",
        page_icon="🧪",
        layout="wide",
    )
    inject_forge_theme()

    _sync_streamlit_secrets_to_env()
    init_session_state()
    model, temperature, retrieval_k = render_sidebar()
    invalidate_chain_if_settings_changed(model, temperature, retrieval_k)
    try_load_persisted_index()

    st.title("QA RAG Assistant")
    st.markdown(
        "Upload requirements or specification documents (`.txt`, `.pdf`) to generate "
        "evidence-based test suites powered by **local embeddings** (free) and "
        "**Groq LLM** (free tier)."
    )

    uploaded_files = st.file_uploader(
        "Upload specification documents",
        type=["txt", "pdf"],
        accept_multiple_files=True,
    )

    if uploaded_files:
        valid, error = validate_uploads(uploaded_files)
        if not valid:
            st.error(error)
        else:
            ingest_files(uploaded_files, persist=st.session_state.persist_index)
            if st.session_state.vectorstore is not None:
                st.success(
                    f"Indexed **{len(st.session_state.indexed_files)}** file(s): "
                    f"{', '.join(f['name'] for f in st.session_state.indexed_files)}."
                )
                if get_groq_api_key() is None:
                    st.info(
                        "Documents indexed locally. Copy `.env.example` to `.env` and "
                        "add your Groq API key to generate test suites."
                    )
    elif st.session_state.vectorstore is None:
        st.info("Upload one or more `.txt` or `.pdf` files to begin.")
    elif st.session_state.indexed_files:
        st.success(
            "Using persisted index: "
            + ", ".join(f["name"] for f in st.session_state.indexed_files)
        )

    st.divider()

    action = st.selectbox("Quick Actions", options=list(QUICK_ACTIONS.keys()))

    custom_query = ""
    if action == "Custom Inquiry":
        custom_query = st.text_input(
            "Enter your custom QA inquiry",
            placeholder="e.g., What negative test cases should we write for the login module?",
        )

    generate = st.button(
        "Generate Test Suite",
        type="primary",
        disabled=st.session_state.vectorstore is None,
    )

    if generate:
        if action == "Custom Inquiry":
            if not custom_query.strip():
                st.warning("Please enter a custom inquiry before generating.")
                st.stop()
            query = custom_query.strip()
        else:
            query = QUICK_ACTIONS[action]

        result = run_generation(
            query, model, temperature, retrieval_k, use_history=False
        )
        if result:
            answer, context_docs = result
            st.markdown("### Generated Test Suite")
            render_test_suite_output(answer)
            render_export_buttons(answer)
            render_source_expander(
                context_docs, query, st.session_state.vectorstore, retrieval_k
            )

    elif st.session_state.last_answer:
        st.markdown("### Generated Test Suite")
        render_test_suite_output(st.session_state.last_answer)
        render_export_buttons(st.session_state.last_answer)
        render_source_expander(
            st.session_state.last_context_docs,
            st.session_state.last_query,
            st.session_state.vectorstore,
            retrieval_k,
        )

    if st.session_state.vectorstore is not None:
        st.divider()
        st.subheader("Follow-up chat")
        st.caption(
            "Ask refinements like: *Add 5 negative test cases for the payment lockout rule.*"
        )

        for message in st.session_state.chat_messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        follow_up = st.chat_input(
            "Ask a follow-up question about your test suite...",
            disabled=st.session_state.vectorstore is None,
        )
        if follow_up:
            result = run_generation(
                follow_up.strip(),
                model,
                temperature,
                retrieval_k,
                use_history=True,
            )
            if result:
                st.rerun()


main()
