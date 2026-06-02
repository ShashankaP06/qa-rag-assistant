try:
    __import__("pysqlite3")
    import sys

    sys.modules["sqlite3"] = sys.modules.pop("pysqlite3")
except ImportError:
    pass

import hashlib
import json
import os
import shutil
import tempfile
from pathlib import Path

import pandas as pd
from groq import BadRequestError, RateLimitError
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_community.vectorstores import Chroma

APP_DIR = Path(__file__).parent
CHROMA_PERSIST_DIR = APP_DIR / "chroma_db"
METADATA_PATH = CHROMA_PERSIST_DIR / "index_metadata.json"
COLLECTION_NAME = "qa_rag_docs"

CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200
DEFAULT_RETRIEVAL_K = 4
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
DEFAULT_LLM_MODEL = "llama-3.3-70b-versatile"
DEFAULT_LLM_TEMPERATURE = 0.2
GROQ_API_KEY_PLACEHOLDER = "your_personal_groq_api_key_here"

MAX_FILE_SIZE_MB = int(os.getenv("MAX_FILE_SIZE_MB", "10"))
MAX_TOTAL_UPLOAD_MB = int(os.getenv("MAX_TOTAL_UPLOAD_MB", "25"))
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024
MAX_TOTAL_UPLOAD_BYTES = MAX_TOTAL_UPLOAD_MB * 1024 * 1024
ALLOWED_EXTENSIONS = {".txt", ".pdf"}

GROQ_MODELS = [
    "llama-3.3-70b-versatile",
    "llama-3.1-8b-instant",
    "openai/gpt-oss-120b",
]

QUICK_ACTIONS = {
    "Generate Functional Test Cases Matrix": (
        "Analyze the provided context and generate a comprehensive functional test "
        "cases matrix covering all major features, user flows, and business rules."
    ),
    "Generate Boundary Value & Edge Case Scenarios": (
        "Analyze the provided context and generate boundary value analysis and edge "
        "case test scenarios, including invalid inputs, limits, and failure modes."
    ),
    "Custom Inquiry": None,
}

SYSTEM_PROMPT = """You are a Senior Lead QA Automation Architect with deep expertise in \
test design, requirements analysis, and quality assurance best practices.

STRICT RULES:
1. Rely ONLY on facts explicitly stated in the context below. Do not invent features, \
requirements, or behaviors not supported by the context.
2. If the context lacks sufficient information for a test case, state "Insufficient context" \
in the Expected Result column for that row rather than guessing.
3. Output a complete test suite formatted as a Markdown table with EXACTLY these columns:
| Test ID | Component/Feature | Test Scenario | Pre-conditions | Execution Steps | Expected Result | Test Type (Positive/Negative) | Source Reference |
4. Use sequential Test IDs (TC-001, TC-002, ...).
5. Be precise, professional, and actionable in every cell.
6. Include both positive and negative test cases where applicable.
7. In the Source Reference column, cite the specific requirement, section, or phrase from \
the context that supports each test case (e.g., "Section 3.2 — Login validation rules").

<context>
{context}
</context>"""


