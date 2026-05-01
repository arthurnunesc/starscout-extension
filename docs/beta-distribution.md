# Beta Distribution

This document describes the dev-loaded beta distribution path for trusted
testers. This is not a Chrome Web Store release.

## Public URLs

- Landing page: `https://starscout-extension.arthurnun.es`
- Privacy notice: `https://starscout-extension.arthurnun.es/privacy`
- Support: GitHub Issues
- API: `https://starscout-extension-api.arthurnun.es`

## Package The Chrome Beta

From the extension directory:

```sh
pnpm zip:beta
```

The beta script bakes the deployed API URL into the extension and omits local
backend host permissions from the shared package.

The generated zip is written under `extension/.output/`.

## Tester Installation

Share the zip with testers together with these steps:

1. Unzip the package locally.
2. Open `chrome://extensions`.
3. Enable Developer mode.
4. Choose Load unpacked.
5. Select the unzipped extension directory.
6. Open a public GitHub repository page.
7. Verify the `StarScout` badge appears near GitHub's native star control.

## Updating

Dev-loaded packages do not auto-update.

To update:

1. Download the new beta zip.
2. Unzip it into a fresh local directory.
3. Open `chrome://extensions`.
4. Remove the previous StarScout beta or click Reload after replacing the folder.
5. Refresh GitHub repository pages.

## Uninstalling

Open `chrome://extensions`, find `StarScout Star Integrity`, and click Remove.

## Before Sharing

Run the verification checklist:

```sh
cd backend
uv run pytest
uv run ruff check .

cd ../extension
pnpm compile
pnpm zip:beta
```

Then manually verify the scenarios in `docs/manual-qa.md`.

## Public Release Hygiene

- Do not commit `.env` files, generated zips, database dumps, or StarScout data
  dumps.
- Do not distribute the imported Postgres database unless source-data licensing
  and redistribution terms are confirmed.
- Keep public wording neutral: suspected non-legit star signal, not proof of fake
  stars.
- Include the landing page, privacy notice, and GitHub Issues support link in
  every beta announcement.
