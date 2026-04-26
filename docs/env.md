# Environment Variables

## Root `.env`

Used by Docker Compose.

- `POSTGRES_DB` - local Postgres database name.
- `POSTGRES_USER` - local Postgres username.
- `POSTGRES_PASSWORD` - local Postgres password. Use a real secret outside local development.
- `POSTGRES_PORT` - host port for local Postgres.

## Backend `.env`

All backend variables use the `STARSCOUT_` prefix.

- `STARSCOUT_APP_NAME` - FastAPI app title.
- `STARSCOUT_APP_VERSION` - API version string.
- `STARSCOUT_ENABLE_DOCS` - enables `/docs` and `/redoc` locally.
- `STARSCOUT_DATABASE_URL` - Postgres connection string.
- `STARSCOUT_MONGODB_URL` - MongoDB connection string for the restored StarScout source dataset.
- `STARSCOUT_MONGODB_DATABASE` - MongoDB database name containing the restored StarScout collections.
- `STARSCOUT_ANALYZED_THROUGH` - dataset cutoff date used by the importer and future aggregates.
- `STARSCOUT_GITHUB_TOKEN` - optional GitHub token for higher REST API rate limits.
- `STARSCOUT_GITHUB_REPO_CACHE_TTL_SECONDS` - number of seconds to reuse cached GitHub repository metadata.

## Test-only Environment Variables

- `TEST_POSTGRES_DSN` - explicit Postgres DSN for the Phase 2 integration test.

Never commit real credentials. Use `.env.example` files as safe templates only.
