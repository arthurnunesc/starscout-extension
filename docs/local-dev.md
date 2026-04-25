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

Run backend tests:

```sh
cd backend
uv run pytest
```

## Run Extension

```sh
cd extension
pnpm install
pnpm dev
```

Load the generated dev extension from WXT's output directory according to the WXT dev server instructions.
