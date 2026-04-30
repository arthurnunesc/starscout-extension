# Manual QA Checklist

Run this checklist before sharing a dev-loaded beta.

## Prerequisites

- Local or deployed backend is running.
- StarScout data has been imported into Postgres.
- Dev-loaded extension is installed from WXT output.
- Extension backend URL points at the API under test.

## Analyzed Repository

Use `https://github.com/xai-org/grok-1`.

- [ ] Badge appears near GitHub's native star control.
- [ ] Badge shows a suspected percentage.
- [ ] Clicking the badge opens the popover without navigating away from GitHub.
- [ ] Popover shows current stars, suspected non-legit stars, estimated legitimate stars, and percentage.
- [ ] Popover shows low-activity, lockstep, and overlap breakdown.
- [ ] Popover shows the StarScout analyzed-through date.
- [ ] Popover includes StarScout, paper, and Zenodo attribution.
- [ ] Popover does not show suspected actor identities.

## Not-Analyzed Repository

Use `https://github.com/octocat/Hello-World`.

- [ ] Badge appears near GitHub's native star control.
- [ ] Badge shows a neutral not-analyzed state.
- [ ] Popover explains that missing StarScout data is not a zero-suspected claim.
- [ ] No suspected actor identities are shown.

## Count Mismatch Fixture

Use a backend fixture or database row where `suspected_non_legit_stars` is greater
than the current GitHub star count.

- [ ] API response clamps `estimatedLegitStars` to `0`.
- [ ] API response includes a count-mismatch warning.
- [ ] Popover shows the warning clearly.

## GitHub Navigation

- [ ] Open a supported repo page directly and confirm the badge appears.
- [ ] Navigate between GitHub repo pages without a full page reload and confirm the badge updates.
- [ ] Navigate to non-repo GitHub pages such as topics, marketplace, issues, or pull requests and confirm no badge is injected.
- [ ] Navigate to a non-GitHub host and confirm the content script does not run.

## Extension Reload

- [ ] Reload the dev extension from the browser extensions page.
- [ ] Refresh an analyzed repo page and confirm the badge returns.
- [ ] Restart the backend and refresh GitHub; confirm unavailable states recover after the API is back.

## Regression Commands

```sh
cd backend
uv run pytest
uv run ruff check .

cd ../extension
pnpm compile
```
