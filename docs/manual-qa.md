# Manual QA Checklist

This checklist covers verification steps for the Chrome Web Store release of the
StarScout - See Suspected Non-Legit Stars on GitHub repos extension.

## Automated / Programmatic Verification

The following were verified during the build process:

- [x] **Manifest name**: `StarScout - See Suspected Non-Legit Stars on GitHub repos`
- [x] **Manifest description**: `Shows heuristic suspected non-legit star signals on public GitHub repository pages.`
- [x] **Manifest version**: `0.1.1`
- [x] **Action default title**: `StarScout - See Suspected Non-Legit Stars on GitHub repos`
- [x] **Icons present**: 16, 32, 48, 96, 128
- [x] **Permissions**: empty array (no extension permissions requested)
- [x] **Host permissions**: `https://github.com/*`, `https://starscout-extension-api.arthurnun.es/*`
- [x] **No local-only URLs in bundled code**: no `localhost` or `127.0.0.1` references found
- [x] **Production API URL baked in**: `https://starscout-extension-api.arthurnun.es`
- [x] **Popup title**: `StarScout - See Suspected Non-Legit Stars on GitHub repos` (not "Default Popup Title")
- [x] **Popup language**: Store-ready, no "dev-loaded beta" wording
- [x] **Backend health**: `GET /health` returns 200 `{"status":"ok","service":"StarScout API"}`
- [x] **Analyzed repo endpoint**: `GET /repos/xai-org/grok-1/star-integrity` returns 200 with aggregate metrics
- [x] **Not-analyzed repo endpoint**: `GET /repos/octocat/Hello-World/star-integrity` returns 200 with `analyzed: false`
- [x] **HTTPS**: API uses HTTP/2 with valid TLS
- [x] **CORS**: `access-control-allow-origin: https://github.com` present for extension origin

## Required Manual Verification

The following must be verified by loading the built extension in Chrome before
Store submission:

1. **Load the unpacked production build**:
   ```sh
   cd extension
   pnpm zip:chrome-store
   unzip .output/starscout-extension-0.1.1-chrome.zip -d /tmp/starscout-store-test
   ```
   Then open `chrome://extensions`, enable Developer mode, click **Load unpacked**,
   and select `/tmp/starscout-store-test`.

2. **Analyzed repository**:
   - [ ] Navigate to `https://github.com/xai-org/grok-1`
   - [ ] Verify the `StarScout` badge appears near the native star count
   - [ ] Verify the badge shows a percentage (e.g., `85.53% suspected`)
   - [ ] Hover, click, and keyboard-focus the badge and verify the popover opens with aggregate metrics
   - [ ] Verify the badge and popover do not navigate away when clicked
   - [ ] Verify popover attribution and dataset cutoff are present

3. **Not-analyzed repository**:
   - [ ] Navigate to `https://github.com/octocat/Hello-World`
   - [ ] Verify the badge shows `Not analyzed - StarScout`
   - [ ] Hover the badge and verify the not-analyzed popover opens

4. **Unsupported GitHub pages**:
   - [ ] Navigate to `https://github.com/orgs/community` or `https://github.com/topics`
   - [ ] Verify no StarScout badge appears
   - [ ] Navigate to `https://github.com/xai-org` (user/org profile, no repo)
   - [ ] Verify no badge appears
   - [ ] Navigate to a private repository page available to the tester
   - [ ] Verify no StarScout badge appears and no StarScout API request is sent

5. **SPA navigation**:
   - [ ] Start on `https://github.com/xai-org/grok-1`
   - [ ] Click a link to `https://github.com/octocat/Hello-World` without reloading
   - [ ] Verify the badge updates correctly (or disappears if not a repo page)
   - [ ] Navigate back and verify the badge reappears

6. **Extension popup**:
   - [ ] Click the extension icon in the Chrome toolbar
   - [ ] Verify the popup title is `StarScout - See Suspected Non-Legit Stars on GitHub repos`
   - [ ] Verify popup text does not contain "beta" or "dev-loaded"
   - [ ] Verify popup language is neutral

7. **Extension reload**:
   - [ ] Open `chrome://extensions`
   - [ ] Click the reload icon on StarScout - See Suspected Non-Legit Stars on GitHub repos
   - [ ] Return to a GitHub repo page
   - [ ] Verify the badge reappears after reload

8. **Screenshots review**:
   - [ ] Review `docs/store-assets/screenshots/analyzed-repo-desktop.png`
   - [ ] Review `docs/store-assets/screenshots/analyzed-repo-popover.png`
   - [ ] Review `docs/store-assets/screenshots/not-analyzed-repo.png`
   - [ ] Review `docs/store-assets/screenshots/analyzed-repo-low-signal.png`
   - [ ] Confirm screenshots do not imply proof of fake stars, fake users, or fake repositories
   - [ ] Confirm screenshots are 1280x800 or 640x400

## Store Listing Consistency Check

Before submitting, verify consistent terminology across all surfaces:

- [ ] Extension UI (badge, popover, popup)
- [ ] `docs/chrome-web-store.md` listing copy
- [ ] Public privacy policy at `https://arthurnun.es/projects/starscout-extension/privacy`
- [ ] `README.md`
- [ ] Screenshots

All should use:
- "suspected non-legit stars"
- "heuristic signal"
- No claims that stars, users, or repositories are definitively fake
