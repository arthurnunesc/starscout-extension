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

Never commit real credentials. Use `.env.example` files as safe templates only.
