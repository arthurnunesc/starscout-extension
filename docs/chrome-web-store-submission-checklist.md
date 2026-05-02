# Chrome Web Store Submission Checklist

Use this checklist when filling out the Chrome Web Store developer dashboard.

## Package

- [ ] Final zip: `extension/.output/starscout-extension-0.1.0-chrome.zip`
- [ ] Manifest version: 3
- [ ] Required icon sizes: 16, 32, 48, 96, 128

## Store Listing

Copy the values from `docs/chrome-web-store.md`:

| Field | Value |
|-------|-------|
| Extension name | StarScout Star Integrity |
| Short description | Shows heuristic suspected non-legit star signals on public GitHub repositories. |
| Full description | See `docs/chrome-web-store.md` |
| Category | Developer Tools |
| Language | English |

## URLs

| Field | Value |
|-------|-------|
| Privacy policy | https://arthurnun.es/starscout-extension/privacy |
| Support / Contact | https://github.com/arthurnunesc/starscout-extension/issues |
| Website (optional) | https://github.com/arthurnunesc/starscout-extension |

## Screenshots

Upload from `docs/store-assets/screenshots/`:

1. `analyzed-repo-desktop.png` — badge visible near star count
2. `analyzed-repo-popover.png` — popover open with aggregate metrics
3. `not-analyzed-repo.png` — neutral not-analyzed state

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
  - Transfer to third parties: No

## Single-Purpose Statement

> The extension has a single purpose: to display a heuristic suspected non-legit
> star signal badge on public GitHub repository pages.

## Pre-Submit Verification

- [ ] Manual QA checklist completed: `docs/manual-qa.md`
- [ ] All user-facing text uses neutral terminology
- [ ] Privacy policy is publicly hosted and accessible
- [ ] Support URL is accessible
- [ ] Screenshot dimensions are acceptable (1280x800 or 640x400)
- [ ] No alarming colors or fake-star imagery in icons/screenshots
- [ ] Backend health, CORS, and endpoints verified

## Post-Submit

- [ ] Note the review submission ID
- [ ] Monitor the developer dashboard for review feedback
- [ ] Respond to any requests for additional information promptly
