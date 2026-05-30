"""RAG evaluation runner — local retrieval metrics + optional Groq generation eval."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

EVAL_DIR = Path(__file__).parent
PROJECT_DIR = EVAL_DIR.parent
FIXTURES_DIR = PROJECT_DIR / "tests" / "fixtures"

sys.path.insert(0, str(PROJECT_DIR))

from eval.metrics import (  # noqa: E402
    RAGEvalReport,
    evaluate_generation_case,
    evaluate_retrieval_case,
    format_report,
)
from core import build_vectorstore, load_documents, split_documents  # noqa: E402
from tests.conftest import MockUploadedFile  # noqa: E402


def load_eval_set(path: Path | None = None) -> dict:
    eval_path = path or EVAL_DIR / "rag_eval_set.json"
    return json.loads(eval_path.read_text(encoding="utf-8"))


def build_vectorstore_from_fixture(fixture_name: str, embeddings):
    fixture_path = FIXTURES_DIR / fixture_name
    uploaded = MockUploadedFile.from_path(fixture_path)
    documents = load_documents([uploaded])
    chunks = split_documents(documents)
    return build_vectorstore(chunks, embeddings, persist=False)


def run_retrieval_eval(vectorstore, eval_set: dict) -> RAGEvalReport:
    report = RAGEvalReport()
    k = eval_set.get("retrieval_k", 4)

    for case in eval_set["retrieval_cases"]:
        chunks = vectorstore.similarity_search(case["query"], k=k)
        result = evaluate_retrieval_case(case, chunks, k)
        report.retrieval_results.append(result)

    return report


def run_generation_eval(vectorstore, eval_set: dict, model: str, temperature: float) -> list:
    from langchain.chains import create_retrieval_chain
    from langchain.chains.combine_documents import create_stuff_documents_chain
    from langchain_core.prompts import ChatPromptTemplate
    from langchain_groq import ChatGroq

    from core import SYSTEM_PROMPT, get_groq_api_key

    api_key = get_groq_api_key()
    if not api_key:
        print("Skipping generation eval: GROQ_API_KEY not set.")
        return []

    k = eval_set.get("retrieval_k", 4)
    llm = ChatGroq(groq_api_key=api_key, model_name=model, temperature=temperature)
    prompt = ChatPromptTemplate.from_messages(
        [("system", SYSTEM_PROMPT), ("human", "{input}")]
    )
    document_chain = create_stuff_documents_chain(llm, prompt)
    retriever = vectorstore.as_retriever(search_kwargs={"k": k})
    chain = create_retrieval_chain(retriever, document_chain)

    results = []
    for case in eval_set.get("generation_cases", []):
        output = chain.invoke({"input": case["query"]})
        answer = output.get("answer", "")
        context = output.get("context", [])
        results.append(evaluate_generation_case(case, answer, context))

    return results


def main() -> int:
    parser = argparse.ArgumentParser(description="Run RAG evaluation benchmark.")
    parser.add_argument(
        "--with-llm",
        action="store_true",
        help="Include Groq generation eval (uses free-tier API quota).",
    )
    parser.add_argument(
        "--model",
        default="llama-3.3-70b-versatile",
        help="Groq model for generation eval.",
    )
    parser.add_argument(
        "--eval-set",
        type=Path,
        default=None,
        help="Path to eval JSON dataset (default: eval/rag_eval_set.json).",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Run all eval datasets in eval/ (rag_eval_set*.json).",
    )
    args = parser.parse_args()

    eval_paths = (
        sorted(EVAL_DIR.glob("rag_eval_set*.json"))
        if args.all
        else [args.eval_set or EVAL_DIR / "rag_eval_set.json"]
    )

    exit_code = 0
    for eval_path in eval_paths:
        print(f"\n{'=' * 60}\nEval set: {eval_path.name}\n{'=' * 60}")
        code = _run_single_eval(eval_path, args.with_llm, args.model)
        if code != 0:
            exit_code = code

    raise SystemExit(exit_code)


def _run_single_eval(eval_path: Path, with_llm: bool, model: str) -> int:
    eval_set = load_eval_set(eval_path)
    fixture = eval_set["fixture"]

    print(f"Loading fixture: {fixture}")
    from langchain_huggingface import HuggingFaceEmbeddings

    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    vectorstore = build_vectorstore_from_fixture(fixture, embeddings)

    report = run_retrieval_eval(vectorstore, eval_set)

    if with_llm:
        print("Running generation eval via Groq (free tier)...")
        report.generation_results = run_generation_eval(
            vectorstore, eval_set, model=model, temperature=0.2
        )

    print(format_report(report))

    thresholds = eval_set.get("pass_thresholds", {})
    failed = False

    if report.retrieval_pass_rate < thresholds.get("retrieval_pass_rate", 0.85):
        print("FAIL: retrieval pass rate below threshold.")
        failed = True
    if report.avg_keyword_recall < thresholds.get("avg_keyword_recall", 0.5):
        print("FAIL: avg keyword recall below threshold.")
        failed = True
    if report.avg_mrr < thresholds.get("avg_mrr", 0.5):
        print("FAIL: avg MRR below threshold.")
        failed = True
    if report.generation_results and report.generation_pass_rate < 1.0:
        print("FAIL: one or more generation eval cases failed.")
        failed = True

    if not failed:
        print("OVERALL: PASS")
        return 0

    print("OVERALL: FAIL")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
