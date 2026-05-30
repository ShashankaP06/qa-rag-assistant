import pytest

from core import (
    CHUNK_OVERLAP,
    CHUNK_SIZE,
    build_indexed_file_records,
    build_vectorstore,
    load_documents,
    split_documents,
)
from tests.conftest import MockUploadedFile


class TestDocumentIngestion:
    def test_load_txt_document(self, minimal_prd_file):
        docs = load_documents([minimal_prd_file])
        assert len(docs) >= 1
        assert "Login Module" in docs[0].page_content
        assert docs[0].metadata["original_filename"] == "minimal_prd.txt"

    def test_whitespace_only_txt_still_loads_as_document(self):
        empty_file = MockUploadedFile.from_text("empty.txt", "   \n  ")
        docs = load_documents([empty_file])
        assert len(docs) == 1
        assert docs[0].page_content.strip() == ""

    def test_chunk_count_for_minimal_prd(self, minimal_prd_file):
        docs = load_documents([minimal_prd_file])
        chunks = split_documents(docs)
        assert len(chunks) >= 1
        for chunk in chunks:
            assert len(chunk.page_content) <= CHUNK_SIZE + 100

    def test_build_indexed_file_records(self, minimal_prd_file):
        docs = load_documents([minimal_prd_file])
        chunks = split_documents(docs)
        records = build_indexed_file_records([minimal_prd_file], chunks)

        assert len(records) == 1
        assert records[0]["name"] == "minimal_prd.txt"
        assert records[0]["chunks"] == len(chunks)
        assert len(records[0]["hash"]) == 12


@pytest.mark.slow
class TestVectorstore:
    def test_build_in_memory_vectorstore_and_retrieve(self, minimal_prd_file):
        pytest.importorskip("langchain_huggingface")
        from langchain_huggingface import HuggingFaceEmbeddings

        docs = load_documents([minimal_prd_file])
        chunks = split_documents(docs)
        embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

        vectorstore = build_vectorstore(
            chunks,
            embeddings,
            persist=False,
        )

        results = vectorstore.similarity_search("login attempts", k=2)
        assert len(results) >= 1
        assert any("login" in doc.page_content.lower() for doc in results)
