from datetime import timedelta

from starscout_api.github.client import (
    GitHubRateLimitError,
    GitHubRepoNotFoundError,
    GitHubRepositoryMetadata,
)
from starscout_api.integrity.models import RepoAggregateRecord
from starscout_api.integrity.star_counts import GitHubStarCountProvider


class FakeGitHubClient:
    def __init__(self, result: GitHubRepositoryMetadata | Exception) -> None:
        self._result = result

    def get_repository(self, repo: str) -> GitHubRepositoryMetadata:
        if isinstance(self._result, Exception):
            raise self._result
        return self._result


class FakeCache:
    def __init__(self, cached: GitHubRepositoryMetadata | None = None) -> None:
        self._cached = cached
        self.saved: tuple[str, GitHubRepositoryMetadata] | None = None

    def get_fresh(self, repo: str, ttl: timedelta) -> GitHubRepositoryMetadata | None:
        return self._cached

    def save(self, repo: str, metadata: GitHubRepositoryMetadata) -> None:
        self.saved = (repo, metadata)


def test_github_star_count_provider_uses_and_saves_successful_lookup() -> None:
    metadata = GitHubRepositoryMetadata(
        repo="canonical/repo",
        github_repo_id=123,
        github_node_id="R_123",
        current_stars=100,
    )
    cache = FakeCache()
    provider = GitHubStarCountProvider(FakeGitHubClient(metadata), cache, ttl_seconds=3600)

    snapshot = provider.get_current_stars(_aggregate())

    assert snapshot.repo == "canonical/repo"
    assert snapshot.github_repo_id == 123
    assert snapshot.current_stars == 100
    assert snapshot.warnings == []
    assert cache.saved == ("owner/repo", metadata)


def test_github_star_count_provider_uses_cached_metadata() -> None:
    cached = GitHubRepositoryMetadata(
        repo="canonical/repo",
        github_repo_id=123,
        github_node_id="R_123",
        current_stars=100,
    )
    provider = GitHubStarCountProvider(
        FakeGitHubClient(GitHubRepoNotFoundError()),
        FakeCache(cached),
        3600,
    )

    snapshot = provider.get_current_stars(_aggregate())


    assert snapshot.repo == "canonical/repo"
    assert snapshot.current_stars == 100
    assert snapshot.warnings == []


def test_github_star_count_provider_falls_back_on_not_found() -> None:
    provider = GitHubStarCountProvider(
        FakeGitHubClient(GitHubRepoNotFoundError()),
        FakeCache(),
        3600,
    )

    snapshot = provider.get_current_stars(_aggregate())

    assert snapshot.current_stars == 25
    assert snapshot.warnings == [
        "GitHub repository metadata was not found; using StarScout count denominator."
    ]


def test_github_star_count_provider_falls_back_on_rate_limit() -> None:
    provider = GitHubStarCountProvider(FakeGitHubClient(GitHubRateLimitError()), FakeCache(), 3600)

    snapshot = provider.get_current_stars(_aggregate())

    assert snapshot.current_stars == 25
    assert snapshot.warnings == [
        "GitHub repository metadata is rate limited; using StarScout count denominator."
    ]


def _aggregate() -> RepoAggregateRecord:
    return RepoAggregateRecord(
        repo="owner/repo",
        suspected_non_legit_stars=25,
        low_activity_count=20,
        lockstep_count=10,
        overlap_count=5,
        analyzed_through="2025-01-01",
    )
