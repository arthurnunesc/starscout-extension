# Privacy Notice

This notice is intended for the StarScout Star Integrity dev-loaded beta at
`https://starscout-extension.arthurnun.es/privacy`.

## Summary

The extension sends only the public GitHub repository identifier currently being
viewed, such as `owner/repo`, to the StarScout API. It does not collect GitHub
credentials, GitHub user identity, extension-specific user IDs, or private
repository data.

## Data The Extension Sends

- Public GitHub repository owner and name, for example `xai-org/grok-1`.
- Standard browser request metadata sent by the browser when calling the API,
  such as IP address and user agent.

## Data The Extension Does Not Send

- GitHub credentials or tokens.
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

Operational logs should not be used to build long-lived per-user browsing
history. Production deployments should keep log retention short and avoid adding
user identity or extension identifiers.

## Sharing And Sale

This project does not sell user data. The API is designed to return aggregate
public-repository metrics and does not require accounts, login, or payment.

## Scope And Limitations

- The extension supports public `github.com/{owner}/{repo}` repository pages.
- Private repositories and GitHub Enterprise Server are not supported.
- Missing StarScout aggregate data is shown as not analyzed, not as zero
  suspected stars.
- Results are heuristic signals, not definitive claims that stars, users, or
  repositories are fake.

## Attribution

This project uses StarScout-derived data and methodology.

- StarScout repository: https://github.com/hehao98/StarScout
- Zenodo replication package DOI: https://doi.org/10.5281/zenodo.17009694
- Paper: Hao He, Haoqin Yang, Philipp Burckhardt, Alexandros Kapravelos,
  Bogdan Vasilescu, and Christian Kaestner. 2026. Six Million (Suspected) Fake
  Stars on GitHub: A Growing Spiral of Popularity Contests, Spam, and Malware.
  ICSE 2026.

## Support

For support or privacy questions, open a GitHub Issue in the project repository.
