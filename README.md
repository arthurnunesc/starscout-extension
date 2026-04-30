# Real GitHub Stars Extension

Browser extension and backend API for showing StarScout-derived suspected non-legit
star signals on public GitHub repository pages.

This project is intentionally careful with wording: it shows heuristic suspected
signals, not definitive fake-star accusations. It does not claim that any specific
star, account, or repository is fake.

## What It Does

- Detects public `github.com/{owner}/{repo}` repository pages.
- Sends only the public `owner/repo` name to the backend.
- Shows a compact neutral `StarScout` badge near GitHub's native star control.
- Opens a popover with aggregate suspected-star metrics, current GitHub stars,
  estimated legitimate stars, warnings, dataset cutoff, and attribution.
- Uses the StarScout Zenodo MongoDB dump imported into Postgres as aggregate-only
  serving data.

## What It Does Not Claim

- It does not prove that stars are fake.
- It does not prove that remaining stars are legitimate.
- It does not expose suspected actor identities.
- It does not support private repositories or GitHub Enterprise Server.
- It does not replace GitHub's native star count.

## Project Layout

- `backend/` - FastAPI backend and importer managed with `uv`.
- `extension/` - WXT + React browser extension.
- `infra/` - Docker Compose infrastructure.
- `docs/` - Architecture, environment, local development, deployment, QA, and attribution notes.
- `plans/` - Implementation plan and acceptance criteria.

## Local Backend Setup

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

Install backend dependencies and run the importer/API:

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

See `docs/local-dev.md` and `docs/full-import-verification.md` for details.

## Deployed Backend Setup

Copy the deployment env template and replace placeholders:

```sh
cp .env.deploy.example .env
```

Start the Compose deployment on a VPS:

```sh
docker compose --env-file .env -f infra/docker-compose.yml up -d postgres mongo api
```

Deployment configuration includes:

- Postgres serving database.
- Optional MongoDB import-time service.
- FastAPI API container.
- Public read API rate limiting.
- Cache headers.
- CORS restricted to GitHub and browser-extension origins.
- Uvicorn stdout/stderr logging.

See `docs/deployment.md` for secrets, import, restart, logging, and verification steps.

## Dev-Loaded Extension Setup

Install dependencies and start WXT:

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

## Privacy Posture

- The extension sends only the public `owner/repo` identifier to the backend.
- The extension does not send user identity, GitHub credentials, extension-specific user IDs,
  or private repository data.
- The backend returns aggregate repo-level metrics only.
- The public API is read-only and rate-limited.
- Operational logs should avoid long-lived per-user browsing history.

## Attribution

This project uses StarScout-derived data and methodology.

- StarScout repository: https://github.com/hehao98/StarScout
- Zenodo replication package DOI: https://doi.org/10.5281/zenodo.17009694
- Paper: Hao He, Haoqin Yang, Philipp Burckhardt, Alexandros Kapravelos,
  Bogdan Vasilescu, and Christian Kaestner. 2026. Six Million (Suspected) Fake
  Stars on GitHub: A Growing Spiral of Popularity Contests, Spam, and Malware.
  ICSE 2026.

See `docs/attribution.md`.

## Known Limitations

- Supports public `github.com/{owner}/{repo}` repository pages only.
- Does not support private repositories.
- Does not support GitHub Enterprise Server.
- Does not show actor-level suspected stargazer evidence.
- Results are bounded by the StarScout dataset cutoff, currently `2025-01-01`.
- Missing aggregate data is shown as not analyzed, not as zero suspected stars.
- Browser store publication is out of scope for the dev-loaded beta.

## Verification

- Backend tests: `cd backend && uv run pytest`
- Backend lint: `cd backend && uv run ruff check .`
- Extension type-check: `cd extension && pnpm compile`
- Manual beta QA: see `docs/manual-qa.md`
