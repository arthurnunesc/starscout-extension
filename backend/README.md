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
