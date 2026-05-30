import os
from unittest.mock import patch

import pytest

from core import (
    GROQ_API_KEY_PLACEHOLDER,
    MAX_FILE_SIZE_BYTES,
    MAX_TOTAL_UPLOAD_BYTES,
    batch_hash_signature,
    friendly_api_error,
    get_groq_api_key,
    hash_bytes,
    load_index_metadata,
    parse_markdown_table,
    relevance_score,
    save_index_metadata,
    validate_uploads,
)
from tests.conftest import MockUploadedFile


class TestContentHash:
    def test_hash_bytes_is_deterministic(self):
        content = b"hello world"
        assert hash_bytes(content) == hash_bytes(content)

    def test_hash_changes_when_content_changes(self):
        file_a = MockUploadedFile.from_text("spec.txt", "version 1")
        file_b = MockUploadedFile.from_text("spec.txt", "version 2")
        assert hash_bytes(file_a.getvalue()) != hash_bytes(file_b.getvalue())

    def test_same_name_different_content_produces_different_signature(self):
        file_a = MockUploadedFile.from_text("spec.txt", "version 1")
        file_b = MockUploadedFile.from_text("spec.txt", "version 2")
        assert batch_hash_signature([file_a]) != batch_hash_signature([file_b])

    def test_same_content_produces_same_signature(self):
        file_a = MockUploadedFile.from_text("spec.txt", "same content")
        file_b = MockUploadedFile.from_text("spec.txt", "same content")
        assert batch_hash_signature([file_a]) == batch_hash_signature([file_b])


class TestGroqApiKey:
    def test_returns_none_for_placeholder(self):
        with patch.dict(os.environ, {"GROQ_API_KEY": GROQ_API_KEY_PLACEHOLDER}):
            assert get_groq_api_key() is None

    def test_returns_none_when_missing(self):
        with patch.dict(os.environ, {}, clear=True):
            assert get_groq_api_key() is None

    def test_strips_quotes_from_key(self):
        with patch.dict(os.environ, {"GROQ_API_KEY": '"gsk_test_key"'}):
            assert get_groq_api_key() == "gsk_test_key"

    def test_returns_valid_key(self):
        with patch.dict(os.environ, {"GROQ_API_KEY": "gsk_real_key"}):
            assert get_groq_api_key() == "gsk_real_key"


class TestFriendlyApiError:
    def test_rate_limit_error(self):
        msg = friendly_api_error(Exception("rate limit exceeded"))
        assert "rate limit" in msg.lower()

    def test_decommissioned_model(self):
        msg = friendly_api_error(Exception("model_decommissioned: llama3-70b-8192"))
        assert "no longer available" in msg.lower()

    def test_generic_error_includes_message(self):
        msg = friendly_api_error(ValueError("something broke"))
        assert "something broke" in msg


class TestMarkdownTableParser:
    def test_parses_valid_table(self, sample_markdown_table):
        df = parse_markdown_table(sample_markdown_table)
        assert df is not None
        assert len(df) == 2
        assert "Test ID" in df.columns
        assert df.iloc[0]["Test ID"] == "TC-001"

    def test_returns_none_for_plain_text(self):
        assert parse_markdown_table("No table here.") is None

    def test_handles_short_rows(self):
        text = (
            "| A | B | C |\n|---|---|---|\n| 1 | 2 |\n"
        )
        df = parse_markdown_table(text)
        assert df is not None
        assert df.iloc[0]["C"] == ""


class TestIndexMetadata:
    def test_save_and_load_roundtrip(self, tmp_path):
        metadata_path = tmp_path / "meta.json"
        files = [{"name": "spec.txt", "hash": "abc123", "size_kb": 1.0, "chunks": 3}]
        signature = (("spec.txt", "fullhash"),)

        save_index_metadata(files, signature, metadata_path=metadata_path)
        loaded = load_index_metadata(metadata_path=metadata_path)

        assert loaded is not None
        assert loaded["files"] == files
        assert loaded["signature"] == [list(signature[0])]

    def test_load_returns_none_for_missing_file(self, tmp_path):
        assert load_index_metadata(metadata_path=tmp_path / "missing.json") is None


class TestRelevanceScore:
    def test_lower_distance_means_higher_relevance(self):
        assert relevance_score(0.1) > relevance_score(0.9)

    def test_zero_distance_is_perfect(self):
        assert relevance_score(0.0) == 1.0


class TestUploadValidation:
    def test_rejects_unsupported_extension(self):
        bad = MockUploadedFile("spec.docx", b"content")
        valid, error = validate_uploads([bad])
        assert valid is False
        assert "Unsupported" in error

    def test_rejects_oversized_file(self):
        big = MockUploadedFile("big.txt", b"x" * (MAX_FILE_SIZE_BYTES + 1))
        valid, error = validate_uploads([big])
        assert valid is False
        assert "exceeds" in error

    def test_rejects_total_size_limit(self):
        chunk = 9 * 1024 * 1024  # 9 MB each — under per-file limit
        files = [
            MockUploadedFile("a.txt", b"x" * chunk),
            MockUploadedFile("b.txt", b"y" * chunk),
            MockUploadedFile("c.txt", b"z" * chunk),
        ]
        valid, error = validate_uploads(files)
        assert valid is False
        assert "Total upload" in error

    def test_accepts_valid_files(self, minimal_prd_file):
        valid, error = validate_uploads([minimal_prd_file])
        assert valid is True
        assert error == ""
