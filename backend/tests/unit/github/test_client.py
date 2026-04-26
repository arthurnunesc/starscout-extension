import httpx
import pytest

from starscout_api.github.client import GitHubClient, GitHubRateLimitError, GitHubRepoNotFoundError


class FakeResponse:
    def __init__(self, status_code: int, payload: dict | None = None) -> None:
        self.status_code = status_code
        self._payload = payload or {}

    def json(self) -> dict:
        return self._payload


def test_github_client_fetches_repository_metadata(monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_get(*args, **kwargs) -> FakeResponse:
        return FakeResponse(
            200,
            {
                "full_name": "canonical/repo",
                "id": 123,
                "node_id": "R_123",
                "stargazers_count": 42,
            },
        )

    monkeypatch.setattr(httpx, "get", fake_get)

    metadata = GitHubClient(token="token").get_repository("owner/repo")

    assert metadata.repo == "canonical/repo"
    assert metadata.github_repo_id == 123
    assert metadata.github_node_id == "R_123"
    assert metadata.current_stars == 42


def test_github_client_reports_not_found(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(httpx, "get", lambda *args, **kwargs: FakeResponse(404))

    with pytest.raises(GitHubRepoNotFoundError):
        GitHubClient().get_repository("owner/missing")


def test_github_client_reports_rate_limit(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(httpx, "get", lambda *args, **kwargs: FakeResponse(403))

    with pytest.raises(GitHubRateLimitError):
        GitHubClient().get_repository("owner/repo")
