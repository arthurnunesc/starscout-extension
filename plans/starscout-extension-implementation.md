# Plan: StarScout-Based GitHub Star Integrity Extension

> Source PRD: `PRD.md`

## Technical Decisions

- **Product promise**: Show a heuristic suspected non-legit star signal, not a definitive fake-star or legitimate-star judgment.
- **Primary user**: Developers browsing public GitHub repositories.
- **Supported surface**: Public `github.com/{owner}/{repo}` repository pages only for v1.
- **Extension stack**: WXT + React.
- **Backend stack**: Python FastAPI managed with `uv`.
- **Serving database**: Postgres.
- **Source dataset**: StarScout Zenodo MongoDB dump, restored before v1.
- **Deduplication key**: `repo + actor + starred_at` across low-activity and clustered StarScout collections.
- **Public data exposure**: Aggregate repo-level metrics only; no public suspected actor lists.
- **Current star denominator**: Backend fetches and caches GitHub REST `stargazers_count`.
- **Missing repo behavior**: Show "not found/analyzed," never `0% suspected`.
- **Count mismatch behavior**: Clamp estimated legitimate stars to zero and return a data-quality warning.
- **API access**: Public read-only API with rate limiting.
- **Privacy posture**: Extension sends only public repo identity; backend keeps minimal operational logs.
- **Deployment target**: Docker Compose on a VPS.
- **Distribution target**: Dev-loaded beta first, not browser stores.
- **Attribution**: Visible StarScout, paper, and Zenodo attribution in UI/docs.
- **Testing focus**: Backend tests for v1; extension verification is manual initially.

## Durable API Contract

- **Health route**: `GET /health`
- **Repo integrity route**: `GET /repos/{owner}/{repo}/star-integrity`
- **Success response fields**:
  - `repo`: canonical `owner/repo` string
  - `githubRepoId`: GitHub numeric repository ID when available
  - `currentStars`: current GitHub star count
  - `suspectedNonLegitStars`: deduped suspicious star count
  - `estimatedLegitStars`: `max(currentStars - suspectedNonLegitStars, 0)`
  - `suspectedNonLegitPercent`: percentage using current GitHub stars as denominator
  - `breakdown.lowActivity`: low-activity suspicious count
  - `breakdown.lockstep`: lockstep suspicious count
  - `breakdown.overlap`: count detected by both heuristics
  - `analyzedThrough`: StarScout dataset cutoff date
  - `dataSource`: StarScout/Zenodo metadata
  - `warnings`: list of data-quality warnings
- **Not analyzed response**: A structured response that states the repo has no StarScout suspicious-star record, without implying zero suspected stars.
- **Error responses**: Structured errors for invalid repo name, unsupported host, GitHub lookup failure, rate limit, and backend failures.

## Durable Data Model

- **Repository identity**: Store StarScout repo name, current canonical GitHub full name, GitHub repo ID, GitHub node ID, and timestamps for metadata refresh.
- **Suspicious star fact**: Store one row per deduped `repo + actor + starred_at` with boolean flags for low-activity and lockstep membership.
- **Repo aggregate**: Store precomputed counts per repo for total suspected, low-activity, lockstep, overlap, and analyzed-through cutoff.
- **GitHub star cache**: Store current star count, fetch timestamp, and lookup status.
- **Import run**: Store source dataset version, started/completed timestamps, counts imported, counts deduped, and import status.

## Phase 1: Repository And Local Development Foundation

**User stories**: 20

### What to build

Create the monorepo foundation for extension, backend, importer, and local infrastructure. The result should let a developer start the backend dependencies locally and understand where each part of the product will live.

### Acceptance criteria

- [x] Monorepo structure separates extension, API/importer, shared docs, and infrastructure concerns.
- [x] Python backend project uses `uv` with locked dependencies.
- [x] Extension project uses WXT + React.
- [x] Local Docker Compose starts Postgres and any required import-time services.
- [x] Environment variables are documented with safe example values.
- [x] `GET /health` can run locally and return a healthy response.
- [x] No secrets are committed.

## Phase 2: StarScout Dataset Import Skeleton

**User stories**: 17, 18, 20

### What to build

Create the import workflow that can connect to a restored StarScout MongoDB dump, read low-activity and clustered suspicious-star collections, dedupe them, and write normalized aggregate-ready data into Postgres.

### Acceptance criteria

- [x] Importer can run locally against a small fixture shaped like the StarScout MongoDB collections.
- [x] Importer stores one deduped suspicious-star fact per `repo + actor + starred_at`.
- [x] Importer preserves whether each fact came from low-activity, lockstep, or both.
- [x] Importer records an import run with source metadata and row counts.
- [x] Importer can be rerun idempotently for the same source dataset without duplicating facts.
- [x] Backend tests prove overlap is not double-counted.
- [x] Backend tests prove aggregate counts are derived from deduped facts.

## Phase 3: Repo Aggregates And Star Integrity API

**User stories**: 1, 3, 4, 8, 9, 10, 17, 18

### What to build

Expose the core repo integrity API from Postgres-backed aggregates using fixture data first. This phase proves the central product math before connecting live GitHub star counts.

### Acceptance criteria

- [x] API returns aggregate suspicious-star metrics for an analyzed repo.
- [x] API returns a clear not-analyzed response for repos absent from StarScout aggregates.
- [x] API returns low-activity, lockstep, and overlap breakdowns.
- [x] API returns the StarScout analyzed-through cutoff date.
- [x] API never exposes suspected actor identities.
- [x] Backend tests cover success, not-analyzed, invalid owner/repo input, and percentage math.
- [x] Backend tests cover clamping when suspicious stars exceed denominator.

## Phase 4: GitHub Metadata And Current Star Cache

