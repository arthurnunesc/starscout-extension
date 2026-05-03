# Chrome Web Store Listing

This document contains the content and values needed for the Chrome Web Store
dashboard submission.

## Extension Name

StarScout - See Suspected Non-Legit Stars on GitHub repos

## Short Description (max 132 characters)

Shows heuristic suspected non-legit star signals on public GitHub repositories.

## Full Description

StarScout - See Suspected Non-Legit Stars on GitHub repos adds a neutral badge near GitHub's native star count on
public repository pages. When a repository has been analyzed by the StarScout
dataset, the badge shows the estimated percentage of suspected non-legit stars
based on heuristic signals. Clicking or hovering the badge opens a popover with
aggregate metrics, including current GitHub stars, estimated legitimate stars,
breakdown categories, and dataset attribution.

The extension does not prove that stars are fake, does not expose suspected
actor identities, and does not support private repositories or GitHub Enterprise
Server. Missing data is shown as "not analyzed," not as zero suspected stars.

This extension sends only the public `owner/repo` identifier of the repository
you are viewing to the StarScout API. It does not collect GitHub credentials,
account identity, extension-specific user IDs, or private repository data. See
the privacy policy for full details.

Data and methodology attribution: StarScout, ICSE 2026 paper, and Zenodo DOI
10.5281/zenodo.17009694.

## Single-Purpose Statement

The extension has a single purpose: to display a heuristic suspected non-legit
star signal badge on public GitHub repository pages.

## Permission Justification

The extension does not request any `permissions` in the manifest. All
functionality is implemented through `host_permissions` and content scripts.

## Host-Permission Justification

- `https://github.com/*` — Required to inject the badge and popover on public
  GitHub repository pages. The content script matches `https://github.com/*/*`
  and parses the URL to detect repository pages.
- `https://starscout-extension-api.arthurnun.es/*` — Required to call the
  StarScout API and retrieve aggregate star-integrity metrics for the
  repository being viewed.

## Data Usage Answers (Chrome Web Store questionnaire)

- **Do you transmit user data?** Yes — the public `owner/repo` identifier and
  standard browser request metadata (IP, user agent) are sent to the StarScout
  API.
- **Is the data transmitted secure?** Yes — the API uses HTTPS.
- **Is the data transmitted user-identifiable?** No — the extension does not
  send GitHub identity, credentials, extension-specific user IDs, or private
  repository data.
- **Do you sell user data?** No.
- **Do you use user data for purposes other than the extension's single purpose?**
  No.
- **Do you transfer user data to third parties?** No.

## Privacy Policy URL

https://arthurnun.es/projects/starscout-extension/privacy

## Support / Contact URL

https://github.com/arthurnunesc/starscout-extension/issues

## Category

Developer Tools

## Language

English

## Screenshot Requirements

- At least one screenshot showing the analyzed repository badge and popover.
- At least one screenshot showing a not-analyzed repository state.
- Recommended dimensions: 1280x800 or 640x400.
- Screenshots must not imply proof of fake stars, fake users, or fake
  repositories.

Store screenshots are stored in `docs/store-assets/screenshots/`.
