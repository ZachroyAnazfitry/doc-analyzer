"""API tests using FastAPI TestClient; model is mocked to avoid loading HF in CI."""
from fastapi.testclient import TestClient

from app import model as model_module


def _fake_summarize(text: str, max_length: int | None = None, min_length: int | None = None) -> str:
    return "Summary of the document."


model_module.summarize = _fake_summarize
from app.main import app  # noqa: E402

client = TestClient(app)


def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


def test_summarize():
    r = client.post(
        "/summarize",
        json={"text": "Some long document content here."},
    )
    assert r.status_code == 200
    data = r.json()
    assert "summary" in data
    assert data["summary"] == "Summary of the document."


def test_summarize_with_options():
    r = client.post(
        "/summarize",
        json={"text": "Content.", "max_length": 50, "min_length": 10},
    )
    assert r.status_code == 200
    assert "summary" in r.json()
