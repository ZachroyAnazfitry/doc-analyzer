# Document Summarizer

Document summarization API and simple web UI, using a Hugging Face model. Docker-first development; deployable to AWS ECS.

## Run locally with Docker (recommended)

```bash
docker-compose up --build
```

- API and UI: <http://localhost:8001> (port 8001 to avoid conflict if 8000 is in use; edit `docker-compose.yml` to use `8000:8000` if you prefer)
- Interactive API docs: <http://localhost:8001/docs>
- Health: <http://localhost:8001/health>

Code in `app/` is mounted so changes apply with reload (no image rebuild).

## Run without Docker

```bash
python -m venv .venv
.venv\Scripts\activate   # Windows
# source .venv/bin/activate  # Linux/macOS
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

Optional: copy `.env.example` to `.env` and set `MODEL_NAME`, `MAX_LENGTH`, `MIN_LENGTH`.

## API

### Health check

```bash
curl http://localhost:8000/health
```

### Summarize

**POST** `/summarize`  
Body (JSON):

```json
{
  "text": "Your long document text here...",
  "max_length": 130,
  "min_length": 30
}
```

`max_length` and `min_length` are optional (defaults from config/env).

**Example (curl):**

```bash
curl -X POST http://localhost:8000/summarize \
  -H "Content-Type: application/json" \
  -d "{\"text\": \"Your document content to summarize here. It can be several sentences or paragraphs.\"}"
```

**Example (Postman):**  
Method: POST, URL: `http://localhost:8000/summarize`, Body: raw JSON as above.

## Configuration

| Variable     | Default                       | Description                    |
|-------------|-------------------------------|--------------------------------|
| `MODEL_NAME`| `sshleifer/distilbart-cnn-6-6`| Hugging Face summarization model |
| `MAX_LENGTH`| `130`                         | Max summary length (tokens)   |
| `MIN_LENGTH`| `30`                          | Min summary length (tokens)   |

## AWS deployment (ECS)

See [docs/aws-deployment.md](docs/aws-deployment.md) for ECR, ECS Fargate, and optional GitHub Actions CD.

## License

MIT
