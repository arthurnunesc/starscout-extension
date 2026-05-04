# PRD: StarScout-Based GitHub Star Integrity Extension

## Problem Statement

Developers use GitHub stars as a trust and popularity signal, but stars can be artificially inflated. Existing GitHub UI shows only the raw star count and gives no indication of whether a repository has suspected non-legitimate star activity.

StarScout provides research-backed methods for detecting suspicious GitHub stars, but it is a research/data pipeline, not a browser-friendly product. Users need a lightweight browser extension that surfaces StarScout-derived signals directly on GitHub repository pages.

## Solution

Build a browser extension that shows a compact, neutral badge on public GitHub repository pages. The badge displays the percentage of suspected non-legitimate stars based on StarScout's provided dataset.

The extension will query a hosted backend API. The backend will import StarScout's Zenodo MongoDB dataset, dedupe suspicious stars across detection methods by `repo + actor + starred_at`, aggregate results per repository, fetch/cache current GitHub star counts, and return safe aggregate-only metrics.

The product must use careful wording: "suspected non-legit stars" and "estimated legitimate stars." It must not claim definitive fake-star detection.

## User Stories

1. As a developer browsing GitHub, I want to see whether a repository has suspected non-legit stars, so that I can interpret its popularity more critically.
2. As a developer browsing GitHub, I want the signal to appear directly on repository pages, so that I do not need to leave GitHub.
3. As a developer browsing GitHub, I want to see the suspected non-legit percentage, so that I can compare repositories of different sizes.
4. As a developer browsing GitHub, I want to see the estimated legitimate star count, so that I can understand the adjusted popularity signal.
5. As a developer browsing GitHub, I want the extension to explain that the result can include false positives, so that I do not mistake it for a definitive accusation.
6. As a developer browsing GitHub, I want the badge to stay visually neutral, so that it informs without sensationalizing.
7. As a developer browsing GitHub, I want to open a popover with more detail, so that I can understand the low-activity and lockstep breakdown.
8. As a developer browsing GitHub, I want to see the StarScout data cutoff date, so that I understand whether the data may be stale.
9. As a developer browsing GitHub, I want to see when no StarScout record exists for a repo, so that I do not confuse missing data with zero suspected stars.
10. As a developer browsing GitHub, I want clear warnings when current GitHub star counts conflict with historical StarScout data, so that I can trust the displayed math.
11. As a developer browsing GitHub, I want the extension to work automatically on public repo pages, so that the experience is frictionless.
12. As a privacy-conscious user, I want the extension to send only public repository names to the backend, so that no account identity or private browsing context is exposed.
13. As a privacy-conscious user, I want the backend to avoid long-lived browsing logs, so that my repository visits are not stored unnecessarily.
14. As a maintainer of the service, I want the backend to fetch and cache current GitHub star counts, so that the extension does not need GitHub credentials.
15. As a maintainer of the service, I want rate limits on the public API, so that the backend is protected from abuse.
16. As a maintainer of the service, I want repo lookups to account for GitHub repo IDs and names, so that renames are handled more reliably.
17. As a maintainer of the service, I want StarScout actor-level data deduped before serving, so that the central percentage is not inflated by overlapping detection methods.
18. As a maintainer of the service, I want only aggregate results exposed publicly, so that suspected users are not publicly listed or shamed.
19. As a maintainer of the service, I want visible StarScout, paper, and Zenodo attribution, so that the product is transparent and compliant.
20. As a future implementer, I want a monorepo structure, so that extension, backend, importer, and infra evolve together during v1.

## Implementation Decisions

- The product will be an estimated GitHub star integrity badge, not a definitive fake-star detector.
- v1 supports public `github.com` repository pages only.
- v1 targets developers browsing GitHub.
- The extension will use WXT and React.
- The backend will use Python FastAPI.
- Python dependency management will use `uv`.
- The serving database will be Postgres.
- The StarScout Zenodo MongoDB dump will be restored and imported before v1.
- The importer will dedupe suspicious stars by `repo + actor + starred_at`.
- The backend will serve only aggregate repo-level results.
- The backend will fetch and cache current GitHub `stargazers_count`.
- Missing repos will be shown as "not found/analyzed," not `0%`.
- If suspected count exceeds current stars, the backend will clamp the legit estimate and return a data-quality warning.
- The API will be public read-only with rate limiting.
- Deployment target is Docker Compose on a VPS.
- The extension will query automatically on public GitHub repo pages.
- The badge will be compact, neutral, and open a popover for details.
- Visible attribution to StarScout, the ICSE paper, and Zenodo is required.
- Dev-loaded beta is the first distribution target.

## Testing Decisions

- v1 will focus on backend tests.
- Tests should verify external behavior, not internal implementation details.
- Importer tests should verify deduplication across low-activity and clustered records.
- API tests should verify response shape, percentage math, missing repo behavior, count mismatch behavior, and GitHub star-count cache behavior.
- Extension testing will be manual for v1.
- The content script should remain small and isolated so browser tests can be added later.

## Out of Scope

- Running the full StarScout DuckDB or BigQuery pipeline in v1.
- Supporting private repositories.
- Supporting GitHub Enterprise Server.
- Supporting GitHub search, trending, topic, or organization listing pages.
- Showing actor-level suspected stargazer evidence.
- Publishing to Chrome Web Store in v1.
- Building dashboards, accounts, alerts, or paid features.
- Claiming that stars are definitively fake or legitimate.
- Replacing GitHub's native star count.

## Further Notes

StarScout's own language and disclaimer matter. The extension should preserve the same caution: these are suspected signals and may include false positives.

The central v1 quality bar is accurate aggregate math. That is why v1 depends on importing the actor-level MongoDB dump instead of summing repo-level CSV aggregates.
