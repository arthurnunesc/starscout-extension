from datetime import timedelta
from typing import Protocol

from starscout_api.github.client import (
    GitHubClient,
    GitHubLookupError,
    GitHubRateLimitError,
    GitHubRepoNotFoundError,
    GitHubRepositoryMetadata,
)
from starscout_api.integrity.models import RepoAggregateRecord, StarCountSnapshot

GITHUB_NOT_FOUND_WARNING = (
    "GitHub repository metadata was not found; using StarScout count denominator."
)
GITHUB_RATE_LIMIT_WARNING = (
    "GitHub repository metadata is rate limited; using StarScout count denominator."
)
GITHUB_LOOKUP_FAILED_WARNING = (
    "GitHub repository metadata lookup failed; using StarScout count denominator."
)


class GitHubRepoCache(Protocol):
    def get_fresh(self, repo: str, ttl: timedelta) -> GitHubRepositoryMetadata | None: ...

    def save(self, repo: str, metadata: GitHubRepositoryMetadata) -> None: ...


class GitHubStarCountProvider:
    def __init__(self, client: GitHubClient, cache: GitHubRepoCache, ttl_seconds: int) -> None:
        self._client = client
        self._cache = cache
        self._ttl = timedelta(seconds=ttl_seconds)

    def get_current_stars(self, aggregate: RepoAggregateRecord) -> StarCountSnapshot:
        cached = self._cache.get_fresh(aggregate.repo, self._ttl)
        if cached is not None:
            return _to_snapshot(cached, [])

        try:
            metadata = self._client.get_repository(aggregate.repo)
        except GitHubRepoNotFoundError:
            return StarCountSnapshot(
                repo=aggregate.repo,
                github_repo_id=None,
                current_stars=aggregate.suspected_non_legit_stars,
                warnings=[GITHUB_NOT_FOUND_WARNING],
            )
        except GitHubRateLimitError:
            return StarCountSnapshot(
                repo=aggregate.repo,
                github_repo_id=None,
                current_stars=aggregate.suspected_non_legit_stars,
                warnings=[GITHUB_RATE_LIMIT_WARNING],
            )
        except GitHubLookupError:
            return StarCountSnapshot(
                repo=aggregate.repo,
                github_repo_id=None,
                current_stars=aggregate.suspected_non_legit_stars,
                warnings=[GITHUB_LOOKUP_FAILED_WARNING],
            )

        self._cache.save(aggregate.repo, metadata)
        return _to_snapshot(metadata, [])


def _to_snapshot(metadata: GitHubRepositoryMetadata, warnings: list[str]) -> StarCountSnapshot:
    return StarCountSnapshot(
        repo=metadata.repo,
        github_repo_id=metadata.github_repo_id,
        current_stars=metadata.current_stars,
        warnings=warnings,
    )
