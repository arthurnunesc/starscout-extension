# Local Development

## Prerequisites

- Docker or a compatible Docker Compose runtime
- Node.js and pnpm
- Python 3.12
- `uv`

Install `uv` on macOS with:

```sh
brew install uv
```

## Start Postgres

```sh
docker compose --env-file .env.example -f infra/docker-compose.yml up -d
```

Check container health:

```sh
docker compose --env-file .env.example -f infra/docker-compose.yml ps
```

## Run Backend

```sh
cd backend
uv sync --dev
uv run uvicorn starscout_api.main:app --reload
```

Health check:

```sh
curl http://127.0.0.1:8000/health
```

Repo star integrity endpoint:

```sh
curl http://127.0.0.1:8000/repos/owner/repo/star-integrity
```

The endpoint returns analyzed aggregate metrics when `repo_aggregates` has a row for
the repo, uses GitHub REST metadata for current star counts, and returns a neutral
not-analyzed response when no aggregate exists.

Repo integrity responses are public-read and cacheable for the configured max age.
The backend applies a per-client rate limit and CORS only for GitHub, local dev, and
browser-extension origins. The API does not require user identity or extension IDs.

Run backend tests:

```sh
cd backend
uv run pytest
```

Run the importer skeleton against a restored StarScout MongoDB source:

```sh
cd backend
uv run python -m starscout_api.importer.cli
```

For the Phase 2 Postgres integration test, export a database DSN and run only the integration test file:

```sh
export TEST_POSTGRES_DSN="postgresql://starscout:starscout_dev_password@localhost:5432/starscout"
cd backend
uv run pytest tests/integration/importer/test_postgres_import.py
```

## Run Extension

```sh
cd extension
pnpm install
pnpm dev
```

Load the generated dev extension from WXT's output directory according to the WXT dev server instructions.
