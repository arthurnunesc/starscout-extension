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

## Local Services

Start the local services:

```sh
docker compose --env-file .env.example -f infra/docker-compose.yml up -d
```

Check container health:

```sh
docker compose --env-file .env.example -f infra/docker-compose.yml ps
```

## Local Backend

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

The repo star integrity endpoint returns analyzed aggregate metrics when
`repo_aggregates` has a row for the repo, uses GitHub REST metadata for current
star counts, and returns a neutral not-analyzed response when no aggregate
exists.

Repo integrity responses are public-read and cacheable for the configured max
age. The backend applies a per-client rate limit and CORS only for GitHub, local
dev, and browser-extension origins. The API does not require user identity or
extension IDs.

Run backend tests:

```sh
cd backend
uv run pytest
```

Run the importer against a restored StarScout MongoDB source:

```sh
cd backend
uv run python -m starscout_api.importer.cli
```

For the Phase 2 Postgres integration test, export a database DSN and run only
the integration test file:

```sh
export TEST_POSTGRES_DSN="postgresql://starscout:starscout_dev_password@localhost:5432/starscout"
cd backend
uv run pytest tests/integration/importer/test_postgres_import.py
```

See [deployment.md](deployment.md#verified-full-import-result) for full import
verification details.

## Dev-Loaded Extension

Install extension dependencies and start WXT:

```sh
cd extension
pnpm install
pnpm dev
```

Load the generated WXT development extension in your browser. For local backend usage,
`pnpm dev` injects `WXT_PUBLIC_STARSCOUT_API_BASE_URL=http://127.0.0.1:8000`.

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

### Chrome Web Store Release

To build the production zip intended for Chrome Web Store updates:

```sh
cd extension
pnpm zip
```

This command:
- Uses the production fallback API URL, `https://starscout-extension-api.arthurnun.es`
- Generates a Chrome MV3 zip under `extension/.output/`

The source fallback API URL is also `https://starscout-extension-api.arthurnun.es`;
local development uses the dev script's injected URL.

After generating the zip, inspect the packaged manifest and bundled code for
local-only URLs such as `localhost` or `127.0.0.1` before uploading.

The exact generated zip path is:
`extension/.output/starscout-extension-<version>-chrome.zip`

Before submitting a Store update, run the verification checklist:

```sh
cd backend
uv run pytest
uv run ruff check .

cd ../extension
pnpm compile
pnpm zip
```

Then manually verify the scenarios in [manual-qa.md](manual-qa.md).

Public release hygiene:

- Do not commit `.env` files, generated zips, database dumps, or StarScout data
  dumps.
- Do not distribute the imported Postgres database unless source-data licensing
  and redistribution terms are confirmed.
- Keep public wording neutral: suspected non-legit star signal, not proof of fake
  stars.
- Keep the Store listing, privacy notice, and GitHub Issues support link current.

## Verification

- Backend tests: `cd backend && uv run pytest`
- Backend lint: `cd backend && uv run ruff check .`
- Extension type-check: `cd extension && pnpm compile`
- Manual QA: [manual-qa.md](manual-qa.md)
