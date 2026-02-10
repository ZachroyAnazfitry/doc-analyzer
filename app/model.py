"""Load Hugging Face summarization model and expose summarize()."""
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer

from app.config import MAX_LENGTH, MIN_LENGTH, MODEL_NAME

_model = None
_tokenizer = None


def _get_model_and_tokenizer():
    """Load model and tokenizer once at startup; reuse on every request."""
    global _model, _tokenizer
    if _model is None:
        _tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
        _model = AutoModelForSeq2SeqLM.from_pretrained(MODEL_NAME)
    return _model, _tokenizer


def summarize(
    text: str,
    max_length: int | None = None,
    min_length: int | None = None,
) -> str:
    """Summarize input text. Truncate to model max if needed."""
    model, tokenizer = _get_model_and_tokenizer()
    max_len = max_length if max_length is not None else MAX_LENGTH
    min_len = min_length if min_length is not None else MIN_LENGTH
    # Truncate to avoid exceeding model max input length (e.g. 1024)
    inputs = tokenizer(
        text[:4000],
        max_length=1024,
        truncation=True,
        return_tensors="pt",
    )
    outputs = model.generate(
        **inputs,
        max_length=max_len,
        min_length=min_len,
        do_sample=False,
        length_penalty=2.0,
        num_beams=4,
    )
    summary = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return summary.strip()