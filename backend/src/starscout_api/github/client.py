from dataclasses import dataclass

import httpx


class GitHubLookupError(Exception):
    pass


class GitHubRepoNotFoundError(GitHubLookupError):
    pass


class GitHubRateLimitError(GitHubLookupError):
    pass


@dataclass(frozen=True)
class GitHubRepositoryMetadata:
    repo: str
    github_repo_id: int
    github_node_id: str
    current_stars: int


class GitHubClient:
    def __init__(self, token: str | None = None, base_url: str = "https://api.github.com") -> None:
        self._token = token
        self._base_url = base_url.rstrip("/")

    def get_repository(self, repo: str) -> GitHubRepositoryMetadata:
        headers = {
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }
        if self._token:
            headers["Authorization"] = f"Bearer {self._token}"

        response = httpx.get(
            f"{self._base_url}/repos/{repo}",
            headers=headers,
            follow_redirects=True,
            timeout=10.0,
        )
        if response.status_code == 404:
            raise GitHubRepoNotFoundError(repo)
        if response.status_code in {403, 429}:
            raise GitHubRateLimitError(repo)
        if response.status_code >= 400:
            raise GitHubLookupError(repo)

        payload = response.json()
        return GitHubRepositoryMetadata(
            repo=payload["full_name"],
            github_repo_id=payload["id"],
            github_node_id=payload["node_id"],
            current_stars=payload["stargazers_count"],
        )
