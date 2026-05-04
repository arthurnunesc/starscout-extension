# Docker Compose Beta Deployment

## Overview

The beta deployment runs the FastAPI backend, Postgres serving database, and optional
MongoDB import-time service with Docker Compose on a VPS.

## Environment

Copy the deployment template and replace every placeholder secret before starting
services:

```sh
cp .env.deploy.example .env
```

Important variables:

- `POSTGRES_PASSWORD` must be a real secret, not the example value.
- `STARSCOUT_DATABASE_URL` must match the Postgres user, password, host, and database.
- `STARSCOUT_GITHUB_TOKEN` is optional but recommended to raise GitHub REST rate limits.
- `STARSCOUT_CORS_ALLOW_ORIGIN_REGEX` should allow GitHub and the dev-loaded extension origins only.
- `STARSCOUT_REPO_INTEGRITY_RATE_LIMIT_PER_MINUTE` controls public API abuse protection.
- `STARSCOUT_LOG_LEVEL` controls Uvicorn logging verbosity.

## Start Services

```sh
docker compose --env-file .env -f infra/docker-compose.yml up -d postgres mongo api
```

Check service health:

```sh
docker compose --env-file .env -f infra/docker-compose.yml ps
curl http://YOUR_HOST:8000/health
```

## Restore And Import Dataset

If you already imported the dataset locally, prefer the faster Postgres dump path
below. Use the Mongo restore/import path only when the VPS must perform the full
dataset import itself.

### Faster Path: Copy Local Postgres Export

On your local machine, export the already-imported serving database:

```sh
docker exec starscout-postgres pg_dump -U starscout -d starscout -Fc > starscout.dump
```

Copy the dump to the VPS repository root:

```sh
scp starscout.dump root@YOUR_VPS_IP:/root/real-github-stars-extension/
```

On the VPS, start Postgres and restore the dump:

```sh
docker compose --env-file .env -f infra/docker-compose.yml up -d postgres
docker compose --env-file .env -f infra/docker-compose.yml exec -T postgres \
  pg_restore -U starscout -d starscout --clean --if-exists < starscout.dump
```

Then start the API:

```sh
docker compose --env-file .env -f infra/docker-compose.yml up -d api
```

### Full Path: Restore Mongo And Run Importer

Place `mongodb.zip` on the VPS repository root, then restore the importer-required
collections:

```sh
unzip -o mongodb.zip "mongodb/fake_stars/low_activity_stars*" "mongodb/fake_stars/clustered_stars*"
docker run --rm --network host -v "$PWD/mongodb:/dump" mongo:8-noble \
  mongorestore --gzip --drop --uri="mongodb://127.0.0.1:${MONGO_PORT:-27017}" /dump
```

Run the importer inside the API container:

```sh
docker compose --env-file .env -f infra/docker-compose.yml run --rm api \
  uv run --no-dev python -m starscout_api.importer.cli
```

The importer bootstraps the required Postgres tables before writing facts and
aggregates. Re-running the same dataset is idempotent.

### Verified Full Import Result

The StarScout MongoDB archive was restored from `mongodb.zip` at the repository
root. Only the importer-required suspicious-star collections were extracted and
restored:

- `fake_stars.low_activity_stars`
- `fake_stars.clustered_stars`

Known restore result:

- `82,458,891` MongoDB documents restored successfully
- `0` MongoDB documents failed to restore

Known importer result:

- Source name: `starscout-mongodb`
- Source version: `2025-01-01`
- Low-activity source rows: `1,062,836`
- Lockstep source rows: `4,932,068`
- Deduped suspicious-star facts: `5,985,854`
- Repo aggregates: `26,640`
- Import status: `completed`

Top imported aggregate sample:

| Repo | Suspected | Low Activity | Lockstep | Overlap | Analyzed Through |
| --- | ---: | ---: | ---: | ---: | --- |
| `xai-org/grok-1` | `44,079` | `908` | `43,999` | `828` | `2025-01-01` |
| `sindresorhus/awesome` | `22,476` | `13,433` | `9,043` | `0` | `2025-01-01` |
| `lizongying/my-tv` | `20,537` | `674` | `20,281` | `418` | `2025-01-01` |
| `abi/screenshot-to-code` | `19,077` | `642` | `18,582` | `147` | `2025-01-01` |
| `charlax/professional-programming` | `18,905` | `358` | `18,736` | `189` | `2025-01-01` |

## API Verification

Health route:

```sh
curl http://YOUR_HOST:8000/health
```

Expected response:

```json
{"status":"ok","service":"StarScout API"}
```

Analyzed repository route:

```sh
curl http://YOUR_HOST:8000/repos/xai-org/grok-1/star-integrity
```

Expected response summary for the known full import:

- `analyzed`: `true`
- `currentStars`: `51,527`
- `suspectedNonLegitStars`: `44,079`
- `estimatedLegitStars`: `7,448`
- `suspectedNonLegitPercent`: `85.55`
- `breakdown.lowActivity`: `908`
- `breakdown.lockstep`: `43,999`
- `breakdown.overlap`: `828`

Not-analyzed repository route:

```sh
curl http://YOUR_HOST:8000/repos/octocat/Hello-World/star-integrity
```

Expected response summary:

- `analyzed`: `false`
- `suspectedNonLegitStars`: `null`
- `breakdown`: `null`
- Warning: `Repository has no StarScout suspicious-star aggregate.`

## Extension Verification

The extension type-check passes with `pnpm compile`. Browser display
verification still requires loading the development extension and checking the
badge and popover manually against the backend under test.

## Restart Behavior

Compose services use `restart: unless-stopped`, so containers restart after process
failure or VPS reboot unless intentionally stopped by an operator.

## Logging

The backend logs to stdout/stderr through Uvicorn. The VPS/container runtime owns
log rotation and retention; configure it to avoid long-lived per-user browsing
history. The API does not require user identity or extension identifiers.

Repository names are part of the API path, so API access logs and reverse-proxy
logs contain public `owner/repo` identifiers. Keep retention short and avoid
adding user identity or extension-specific IDs to logs.

## Extension Backend URL

Configure the dev-loaded extension to call the deployed backend by setting WXT's
public API URL before starting the extension dev server:

```sh
cd extension
WXT_PUBLIC_STARSCOUT_API_BASE_URL="https://YOUR_API_HOST" pnpm dev
```

For local development, use `pnpm dev`; that script injects
`WXT_PUBLIC_STARSCOUT_API_BASE_URL=http://127.0.0.1:8000`. The source fallback
URL is the production API.

## Package Dev-Loaded Extension

Build the Chrome MV3 zip with the deployed backend URL baked in:

```sh
cd extension
pnpm zip:beta
```

The generated package is written to:

```text
extension/.output/starscout-extension-0.1.2-chrome.zip
```

Share the zip with beta testers together with these instructions:

1. Unzip the package locally.
2. Open `chrome://extensions`.
3. Enable Developer mode.
4. Choose Load unpacked.
5. Select the unzipped extension directory.
6. Open a public GitHub repository page and verify the `StarScout` badge appears.

For Firefox, use `WXT_PUBLIC_STARSCOUT_API_BASE_URL="https://starscout-extension-api.arthurnun.es" pnpm zip:firefox`.

See [development.md](development.md#packaging) for tester install, update, and
uninstall guidance.
