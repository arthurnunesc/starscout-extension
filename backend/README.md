# StarScout API

FastAPI backend for the StarScout-based GitHub star integrity extension.

## Local Development

Install `uv`, then run:

```sh
uv sync --dev
uv run uvicorn starscout_api.main:app --reload
```

Health check:

```sh
curl http://127.0.0.1:8000/health
```

Tests:

```sh
uv run pytest
```

Phase 2 importer skeleton:

```sh
uv run python -m starscout_api.importer.cli
```

The importer expects a restored StarScout MongoDB dataset and a reachable Postgres database. See the root docs for environment variables and local service setup.
