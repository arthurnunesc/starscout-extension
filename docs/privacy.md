# Privacy Policy

**Effective date:** 2026-05-02

This privacy policy describes how the StarScout Star Integrity browser extension
("the extension") handles information.

## Data The Extension Collects And Sends

When you visit a public GitHub repository page that the extension recognizes, the
extension sends the following information to the StarScout API:

- The public GitHub repository identifier currently being viewed, such as
  `owner/repo` (for example, `xai-org/grok-1`).
- Standard browser request metadata automatically sent by the browser when
  calling the API, such as IP address and user agent.

## Data The Extension Does Not Collect

The extension does **not** collect or send any of the following:

- GitHub credentials, tokens, or passwords.
- GitHub username or account identity.
- Extension-specific user identifiers.
- Private repository contents or private repository names.
- Suspected actor-level stargazer identities.

## How The API Uses Data

The API uses the public `owner/repo` identifier to return aggregate StarScout-
derived suspected non-legit star metrics for that repository. Responses are
repo-level aggregates only and do not expose suspected actor lists.

The API may also fetch current public repository metadata from GitHub, such as
the current `stargazers_count`, to compute the displayed percentage denominator.

## Logs And Retention

The backend logs operational data to support availability, debugging, abuse
prevention, and rate limiting. Because the repository name is part of the API
path, access logs from the API host, reverse proxy, or container platform may
contain public `owner/repo` paths.

Operational logs are retained only as long as necessary for the purposes
described above. The project does not intentionally retain long-lived per-user
browsing history.

## Sharing And Sale

This project does not sell user data. The API is designed to return aggregate
public-repository metrics and does not require accounts, login, or payment. User
data is not shared with third parties.

## Scope And Limitations

- The extension supports public `github.com/{owner}/{repo}` repository pages.
- Private repositories and GitHub Enterprise Server are not supported.
- Missing StarScout aggregate data is shown as not analyzed, not as zero
  suspected stars.
- Results are heuristic signals, not definitive claims that stars, users, or
  repositories are fake.

## Contact And Support

For support or privacy questions, open a GitHub Issue in the project repository:
https://github.com/arthurnunesc/starscout-extension/issues
