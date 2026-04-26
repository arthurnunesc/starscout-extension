# Full Import Verification

## Dataset Restore

The StarScout MongoDB archive was restored from `mongodb.zip` at the repository root.
Only the importer-required suspicious-star collections were extracted and restored:

- `fake_stars.low_activity_stars`
- `fake_stars.clustered_stars`

Restore command:

```sh
unzip -o mongodb.zip "mongodb/fake_stars/low_activity_stars*" "mongodb/fake_stars/clustered_stars*"
docker compose --env-file .env.example -f infra/docker-compose.yml up -d
docker run --rm --network host -v "$PWD/mongodb:/dump" mongo:8-noble \
  mongorestore --gzip --drop --uri="mongodb://127.0.0.1:27017" /dump
```

Restore result:

- `82,458,891` MongoDB documents restored successfully
- `0` MongoDB documents failed to restore

## Import Report

Importer command:

```sh
cd backend
uv run python -m starscout_api.importer.cli
```

Importer result:

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

## Local API Verification

Health check:

```sh
curl http://127.0.0.1:8000/health
```

Response:

```json
{"status":"ok","service":"StarScout API"}
```

Known analyzed repository:

```sh
curl http://127.0.0.1:8000/repos/xai-org/grok-1/star-integrity
```

Response summary:

- `analyzed`: `true`
- `currentStars`: `51,527`
- `suspectedNonLegitStars`: `44,079`
- `estimatedLegitStars`: `7,448`
- `suspectedNonLegitPercent`: `85.55`
- `breakdown.lowActivity`: `908`
- `breakdown.lockstep`: `43,999`
- `breakdown.overlap`: `828`

Known not-analyzed repository:

```sh
curl http://127.0.0.1:8000/repos/octocat/Hello-World/star-integrity
```

Response summary:

- `analyzed`: `false`
- `suspectedNonLegitStars`: `null`
- `breakdown`: `null`
- warning: `Repository has no StarScout suspicious-star aggregate.`

## Extension Verification

The extension type-check passes with `pnpm compile`. Browser display verification still
requires loading the development extension and checking the badge/popover manually
against the local backend.
