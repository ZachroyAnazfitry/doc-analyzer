# Document Summarizer

A document summarization API with a simple web UI, built with FastAPI and a Hugging Face model. Docker-first development, CI/CD with GitHub Actions, and production deployment on AWS ECS—designed to stay within a small budget and follow MLOps practices.

[![CI](https://github.com/OWNER/doc-analyzer/actions/workflows/ci-cd.yml/badge.svg)](https://github.com/OWNER/doc-analyzer/actions)

---

## Problem statement

- **Need:** A way to summarize long documents via an API and a minimal UI, with a clear path from local development to production.
- **Constraints:** Use an existing open-source model (no custom training), keep infrastructure cost low (e.g. under ~$50/month for testing), and automate build, test, and deployment.
- **Goal:** One codebase, Docker-based dev and prod, and a simple MLOps-style pipeline (versioned images, automated deploy, observable version/model in the UI).

---

## Solution

- **API:** `POST /summarize` with `{"text": "..."}`; optional `max_length` / `min_length`. Returns `{"summary": "..."}`.
- **UI:** Single-page app (textarea + button) that calls the API and shows version and model name in the footer.
- **Model:** Configurable Hugging Face summarization model (default: `sshleifer/distilbart-cnn-6-6`), loaded once and reused.
- **Delivery:** Same Docker image for local (Compose) and production (ECR + ECS Fargate); CI on `develop`, CD on version tags (`v*`).

---

## Model capabilities and advantages

The default summarization model is **DistilBART-CNN** (`sshleifer/distilbart-cnn-6-6`): a distilled (smaller) version of BART fine-tuned on the CNN/DailyMail dataset for abstractive summarization.

**Capabilities**

- **Abstractive summarization** — Produces new sentences that capture the main ideas rather than copying phrases from the source. Good for articles, reports, and narrative text.
- **Configurable length** — You can control summary length via `min_length` and `max_length` (in tokens) in the API so outputs fit your use case (e.g. short bullets vs. longer paragraphs).
- **Longer inputs** — The API accepts long documents; the model truncates to the first ~4000 characters (and 1024 tokens) before summarization, so multi-paragraph articles are supported without failing.
- **Single model, no external API** — Everything runs in-process. No third-party summarization API or API keys; the model is loaded once at startup and reused for all requests.

**Advantages**

- **Smaller and faster than full BART** — Distillation reduces size and memory use while keeping reasonable quality, which helps stay within budget on ECS Fargate (e.g. 1–2 GB RAM) and allows CPU-only inference.
- **Open source and swappable** — The model is from Hugging Face; you can change `MODEL_NAME` in config (or env) to another summarization model without changing code.
- **Predictable cost and latency** — No per-call fees; cost is mainly compute (ECS). Latency is dominated by model load at startup and inference time, not network calls to external APIs.
- **Suitable for news and articles** — Trained on CNN/DailyMail, so it works well for news-style and article-style text; other domains may vary in quality.

For different trade-offs (e.g. more accuracy vs. speed), you can switch to another Hugging Face summarization model by setting the `MODEL_NAME` environment variable (see [Configuration](#configuration)).

---

## Tech stack and why

| Choice | Reason |
|--------|--------|
| **FastAPI** | Async-ready, automatic OpenAPI docs (`/docs`), simple to add health/version and model info. |
| **Hugging Face (transformers)** | Pre-trained summarization models, no training pipeline; swap models via config. |
| **Docker + docker-compose** | Reproducible dev and prod; same image in CI and ECS; align with "container-first" ML serving. |
| **GitHub Actions** | CI (lint, test, Docker build) and CD (build, push to ECR, deploy to ECS) in one place; no extra SaaS cost. |
| **AWS ECR** | Private container registry; required for ECS to pull images; pay-per-storage, low cost at small scale. |
| **AWS ECS (Fargate)** | Run the container without managing EC2; scale to one task; fits "single inference API" and budget. |
| **No SageMaker** | For a pre-trained, single-model API, ECS is simpler and cheaper; SageMaker is better later for training/pipelines. |

---

## Architecture

- **Development:** `docker-compose up` → single service (FastAPI + model); volume mount for live reload; env vars for `MODEL_NAME`, `MAX_LENGTH`, `MIN_LENGTH`.
- **Production:** Push Git tag `v*` → GitHub Actions builds image (with `APP_VERSION` = tag), pushes to ECR (ap-southeast-5), runs `aws ecs update-service --force-new-deployment`. ECS runs the same image; UI shows version and model from `/health`.

```
[Developer] → Git (feature → develop → main, tag v1.0.x)
       → GitHub Actions (CI on develop, CD on tag v*)
       → ECR (image: sha, latest, v1.0.x)
       → ECS Fargate (update-service)
[User] → Browser / Postman → ECS (FastAPI) → Model (in-process)
```

---

## MLOps practices applied

- **Reproducibility:** One Dockerfile; same image in dev and prod; dependencies and Python version fixed in the image.
- **Versioning:** Images tagged with Git SHA and semantic tag (e.g. `v1.0.1`); app exposes version (and model name) via `/health` and in the UI.
- **Config-driven model:** Model ID and lengths in env/config; change model without rebuilding code (e.g. ECS task def env or `.env`).
- **CI/CD:** Automated lint, test, and Docker build on `develop`; automated build, push, and ECS deploy on tag push; no manual deploy steps for releases.
- **Observability:** Health and version endpoints for load balancers and support; model name in UI for quick verification.

*(No training pipeline, model registry, or A/B testing in this project—focused on "serve one pre-trained model" with minimal MLOps.)*

---

## Cost estimation (AWS, testing)

| Resource | Typical usage | Rough monthly cost (ap-southeast-5) |
|----------|----------------|-------------------------------------|
| ECR | Few images, < 5 GB | < $5 |
| ECS Fargate | 1 task, 0.5 vCPU, 1–2 GB RAM, 24/7 | ~$15–35 |
| Data transfer | Low (API only) | < $5 |
| **Total** | | **~$25–50** (under $50 for light testing) |

Exact numbers depend on task size and hours; use [AWS Pricing Calculator](https://calculator.aws/) for your case.

---

## Getting started

### Prerequisites

- Docker and Docker Compose
- (Optional) Python 3.10+ and pip for local run without Docker

### Run with Docker (recommended)

```bash
git clone https://github.com/OWNER/doc-analyzer.git
cd doc-analyzer
docker-compose up --build
```

- App + UI: http://localhost:8001 (port 8001 to avoid conflict if 8000 is in use; edit `docker-compose.yml` to use `8000:8000` if you prefer)
- API docs: http://localhost:8001/docs
- Health: http://localhost:8001/health

Code in `app/` is mounted so changes apply with reload (no image rebuild).

### Run without Docker

```bash
python -m venv .venv
.venv\Scripts\activate   # Windows
# source .venv/bin/activate  # Linux/macOS
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

Optional: copy `.env.example` to `.env` and set `MODEL_NAME`, `MAX_LENGTH`, `MIN_LENGTH`.

### API examples

**Health check:**

```bash
curl http://localhost:8000/health
```

**Summarize:**

**POST** `/summarize` — Body (JSON):

```json
{
  "text": "Your long document text here...",
  "max_length": 130,
  "min_length": 30
}
```

`max_length` and `min_length` are optional (defaults from config/env).

```bash
curl -X POST http://localhost:8000/summarize \
  -H "Content-Type: application/json" \
  -d "{\"text\": \"Your document content to summarize here. It can be several sentences or paragraphs.\"}"
```

---

## Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `MODEL_NAME` | `sshleifer/distilbart-cnn-6-6` | Hugging Face summarization model |
| `MAX_LENGTH` | `130` | Max summary length (tokens) |
| `MIN_LENGTH` | `30` | Min summary length (tokens) |

---

## Deployment (production)

- **CI:** Runs on push/PR to `develop` (lint, test, Docker build).
- **CD:** Runs on **push of a tag `v*`** (e.g. `v1.0.1`): builds image with that version, pushes to ECR, runs ECS update-service.
- **Create a release:** From `main`, create tag `v1.0.1` (GitHub UI: Releases → Create new release → choose tag) or `git tag v1.0.1 && git push origin v1.0.1`.

See [docs/aws-deployment.md](docs/aws-deployment.md) for ECR, ECS, IAM, and GitHub secrets/variables.

---

## Problems faced and lessons learned

1. **Transformers pipeline removed** → `KeyError: Unknown task summarization`. **Lesson:** Use `AutoModelForSeq2SeqLM` + tokenizer instead of the deprecated pipeline; check library changelogs when upgrading.
2. **ECR push denied** → Wrong region (us-east-1 vs ap-southeast-5) and missing IAM (e.g. `ecr:InitiateLayerUpload`). **Lesson:** Align workflow region with ECR/ECS; give the deploy user explicit ECR + ECS permissions (correct resource ARNs: **ecs** for service, not ecr).
3. **ECS UpdateService denied** → IAM policy used cluster ARN and a typo (ecr vs ecs). **Lesson:** ECS actions need **service** ARN: `arn:aws:ecs:region:account:service/cluster-name/*`.
4. **Container OOM (exit 137)** → Task memory too low for the model. **Lesson:** Size Fargate task (e.g. 1–2 GB RAM) for model load + inference; start small and increase if needed.
5. **CI "No space left on device"** → Default PyPI `torch` pulls full CUDA stack. **Lesson:** Install CPU-only PyTorch in the Dockerfile (`--index-url https://download.pytorch.org/whl/cpu`) and omit `torch` from `requirements.txt` in the image build to keep CI and image size manageable.
6. **CD not running** → Expected on "merge to main"; actually CD was only on push to main, then switched to tag-only. **Lesson:** Document when CI and CD run (e.g. CI on develop, CD on tag); use tag-based releases for versioned, predictable deploys.

---

## Project structure

```
doc-analyzer/
├── .github/workflows/ci-cd.yml
├── app/
│   ├── main.py          # FastAPI app, /health, /summarize, serve UI
│   ├── model.py         # Load model, summarize()
│   ├── config.py        # MODEL_NAME, MAX_LENGTH, MIN_LENGTH
│   └── static/index.html
├── tests/
├── docs/aws-deployment.md
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md
```

---

## License

MIT
