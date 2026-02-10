"""FastAPI app: health, summarize endpoint, and static UI."""
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from app.model import summarize

app = FastAPI(
    title="Document Summarizer API",
    description="Summarize documents using a Hugging Face model.",
    version="0.1.0",
)

# Mount static files for UI (after routes so / is overridable)
static_dir = Path(__file__).resolve().parent / "static"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")


class SummarizeRequest(BaseModel):
    """Request body for POST /summarize."""

    text: str = Field(..., min_length=1, description="Document text to summarize")
    max_length: int | None = Field(None, ge=10, le=250, description="Max summary length in tokens")
    min_length: int | None = Field(None, ge=5, le=250, description="Min summary length in tokens")


class SummarizeResponse(BaseModel):
    """Response for POST /summarize."""

    summary: str


@app.get("/health")
def health_check():
    """Health check for load balancers and monitoring."""
    return {"status": "ok"}


@app.get("/")
def root():
    """Serve the simple UI if present, else redirect to docs."""
    index = static_dir / "index.html"
    if index.exists():
        return FileResponse(index)
    return {"message": "Document Summarizer API", "docs": "/docs"}


@app.post("/summarize", response_model=SummarizeResponse)
def summarize_endpoint(body: SummarizeRequest):
    """Summarize the provided text."""
    summary = summarize(
        body.text,
        max_length=body.max_length,
        min_length=body.min_length,
    )
    return SummarizeResponse(summary=summary)
