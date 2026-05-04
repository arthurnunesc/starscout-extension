# Chrome Web Store Submission Checklist

Use this checklist when filling out the Chrome Web Store developer dashboard.

## Package

- [ ] Final zip: `extension/.output/starscout-extension-0.1.2-chrome.zip`
- [ ] Manifest version: 3
- [ ] Required icon sizes: 16, 32, 48, 96, 128

## Store Listing

Copy the values from `docs/chrome-web-store.md`:

| Field | Value |
|-------|-------|
| Extension name | StarScout - See Suspected Non-Legit Stars on GitHub repos |
| Short description | Shows suspected non-legit stars on public GitHub repositories. |
| Full description | See `docs/chrome-web-store.md` |
| Category | Developer Tools |
| Language | English |

## URLs

| Field | Value |
|-------|-------|
| Privacy policy | https://arthurnun.es/projects/starscout-extension/privacy |
| Support / Contact | https://github.com/arthurnunesc/starscout-extension/issues |
| Website (optional) | https://github.com/arthurnunesc/starscout-extension |

## Screenshots

Upload from `docs/store-assets/screenshots/`:

1. `analyzed-repo-desktop.png` — badge visible near star count
2. `analyzed-repo-popover.png` — popover open with aggregate metrics
3. `not-analyzed-repo.png` — neutral not-analyzed state
4. `analyzed-repo-low-signal.png` — low suspected non-legit star signal example

## Promotional Images

Upload from `docs/store-assets/promotional/`:

1. `small-promo-tile.png` — small promotional tile, 440x280

## Permissions & Data Usage

- [ ] Permissions: None declared (`permissions: []`)
- [ ] Host permissions:
  - `https://github.com/*` — inject badge on GitHub repo pages
  - `https://starscout-extension-api.arthurnun.es/*` — call StarScout API
- [ ] Data usage answers:
  - Transmit user data: Yes (public `owner/repo` + standard request metadata)
  - Secure transmission: Yes (HTTPS)
  - User-identifiable: No
  - Sell data: No
  - Use for other purposes: No
  - Third-party transfer: The backend tries to query GitHub for public repository metadata; no sale or account-identity sharing

## Single-Purpose Statement

> The extension has a single purpose: to display a suspected non-legit stars
> badge on public GitHub repository pages.

## Pre-Submit Verification

- [ ] Manual QA checklist completed: `docs/manual-qa.md`
- [ ] All user-facing text uses neutral terminology
- [ ] Privacy policy is publicly hosted and accessible
- [ ] Support URL is accessible
- [ ] Screenshot dimensions are acceptable (1280x800 or 640x400)
- [ ] Small promotional tile dimensions are acceptable (440x280)
- [ ] No alarming colors or fake-star imagery in icons, screenshots, or promotional assets
- [ ] Backend health, CORS, and endpoints verified

## Post-Submit

- [ ] Note the review submission ID
- [ ] Monitor the developer dashboard for review feedback
- [ ] Respond to any requests for additional information promptly
