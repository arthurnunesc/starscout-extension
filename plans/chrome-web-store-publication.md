# Plan: Chrome Web Store Publication

## Goal

Prepare the StarScout browser extension and supporting backend/documentation for a
direct Chrome Web Store submission.

## 1. Audit Store Readiness

- Inspect the generated Chrome MV3 manifest from WXT.
- Verify extension name, description, version, icons, permissions, and host permissions.
- Confirm no local-only API URLs or localhost permissions are present in the production package.
- Confirm the extension calls only `https://starscout-extension-api.arthurnun.es` in the store build.

## 2. Create Production Packaging Path

- Add a dedicated Chrome Web Store packaging command.
- Keep local/dev packaging separate from production packaging.
- Ensure the production command sets:
  - `WXT_PUBLIC_STARSCOUT_API_BASE_URL=https://starscout-extension-api.arthurnun.es`
  - production-only host permissions
  - Chrome MV3 output
- Document the exact generated zip path.

## 3. Privacy Policy

- Draft a public privacy policy explaining:
  - the extension sends only public `owner/repo` identifiers;
  - it does not collect user identity;
  - it does not collect GitHub credentials;
  - it does not inspect private repositories;
  - backend logs should avoid long-lived browsing history;
  - GitHub metadata is fetched/cached server-side;
  - user data is not sold or shared.
- Add the privacy policy to the repo.
- Decide and document the public hosting URL.
- Recommended URL: `https://arthurnun.es/starscout-extension/privacy`.

## 4. Store Listing Content

- Draft Chrome Web Store listing copy:
  - extension name;
  - short description;
  - full description;
  - single-purpose statement;
  - permission justification;
  - data usage answers;
  - support/contact information.
- Save the copy in `docs/chrome-web-store.md`.

## 5. Icons And Branding

- Replace default WXT icons if they are still generic.
- Ensure required icon sizes exist:
  - `16x16`
  - `32x32`
  - `48x48`
  - `128x128`
- Prefer a neutral, non-accusatory StarScout-style visual language.
- Avoid alarming colors or “fake star” imagery.

## 6. Screenshots And Store Assets

- Capture Chrome Web Store screenshots for:
  - analyzed repository badge;
  - analyzed repository popover;
  - neutral not-analyzed state.
- Use accepted screenshot dimensions such as `1280x800` or `640x400`.
- Store source screenshots under `docs/store-assets/screenshots/`.
- Optional: create promotional tile assets if desired.

## 7. Backend Production Checks

- Verify production API routes:
  - `GET https://starscout-extension-api.arthurnun.es/health`
  - analyzed repo integrity route;
  - not-analyzed repo integrity route.
- Confirm HTTPS works.
- Confirm CORS supports the published Chrome extension origin if needed.
- Confirm rate limiting is enabled.
- Confirm Postgres backups and basic uptime monitoring are planned or configured.

## 8. Exact ZIP Verification

- Build the exact production zip intended for upload.
- Unzip it and load it manually in Chrome through `chrome://extensions`.
- Verify:
  - analyzed repo works;
  - not-analyzed repo works;
  - popover opens and does not navigate away;
  - GitHub SPA navigation updates the badge;
  - extension reload works;
  - no badge appears on unsupported GitHub pages.
- Record the result in `docs/manual-qa.md` or a dedicated release checklist.

## 9. Chrome Web Store Submission Checklist

- Prepare the final zip path.
- Prepare dashboard values:
  - privacy policy URL;
  - support URL or email;
  - category;
  - language;
  - short description;
  - full description;
  - permission justifications;
  - data usage declarations.
- The Chrome Web Store developer account and final upload must be done by the account owner.

## 10. Commit And Push

- Commit production packaging scripts/configuration.
- Commit privacy policy and store listing docs.
- Commit icons and screenshots.
- Commit release checklist updates.
- Push everything before submitting the store package.

## Decisions Needed

- Final extension name.
- Privacy policy hosting location.
- Support/contact email or URL.
- Whether to create new branding/icons or use existing assets.
- Whether Chrome-only is enough for this release, or Firefox packaging should also be prepared.