def hash_bytes(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def file_content_hash(uploaded_file) -> str:
    return hash_bytes(uploaded_file.getvalue())


def batch_hash_signature(uploaded_files: list) -> tuple:
    return tuple(sorted((f.name, file_content_hash(f)) for f in uploaded_files))


def save_index_metadata(
    indexed_files: list,
    signature: tuple,
    metadata_path: Path = METADATA_PATH,
) -> None:
    metadata_path.parent.mkdir(parents=True, exist_ok=True)
    payload = {"files": indexed_files, "signature": list(signature)}
    metadata_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def load_index_metadata(metadata_path: Path = METADATA_PATH) -> dict | None:
    if not metadata_path.exists():
        return None
    try:
        return json.loads(metadata_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None


def get_groq_api_key() -> str | None:
    api_key = os.getenv("GROQ_API_KEY", "").strip().strip('"').strip("'")
    if not api_key or api_key == GROQ_API_KEY_PLACEHOLDER:
        return None
    return api_key


def friendly_api_error(exc: Exception) -> str:
    message = str(exc).lower()
    if isinstance(exc, RateLimitError) or "rate limit" in message:
        return (
            "Groq rate limit reached. Wait a moment and try again, or switch to "
            "`llama-3.1-8b-instant` in the sidebar for faster free-tier usage."
        )
    if "model_decommissioned" in message or "decommissioned" in message:
        return (
            "The selected Groq model is no longer available. "
            "Choose another model in the sidebar (e.g. `llama-3.3-70b-versatile`)."
        )
    if isinstance(exc, BadRequestError):
        if "invalid_api_key" in message or "unauthorized" in message:
            return "Invalid Groq API key. Check your `.env` file and refresh the page."
    if "timeout" in message or "timed out" in message:
        return "Request timed out. Try again or use a smaller document / lower retrieval depth."
    return f"Generation failed: {exc}"


def parse_markdown_table(text: str) -> pd.DataFrame | None:
    lines = [line.strip() for line in text.splitlines() if line.strip().startswith("|")]
    if len(lines) < 2:
        return None

    rows = []
    for line in lines:
        stripped = line.replace("|", "").replace("-", "").replace(":", "").strip()
        if not stripped:
            continue
        cells = [cell.strip() for cell in line.strip("|").split("|")]
        rows.append(cells)

    if len(rows) < 2:
        return None

    header, *data = rows
    col_count = len(header)
    normalized = []
    for row in data:
        padded = row + [""] * (col_count - len(row))
        normalized.append(padded[:col_count])

    return pd.DataFrame(normalized, columns=header)


def load_documents(uploaded_files: list) -> list:
    documents = []
    for uploaded_file in uploaded_files:
        suffix = Path(uploaded_file.name).suffix.lower()
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(uploaded_file.getvalue())
            tmp_path = tmp.name

        try:
            if suffix == ".txt":
                loader = TextLoader(tmp_path, encoding="utf-8")
            elif suffix == ".pdf":
                loader = PyPDFLoader(tmp_path)
            else:
                continue
            for doc in loader.load():
                doc.metadata["original_filename"] = uploaded_file.name
                documents.append(doc)
        finally:
            os.unlink(tmp_path)

    return documents


def split_documents(documents: list) -> list:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
    )
    return splitter.split_documents(documents)


def build_vectorstore(
    chunks: list,
    embeddings,
    persist: bool,
    chroma_dir: Path = CHROMA_PERSIST_DIR,
) -> Chroma:
    if persist and chroma_dir.exists():
        shutil.rmtree(chroma_dir, ignore_errors=True)

    kwargs = {
        "documents": chunks,
        "embedding": embeddings,
        "collection_name": COLLECTION_NAME,
    }
    if persist:
        chroma_dir.mkdir(parents=True, exist_ok=True)
        kwargs["persist_directory"] = str(chroma_dir)

    return Chroma.from_documents(**kwargs)


def build_indexed_file_records(uploaded_files: list, chunks: list) -> list:
    file_chunk_counts: dict[str, int] = {}
    for chunk in chunks:
        name = chunk.metadata.get("original_filename", "unknown")
        file_chunk_counts[name] = file_chunk_counts.get(name, 0) + 1

    return [
        {
            "name": uploaded_file.name,
            "hash": file_content_hash(uploaded_file)[:12],
            "size_kb": round(uploaded_file.size / 1024, 1),
            "chunks": file_chunk_counts.get(uploaded_file.name, 0),
        }
        for uploaded_file in uploaded_files
    ]


def relevance_score(distance: float) -> float:
    return round(1 / (1 + distance), 3)


def validate_uploads(uploaded_files: list) -> tuple[bool, str]:
    if not uploaded_files:
        return True, ""

    total_bytes = 0
    for uploaded_file in uploaded_files:
        suffix = Path(uploaded_file.name).suffix.lower()
        if suffix not in ALLOWED_EXTENSIONS:
            allowed = ", ".join(sorted(ALLOWED_EXTENSIONS))
            return False, f"Unsupported file `{uploaded_file.name}`. Allowed types: {allowed}"

        file_size = getattr(uploaded_file, "size", len(uploaded_file.getvalue()))
        if file_size > MAX_FILE_SIZE_BYTES:
            return False, (
                f"File `{uploaded_file.name}` exceeds the {MAX_FILE_SIZE_MB} MB limit."
            )
        total_bytes += file_size

    if total_bytes > MAX_TOTAL_UPLOAD_BYTES:
        return False, (
            f"Total upload size exceeds the {MAX_TOTAL_UPLOAD_MB} MB limit. "
            "Remove a file or upload smaller documents."
        )

    return True, ""


def validate_groq_env() -> dict:
    """Return secrets/config status for startup diagnostics."""
    key = get_groq_api_key()
    return {
        "groq_key_set": key is not None,
        "max_file_mb": MAX_FILE_SIZE_MB,
        "max_total_mb": MAX_TOTAL_UPLOAD_MB,
    }


def build_query_with_history(query: str, chat_messages: list) -> str:
    """Wrap a follow-up query with recent conversation context."""
    if not chat_messages:
        return query

    history_lines = []
    for msg in chat_messages[-8:]:
        role = "User" if msg["role"] == "user" else "Assistant"
        content = msg["content"]
        if len(content) > 800:
            content = content[:800] + "..."
        history_lines.append(f"{role}: {content}")

    return (
        "Continue this QA test design conversation using the indexed documents.\n\n"
        "Conversation so far:\n"
        + "\n".join(history_lines)
        + f"\n\nLatest request:\n{query}"
    )
