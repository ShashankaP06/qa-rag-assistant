from pathlib import Path

import pytest


class MockUploadedFile:
    """Minimal stand-in for Streamlit UploadedFile in unit tests."""

    def __init__(self, name: str, content: bytes):
        self.name = name
        self.size = len(content)
        self._content = content

    def getvalue(self) -> bytes:
        return self._content

    @classmethod
    def from_text(cls, name: str, text: str) -> "MockUploadedFile":
        return cls(name, text.encode("utf-8"))

    @classmethod
    def from_path(cls, path: Path) -> "MockUploadedFile":
        return cls(path.name, path.read_bytes())


@pytest.fixture
def fixtures_dir() -> Path:
    return Path(__file__).parent / "fixtures"


@pytest.fixture
def minimal_prd_file(fixtures_dir: Path) -> MockUploadedFile:
    return MockUploadedFile.from_path(fixtures_dir / "minimal_prd.txt")


@pytest.fixture
def sample_markdown_table() -> str:
    return """\
Here is the test suite:

| Test ID | Component/Feature | Test Scenario | Pre-conditions | Execution Steps | Expected Result | Test Type (Positive/Negative) | Source Reference |
|---|---|---|---|---|---|---|---|
| TC-001 | Login | Valid login | User exists | Enter credentials | Success | Positive | Section 1 |
| TC-002 | Login | Invalid password | User exists | Enter wrong password | Error shown | Negative | Section 1 |
"""