**User stories**: 10, 14, 16

### What to build

Add GitHub repository lookup and current star-count caching to make the denominator current and improve rename handling through GitHub repository identity metadata.

### Acceptance criteria

- [x] Backend fetches current repository metadata from GitHub REST for public repos.
- [x] Backend caches `stargazers_count` with a configured TTL.
- [x] Backend stores GitHub repo ID, node ID, and canonical full name when available.
- [x] Backend follows GitHub repository redirects or canonical name responses where supported.
- [x] API response uses current GitHub stars as the percentage denominator.
- [x] API returns a data-quality warning when current stars are lower than suspicious stars.
- [x] Backend tests mock GitHub responses for success, not found, rate limit, and count mismatch.

## Phase 5: Public API Hardening

**User stories**: 12, 13, 15

### What to build

Harden the public read API so the extension can call it safely without user authentication while limiting abuse and minimizing privacy risk.

### Acceptance criteria

- [x] API applies rate limits to repo integrity requests.
- [x] API accepts only valid public GitHub owner/repo path inputs.
- [x] API does not require user identity or extension-specific user identifiers.
- [x] API logs avoid long-lived per-user browsing history.
- [x] API responses are cacheable where safe.
- [x] CORS policy permits the intended extension/browser usage without opening unnecessary mutation surfaces.
- [x] Backend tests cover rate-limited responses and invalid input responses.

## Phase 6: Extension Repo Page Badge

**User stories**: 1, 2, 3, 6, 11, 12

### What to build

Implement the browser extension content script that detects public GitHub repository pages, calls the backend automatically, and injects a compact neutral suspected-percentage badge near the repository star area.

### Acceptance criteria

- [x] Extension detects `github.com/{owner}/{repo}` repository pages.
- [x] Extension ignores non-repo GitHub pages, private unsupported contexts, and non-GitHub hosts.
- [x] Extension sends only `owner/repo` to the backend.
- [x] Badge appears automatically after API response.
- [x] Badge displays suspected percentage for analyzed repos.
- [x] Badge displays a neutral not-analyzed state for repos absent from StarScout data.
- [x] Badge uses neutral styling and does not replace GitHub's native star count.
- [x] Manual verification steps are documented for loading the extension locally.

## Phase 7: Extension Popover Details And Attribution

**User stories**: 4, 5, 7, 8, 9, 10, 19

### What to build

Add the popover that explains the aggregate result, shows the estimated legitimate count, low-activity and lockstep breakdown, warnings, dataset cutoff, and visible attribution.

### Acceptance criteria

- [x] Popover opens from the badge without navigating away from GitHub.
- [x] Popover shows current stars, suspected non-legit stars, estimated legitimate stars, and suspected percentage.
- [x] Popover shows low-activity, lockstep, and overlap breakdowns.
- [x] Popover explains that results are heuristic and may include false positives.
- [x] Popover shows StarScout analyzed-through date.
- [x] Popover shows warnings for stale/mismatched data when returned by the API.
- [x] Popover includes visible attribution to StarScout, the paper, and Zenodo.
- [x] Popover does not show suspected actor identities.

## Phase 8: Full Dataset Import And Local Verification

**User stories**: 1, 3, 4, 8, 10, 17, 18

### What to build

Run the importer against the restored Zenodo MongoDB dataset, populate Postgres aggregates, and verify representative real repositories end-to-end through the local API and extension.

### Acceptance criteria

- [x] Zenodo MongoDB dump restoration steps are documented.
- [x] Full import completes and records import-run metadata.
- [x] Import report includes source counts, deduped counts, aggregate counts, and overlap counts.
- [x] A known analyzed repo returns expected aggregate data from the API.
- [x] A known not-analyzed repo returns the not-analyzed state.
- [ ] Extension displays correct analyzed and not-analyzed states against local backend.
- [x] Backend test suite passes after full import-related changes.

## Phase 9: Docker Compose Beta Deployment

**User stories**: 11, 13, 14, 15, 19

### What to build

Package the backend, Postgres, and operational configuration for a Docker Compose VPS beta deployment, then point the dev-loaded extension at the deployed API.

### Acceptance criteria

- [ ] Docker Compose can run the API and Postgres on a VPS.
- [ ] Deployment documentation covers environment variables, secrets, database migration/import, and restart behavior.
- [ ] API health route works on the deployed host.
- [ ] Repo integrity route works on the deployed host for analyzed and not-analyzed repos.
- [ ] Rate limiting is enabled in deployment.
- [ ] Minimal logging configuration is documented.
- [ ] Extension can be configured to use the deployed backend.

## Phase 10: Dev-Loaded Beta Readiness

**User stories**: 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 19

### What to build

Prepare the project for a dev-loaded beta with clear installation, usage, limitation, attribution, and manual QA documentation.

### Acceptance criteria

- [ ] README explains what the extension does and does not claim.
- [ ] README documents dev-loaded extension installation.
- [ ] README documents backend configuration for local and deployed APIs.
- [ ] README documents privacy posture and what data is sent to the backend.
- [ ] README documents StarScout/paper/Zenodo attribution.
- [ ] Manual QA checklist covers analyzed repo, not-analyzed repo, count mismatch fixture, GitHub navigation, and extension reload.
- [ ] Known limitations are documented, including public GitHub only, no private repos, no actor evidence, and dataset cutoff.

## Out Of Scope For This Plan

- Running the full StarScout DuckDB or BigQuery detection pipeline.
- Browser store publication.
- Private GitHub repositories.
- GitHub Enterprise Server.
- GitHub search, trending, topic, or organization listing pages.
- Public actor-level suspected stargazer evidence.
- User accounts, dashboards, alerts, billing, or analytics.
- Definitive fake-star or legitimate-star claims.
