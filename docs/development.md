# Development Guide

This guide is the entry point for running, packaging, deploying, and verifying the
project. The detailed task-specific docs stay linked from here so the main README can
focus on what StarScout Extension is.

## Prerequisites

- Docker or a compatible Docker Compose runtime
- Node.js and pnpm
- Python 3.12
- `uv`

On macOS, install `uv` with:

```sh
brew install uv
```

## Local Backend

Start Postgres and MongoDB:

```sh
docker compose --env-file .env.example -f infra/docker-compose.yml up -d postgres mongo
```

Restore the StarScout suspicious-star collections from `mongodb.zip`:

```sh
unzip -o mongodb.zip "mongodb/fake_stars/low_activity_stars*" "mongodb/fake_stars/clustered_stars*"
docker run --rm --network host -v "$PWD/mongodb:/dump" mongo:8-noble \
  mongorestore --gzip --drop --uri="mongodb://127.0.0.1:27017" /dump
```

Install backend dependencies, import data, and run the API:

```sh
cd backend
uv sync --dev
uv run python -m starscout_api.importer.cli
uv run uvicorn starscout_api.main:app --reload
```

Useful checks:

```sh
curl http://127.0.0.1:8000/health
curl http://127.0.0.1:8000/repos/xai-org/grok-1/star-integrity
curl http://127.0.0.1:8000/repos/octocat/Hello-World/star-integrity
```

See [local-dev.md](local-dev.md) and
[full-import-verification.md](full-import-verification.md) for more detail.

## Dev-Loaded Extension

Install extension dependencies and start WXT:

```sh
cd extension
pnpm install
pnpm dev
```

Load the generated WXT development extension in your browser. For local backend usage,
no extra configuration is required; the extension defaults to `http://127.0.0.1:8000`.

To point the dev-loaded extension at a deployed backend:

```sh
cd extension
WXT_PUBLIC_STARSCOUT_API_BASE_URL="https://YOUR_API_HOST" pnpm dev
```

## Deployment

Copy the deployment env template and replace placeholders:

```sh
cp .env.deploy.example .env
```

Start the Compose deployment on a VPS:

```sh
docker compose --env-file .env -f infra/docker-compose.yml up -d postgres mongo api
```

Deployment configuration includes Postgres, the optional MongoDB import-time service,
the FastAPI container, public API rate limiting, cache headers, restricted CORS, and
stdout/stderr logging.

See [deployment.md](deployment.md) for secrets, import, restart, logging, and
verification steps.

## Packaging

To package a Chrome dev-loaded beta zip:

```sh
cd extension
pnpm zip:beta
```

The zip is generated under `extension/.output/`. Unzip it, open
`chrome://extensions`, enable Developer mode, and load the unzipped directory.

See [beta-distribution.md](beta-distribution.md) for tester install, update,
uninstall, and public-release hygiene guidance.

## Verification

- Backend tests: `cd backend && uv run pytest`
- Backend lint: `cd backend && uv run ruff check .`
- Extension type-check: `cd extension && pnpm compile`
- Manual beta QA: [manual-qa.md](manual-qa.md)
