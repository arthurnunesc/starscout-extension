# Real GitHub Stars Extension

Browser extension and backend API for showing StarScout-derived suspected non-legit star signals on public GitHub repository pages.

This project is intentionally careful with wording: it shows heuristic suspected signals, not definitive fake-star accusations.

## Project Layout

- `backend/` - FastAPI backend managed with `uv`.
- `extension/` - WXT + React browser extension.
- `infra/` - Local and deployment infrastructure.
- `docs/` - Architecture, environment, local development, and attribution notes.
- `plans/` - Implementation plan and actionable phases.

## Local Quick Start

Start local Postgres:

```sh
docker compose --env-file .env.example -f infra/docker-compose.yml up -d
```

Run the backend:

```sh
cd backend
uv sync --dev
uv run uvicorn starscout_api.main:app --reload
```

Run the extension dev server:

```sh
cd extension
pnpm install
pnpm dev
```

See `docs/local-dev.md` for details.
