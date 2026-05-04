# Plan: Chrome Web Store Publication

## Goal

Prepare the remaining StarScout browser extension, backend, and documentation work
needed for a direct Chrome Web Store submission.

## Current Baseline

- WXT already generates a Chrome MV3 manifest.
- The generated manifest already has no extension permissions.
- The generated manifest already includes host permissions for:
  - `https://github.com/*`
  - `https://starscout-extension-api.arthurnun.es/*`
- The extension already defaults to `https://starscout-extension-api.arthurnun.es`.
- The current packaged extension does not use remote code: no external scripts,
  remote JS/Wasm imports, `eval`, `new Function`, WebAssembly, or `.wasm` files.
- Backend CORS and repo-integrity rate limiting already exist in code.
- Dataset dumps and generated packages are already excluded from git.

## 1. Fix Publication Blockers

- Replace the default popup title in `extension/entrypoints/popup/index.html`.
- Ensure the generated `action.default_title` is not `Default Popup Title`.
- Replace user-facing “dev-loaded beta” wording in the popup with Chrome Web
  Store-ready language.
- Keep all user-facing language neutral:
  - use “suspected non-legit stars”;
  - do not claim that stars, users, or repositories are fake.

## 2. Use Production Packaging Command

- Use the shared Chrome packaging command, `pnpm zip`.
- Keep local/dev packaging separate from Store packaging.
- Ensure the command uses:
  - the production fallback API URL, `https://starscout-extension-api.arthurnun.es`
  - Chrome MV3 output
- Document the exact generated zip path.
- After generating the final zip, inspect the packaged manifest and bundled code
  for local-only URLs such as `localhost` or `127.0.0.1`.

## 3. Publish Privacy Policy

- Convert `docs/privacy.md` from a dev-loaded beta notice into public Chrome Web
  Store privacy policy content.
- Include:
  - effective date;
  - public `owner/repo` identifiers sent to the API;
  - standard request metadata such as IP address and user agent;
  - no GitHub credentials collected;
  - no GitHub account identity collected;
  - no extension-specific user ID collected;
  - no private repositories inspected;
  - repo-level aggregate responses only;
  - GitHub metadata fetched/cached server-side;
  - operational logging purpose and retention posture;
  - no sale or sharing of user data;
  - GitHub Issues support link.
- Decide and document the public hosting URL.
- Recommended URL: `https://arthurnun.es/projects/starscout-extension/privacy`.
- Verify the hosted URL is public before submitting the Store listing.

## 4. Draft Store Listing Content

- Create `docs/chrome-web-store.md` with:
  - extension name;
  - short description;
  - full description;
  - single-purpose statement;
  - permission justification;
  - host-permission justification;
  - data usage answers;
  - privacy policy URL;
  - support/contact URL.
- Ensure the listing copy uses the same neutral terminology as the extension UI.

## 5. Replace Icons And Branding

- Replace the default WXT puzzle-piece icons in `extension/public/icon/`.
- Ensure required icon sizes exist:
  - `16x16`
  - `32x32`
  - `48x48`
  - `128x128`
- Keep optional `96x96` if still useful for generated manifests.
- Use a neutral StarScout-style visual language.
- Avoid alarming colors or “fake star” imagery.

## 6. Create Store Screenshots And Assets

- Capture Chrome Web Store screenshots for:
  - analyzed repository badge;
  - analyzed repository popover;
  - neutral not-analyzed state.
- Use accepted screenshot dimensions such as `1280x800` or `640x400`.
- Store source screenshots under `docs/store-assets/screenshots/`.
- Optional: create promotional tile assets if desired.
- Verify screenshots do not imply proof of fake stars, fake users, or fake
  repositories.

## 7. Verify Production Backend Operations

- Verify live production routes:
  - `GET https://starscout-extension-api.arthurnun.es/health`
  - analyzed repo integrity route;
  - not-analyzed repo integrity route.
- Confirm HTTPS works.
- Confirm CORS works for extension requests.
- Confirm live rate limiting behavior is acceptable for Store users.
- Confirm Postgres backups and basic uptime monitoring are planned or configured.
- Confirm production logs do not intentionally retain long-lived per-user browsing
  history.

## 8. Exact ZIP Verification

- Build the exact production zip intended for upload.
- Unzip it and load it manually in Chrome through `chrome://extensions`.
- Verify:
  - manifest name, description, icons, action title, permissions, and host
    permissions;
  - bundled code calls only `https://starscout-extension-api.arthurnun.es`;
  - analyzed repo works;
  - not-analyzed repo works;
  - popover opens and does not navigate away;
  - GitHub SPA navigation updates the badge;
  - extension reload works;
  - no badge appears on unsupported GitHub pages;
  - popup language is Store-ready and not beta/dev-only.
- Record the Chrome Web Store remote-code answer as **No** after confirming the
  packaged output has only bundled local JS/CSS and no remote JS/Wasm execution.
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
  - remote-code declaration;
  - data usage declarations.
- Confirm the Store listing, extension UI, screenshots, README, and privacy
  policy use consistent terminology.
- The Chrome Web Store developer account and final upload must be done by the
  account owner.

## 10. Commit And Push

- Commit production packaging scripts/configuration.
- Commit privacy policy and Store listing docs.
- Commit icons and screenshots.
- Commit release checklist updates.
- Push everything before submitting the Store package.

## Decisions Needed

- Final extension name.
- Privacy policy hosting location.
- Support/contact email or URL.
- Whether to create new branding/icons or adapt existing StarScout-style assets.
- Whether Chrome-only is enough for this release, or Firefox packaging should
  also be prepared later.
