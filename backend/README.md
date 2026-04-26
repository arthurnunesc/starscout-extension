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

Repo star integrity API:

```sh
curl http://127.0.0.1:8000/repos/owner/repo/star-integrity
```

The Phase 3 API reads aggregate suspicious-star metrics from Postgres and returns only
repo-level counts. It does not expose suspected actor identities.

Tests:

```sh
uv run pytest
```

Phase 2 importer skeleton:

```sh
uv run python -m starscout_api.importer.cli
```

The importer expects a restored StarScout MongoDB dataset and a reachable Postgres database. See the root docs for environment variables and local service setup.
