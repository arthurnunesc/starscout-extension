# Architecture

## V1 Shape

The v1 product is a dev-loaded browser extension backed by a hosted FastAPI API.

The extension detects public `github.com/{owner}/{repo}` pages, sends only the public repo identity to the backend, and displays a compact neutral badge with a suspected non-legit star percentage.

The backend is responsible for data correctness. It imports StarScout's Zenodo MongoDB dump, dedupes suspicious stars by `repo + actor + starred_at`, stores aggregate repo-level metrics in Postgres, fetches current GitHub star counts, and returns aggregate-only responses.

## Boundaries

- The extension is UI-only and does not compute StarScout heuristics.
- The API exposes aggregates only and never exposes suspected actor identities.
- Postgres is the serving database.
- The restored MongoDB dump is an import source, not the public serving database.
- GitHub's current `stargazers_count` is the denominator for displayed percentages.

## Current Phase

Phase 1 establishes the monorepo, backend health route, WXT scaffold, local Postgres, and documentation. It deliberately does not add importer logic, schemas, migrations, or StarScout dataset processing yet.

## Next steps

1. Get the computational resources to run the StarScout detector to refresh the data.
