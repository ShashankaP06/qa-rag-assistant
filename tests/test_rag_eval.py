import json
from pathlib import Path

import pytest

from eval.metrics import (
    RAGEvalReport,
    evaluate_generation_case,
    evaluate_retrieval_case,
    faithfulness_score,
    keyword_hit_at_k,
    keyword_recall_at_k,
    mean_reciprocal_rank,
    mentions_insufficient_context,
)
from langchain_core.documents import Document

EVAL_SET_PATH = Path(__file__).parent.parent / "eval" / "rag_eval_set.json"


class TestMetricFunctions:
    def test_hit_at_k_finds_keyword(self):
        chunks = [Document(page_content="Maximum login attempts: 3")]
        assert keyword_hit_at_k(chunks, ["3", "login"]) is True

    def test_hit_at_k_misses_keyword(self):
        chunks = [Document(page_content="Search module only")]
        assert keyword_hit_at_k(chunks, ["payment"]) is False

    def test_keyword_recall_partial(self):
        chunks = [Document(page_content="Password must be 8 characters")]
        recall = keyword_recall_at_k(chunks, ["8 characters", "password", "missing"])
        assert recall == pytest.approx(2 / 3)

    def test_mrr_first_rank(self):
        chunks = [
            Document(page_content="Unrelated"),
            Document(page_content="Login attempts limited to 3"),
        ]
        assert mean_reciprocal_rank(chunks, ["3"]) == 0.5

    def test_faithfulness_grounded_answer(self):
        context = [Document(page_content="Maximum login attempts: 3")]
        answer = "Verify account locks after 3 login attempts."
        score = faithfulness_score(answer, context)
        assert score >= 0.3

    def test_insufficient_context_detection(self):
        assert mentions_insufficient_context("Expected Result: Insufficient context") is True


@pytest.mark.slow
class TestRAGRetrievalEval:
    @pytest.fixture(scope="class")
    def eval_vectorstore(self):
        pytest.importorskip("langchain_huggingface")
        from langchain_huggingface import HuggingFaceEmbeddings

        from core import build_vectorstore, load_documents, split_documents
        from tests.conftest import MockUploadedFile

        eval_set = json.loads(EVAL_SET_PATH.read_text(encoding="utf-8"))
        fixture_path = Path(__file__).parent / "fixtures" / eval_set["fixture"]
        uploaded = MockUploadedFile.from_path(fixture_path)
        docs = load_documents([uploaded])
        chunks = split_documents(docs)
        embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        return build_vectorstore(chunks, embeddings, persist=False), eval_set

    def test_retrieval_benchmark_meets_thresholds(self, eval_vectorstore):
        vectorstore, eval_set = eval_vectorstore
        k = eval_set["retrieval_k"]
        thresholds = eval_set["pass_thresholds"]

        report = RAGEvalReport()
        for case in eval_set["retrieval_cases"]:
            chunks = vectorstore.similarity_search(case["query"], k=k)
            report.retrieval_results.append(evaluate_retrieval_case(case, chunks, k))

        assert report.retrieval_pass_rate >= thresholds["retrieval_pass_rate"], (
            f"Retrieval pass rate {report.retrieval_pass_rate:.0%} below "
            f"{thresholds['retrieval_pass_rate']:.0%}. "
            f"Failed: {[r.case_id for r in report.retrieval_results if not r.passed]}"
        )
        assert report.avg_keyword_recall >= thresholds["avg_keyword_recall"]
        assert report.avg_mrr >= thresholds["avg_mrr"]

    def test_negative_cases_do_not_retrieve_hallucinated_topics(self, eval_vectorstore):
        vectorstore, eval_set = eval_vectorstore
        k = eval_set["retrieval_k"]
        negative_cases = [
            c for c in eval_set["retrieval_cases"]
            if c["type"] == "retrieval_negative"
        ]

        for case in negative_cases:
            chunks = vectorstore.similarity_search(case["query"], k=k)
            result = evaluate_retrieval_case(case, chunks, k)
            assert result.passed, (
                f"{case['id']} failed: out-of-scope content retrieved for '{case['query']}'"
            )


class TestGenerationEvalLogic:
    def test_insufficient_context_case_passes_without_llm(self):
        case = {
            "id": "GEN-NEG",
            "query": "payment gateway tests",
            "expect_insufficient_context": True,
            "forbidden_in_answer": ["credit card"],
        }
        answer = "Insufficient context in the document for payment features."
        context = [Document(page_content="Login module only.")]
        result = evaluate_generation_case(case, answer, context)
        assert result.passed is True

    def test_hallucinated_answer_fails(self):
        case = {
            "id": "GEN-BAD",
            "query": "payment tests",
            "forbidden_in_answer": ["stripe", "payment gateway"],
        }
        answer = "TC-001: Test Stripe payment gateway integration."
        context = [Document(page_content="Login only.")]
        result = evaluate_generation_case(case, answer, context)
        assert result.passed is False
        assert "stripe" in result.forbidden_in_answer or "payment gateway" in result.forbidden_in_answer


@pytest.mark.groq
@pytest.mark.slow
class TestRAGGenerationEvalLive:
    """Optional live Groq eval — skipped unless GROQ_API_KEY is set."""

    def test_live_generation_eval(self):
        import os

        from dotenv import load_dotenv

        load_dotenv(Path(__file__).parent.parent / ".env", override=True)
        from core import get_groq_api_key

        if not get_groq_api_key():
            pytest.skip("GROQ_API_KEY not set — skipping live generation eval.")

        from eval.run_eval import build_vectorstore_from_fixture, load_eval_set, run_generation_eval
        from langchain_huggingface import HuggingFaceEmbeddings

        eval_set = load_eval_set()
        embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        vectorstore = build_vectorstore_from_fixture(eval_set["fixture"], embeddings)

        results = run_generation_eval(
            vectorstore, eval_set, model="llama-3.3-70b-versatile", temperature=0.2
        )
        assert results, "No generation cases configured."
        pass_rate = sum(1 for r in results if r.passed) / len(results)
        assert pass_rate >= 0.5, (
            f"Live generation pass rate {pass_rate:.0%}. "
            f"Failed: {[r.case_id for r in results if not r.passed]}"
        )
