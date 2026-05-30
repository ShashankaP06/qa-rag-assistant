"""
RAG evaluation metrics for the QA RAG Assistant.

All metrics run locally against retrieved chunks — no Groq API cost unless
you explicitly run generation eval (--with-llm).
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Iterable

STOPWORDS = {
    "a", "an", "the", "and", "or", "to", "of", "in", "for", "on", "is", "are",
    "be", "with", "must", "should", "that", "this", "it", "as", "at", "by",
    "from", "not", "can", "will", "their", "they", "user", "users", "test",
}


def normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", text.lower()).strip()


def chunk_texts(chunks: Iterable) -> list[str]:
    return [normalize_text(getattr(c, "page_content", str(c))) for c in chunks]


def keyword_in_text(keyword: str, text: str) -> bool:
    return normalize_text(keyword) in normalize_text(text)


def keyword_hit_at_k(chunks: list, expected_keywords: list[str]) -> bool:
    if not expected_keywords:
        return True
    texts = chunk_texts(chunks)
    return any(
        keyword_in_text(kw, text)
        for kw in expected_keywords
        for text in texts
    )


def keyword_recall_at_k(chunks: list, expected_keywords: list[str]) -> float:
    if not expected_keywords:
        return 1.0
    texts = chunk_texts(chunks)
    combined = " ".join(texts)
    hits = sum(1 for kw in expected_keywords if keyword_in_text(kw, combined))
    return hits / len(expected_keywords)


def mean_reciprocal_rank(chunks: list, expected_keywords: list[str]) -> float:
    if not expected_keywords:
        return 1.0
    texts = chunk_texts(chunks)
    for rank, text in enumerate(texts, start=1):
        if any(keyword_in_text(kw, text) for kw in expected_keywords):
            return 1.0 / rank
    return 0.0


def forbidden_keyword_absent(chunks: list, forbidden_keywords: list[str]) -> bool:
    if not forbidden_keywords:
        return True
    texts = chunk_texts(chunks)
    combined = " ".join(texts)
    return not any(keyword_in_text(kw, combined) for kw in forbidden_keywords)


def extract_content_tokens(text: str) -> set[str]:
    tokens = re.findall(r"[a-z0-9]+", normalize_text(text))
    return {t for t in tokens if t not in STOPWORDS and len(t) > 2}


def faithfulness_score(answer: str, context_chunks: list) -> float:
    """Fraction of answer tokens that appear in retrieved context (0–1)."""
    answer_tokens = extract_content_tokens(answer)
    if not answer_tokens:
        return 1.0
    context = " ".join(chunk_texts(context_chunks))
    context_tokens = extract_content_tokens(context)
    grounded = sum(1 for t in answer_tokens if t in context_tokens)
    return grounded / len(answer_tokens)


def mentions_insufficient_context(answer: str) -> bool:
    normalized = normalize_text(answer)
    return "insufficient context" in normalized


def forbidden_terms_in_answer(answer: str, forbidden_keywords: list[str]) -> list[str]:
    found = []
    for kw in forbidden_keywords:
        if keyword_in_text(kw, answer):
            found.append(kw)
    return found


@dataclass
class RetrievalEvalResult:
    case_id: str
    query: str
    case_type: str
    hit_at_k: bool
    keyword_recall: float
    mrr: float
    passed: bool
    detail: str = ""


@dataclass
class GenerationEvalResult:
    case_id: str
    query: str
    faithfulness: float
    insufficient_context: bool
    forbidden_in_answer: list[str]
    passed: bool
    answer_preview: str = ""


@dataclass
class RAGEvalReport:
    retrieval_results: list[RetrievalEvalResult] = field(default_factory=list)
    generation_results: list[GenerationEvalResult] = field(default_factory=list)

    @property
    def retrieval_pass_rate(self) -> float:
        if not self.retrieval_results:
            return 0.0
        return sum(1 for r in self.retrieval_results if r.passed) / len(self.retrieval_results)

    @property
    def avg_keyword_recall(self) -> float:
        if not self.retrieval_results:
            return 0.0
        return sum(r.keyword_recall for r in self.retrieval_results) / len(self.retrieval_results)

    @property
    def avg_mrr(self) -> float:
        if not self.retrieval_results:
            return 0.0
        return sum(r.mrr for r in self.retrieval_results) / len(self.retrieval_results)

    @property
    def generation_pass_rate(self) -> float:
        if not self.generation_results:
            return 0.0
        return sum(1 for g in self.generation_results if g.passed) / len(self.generation_results)

    @property
    def avg_faithfulness(self) -> float:
        if not self.generation_results:
            return 0.0
        return sum(g.faithfulness for g in self.generation_results) / len(self.generation_results)


def evaluate_retrieval_case(case: dict, chunks: list, k: int) -> RetrievalEvalResult:
    case_id = case["id"]
    query = case["query"]
    case_type = case.get("type", "retrieval_positive")

    expected = case.get("expected_keywords", [])
    forbidden = case.get("forbidden_in_context", [])

    hit = keyword_hit_at_k(chunks, expected)
    recall = keyword_recall_at_k(chunks, expected)
    mrr = mean_reciprocal_rank(chunks, expected)
    no_forbidden = forbidden_keyword_absent(chunks, forbidden)

    min_recall = case.get("min_keyword_recall", 0.5)

    if case_type == "retrieval_negative":
        passed = no_forbidden and not hit
        detail = "Context must not contain out-of-scope terms."
    else:
        passed = hit and recall >= min_recall and no_forbidden
        detail = f"Need hit@k + recall>={min_recall:.0%}."

    return RetrievalEvalResult(
        case_id=case_id,
        query=query,
        case_type=case_type,
        hit_at_k=hit,
        keyword_recall=recall,
        mrr=mrr,
        passed=passed,
        detail=detail,
    )


def evaluate_generation_case(case: dict, answer: str, context_chunks: list) -> GenerationEvalResult:
    faithfulness = faithfulness_score(answer, context_chunks)
    insufficient = mentions_insufficient_context(answer)
    forbidden = forbidden_terms_in_answer(answer, case.get("forbidden_in_answer", []))

    min_faithfulness = case.get("min_faithfulness", 0.3)
    expect_insufficient = case.get("expect_insufficient_context", False)

    if expect_insufficient:
        passed = insufficient and not forbidden
    else:
        passed = faithfulness >= min_faithfulness and not forbidden

    return GenerationEvalResult(
        case_id=case["id"],
        query=case["query"],
        faithfulness=faithfulness,
        insufficient_context=insufficient,
        forbidden_in_answer=forbidden,
        passed=passed,
        answer_preview=answer[:200],
    )


def format_report(report: RAGEvalReport) -> str:
    lines = [
        "=" * 60,
        "RAG EVALUATION REPORT",
        "=" * 60,
        "",
        "RETRIEVAL METRICS",
        f"  Pass rate:         {report.retrieval_pass_rate:.0%} "
        f"({sum(1 for r in report.retrieval_results if r.passed)}/{len(report.retrieval_results)})",
        f"  Avg keyword recall @k: {report.avg_keyword_recall:.0%}",
        f"  Mean reciprocal rank:  {report.avg_mrr:.3f}",
        "",
    ]

    for r in report.retrieval_results:
        status = "PASS" if r.passed else "FAIL"
        lines.append(
            f"  [{status}] {r.case_id} | hit={r.hit_at_k} recall={r.keyword_recall:.0%} "
            f"mrr={r.mrr:.2f} | {r.query[:50]}"
        )

    if report.generation_results:
        lines.extend([
            "",
            "GENERATION METRICS (LLM)",
            f"  Pass rate:         {report.generation_pass_rate:.0%}",
            f"  Avg faithfulness:  {report.avg_faithfulness:.0%}",
            "",
        ])
        for g in report.generation_results:
            status = "PASS" if g.passed else "FAIL"
            lines.append(
                f"  [{status}] {g.case_id} | faith={g.faithfulness:.0%} "
                f"insufficient={g.insufficient_context} | {g.query[:50]}"
            )

    lines.append("")
    lines.append("=" * 60)
    return "\n".join(lines)
