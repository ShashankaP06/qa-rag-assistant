import pytest
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import AIMessage
from langchain_core.outputs import ChatGeneration, ChatResult

from core import DEFAULT_RETRIEVAL_K, SYSTEM_PROMPT, QUICK_ACTIONS


class FakeChatModel(BaseChatModel):
    def _generate(self, messages, stop=None, run_manager=None, **kwargs):
        return ChatResult(
            generations=[
                ChatGeneration(
                    message=AIMessage(
                        content=(
                            "| Test ID | Component/Feature | Test Scenario | Pre-conditions | "
                            "Execution Steps | Expected Result | Test Type (Positive/Negative) | "
                            "Source Reference |\n"
                            "| TC-001 | Login | Valid login | User exists | Login | Success | "
                            "Positive | Section 1 |"
                        )
                    )
                )
            ]
        )

    @property
    def _llm_type(self) -> str:
        return "fake"


@pytest.mark.slow
class TestRetrievalChain:
    def test_chain_returns_mocked_answer_with_context(self, minimal_prd_file):
        pytest.importorskip("langchain_huggingface")
        from langchain.chains import create_retrieval_chain
        from langchain.chains.combine_documents import create_stuff_documents_chain
        from langchain_core.prompts import ChatPromptTemplate
        from langchain_huggingface import HuggingFaceEmbeddings

        from core import build_vectorstore, load_documents, split_documents

        docs = load_documents([minimal_prd_file])
        chunks = split_documents(docs)
        embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        vectorstore = build_vectorstore(chunks, embeddings, persist=False)

        prompt = ChatPromptTemplate.from_messages(
            [("system", SYSTEM_PROMPT), ("human", "{input}")]
        )
        document_chain = create_stuff_documents_chain(FakeChatModel(), prompt)
        retriever = vectorstore.as_retriever(search_kwargs={"k": DEFAULT_RETRIEVAL_K})
        chain = create_retrieval_chain(retriever, document_chain)

        query = QUICK_ACTIONS["Generate Functional Test Cases Matrix"]
        result = chain.invoke({"input": query})

        assert "answer" in result
        assert "context" in result
        assert len(result["context"]) > 0
        assert "TC-001" in result["answer"]
