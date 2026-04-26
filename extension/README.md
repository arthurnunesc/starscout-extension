# StarScout Extension

WXT + React browser extension for displaying StarScout-derived suspected non-legit star signals on public GitHub repository pages.

## Development

```sh
pnpm install
pnpm dev
```

Type-check without building:

```sh
pnpm compile
```

## Manual Verification

1. Start the backend on `http://127.0.0.1:8000` with Postgres data loaded.
2. Run `pnpm dev` from `extension/`.
3. Load the WXT-generated development extension in the browser.
4. Open a public GitHub repository page such as `https://github.com/owner/repo`.
5. Confirm a compact `StarScout` badge appears near GitHub's native star control.
6. Confirm analyzed repositories show a suspected percentage and missing aggregates show `not analyzed`.
7. Navigate to a non-repository GitHub page and confirm no badge is injected.
