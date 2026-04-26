from fastapi.testclient import TestClient

from starscout_api.api import get_star_integrity_service
from starscout_api.integrity.models import RepoAggregateRecord, StarCountSnapshot
from starscout_api.integrity.service import StarIntegrityService
from starscout_api.main import create_app


class FakeAggregateRepository:
    def __init__(self, aggregates: dict[str, RepoAggregateRecord]) -> None:
        self._aggregates = aggregates

    def get_by_repo(self, repo: str) -> RepoAggregateRecord | None:
        return self._aggregates.get(repo)


class FixedStarCountProvider:
    def get_current_stars(self, aggregate: RepoAggregateRecord) -> StarCountSnapshot:
        return StarCountSnapshot(
            repo="canonical/repo",
            github_repo_id=123,
            current_stars=100,
            warnings=[],
        )


def test_star_integrity_api_returns_analyzed_repo_metrics() -> None:
    app = create_app()
    app.dependency_overrides[get_star_integrity_service] = lambda: StarIntegrityService(
        FakeAggregateRepository(
            {
                "owner/repo": RepoAggregateRecord(
                    repo="owner/repo",
                    suspected_non_legit_stars=25,
                    low_activity_count=20,
                    lockstep_count=10,
                    overlap_count=5,
                    analyzed_through="2025-01-01",
                )
            }
        ),
        FixedStarCountProvider(),
    )
    client = TestClient(app)

    response = client.get("/repos/owner/repo/star-integrity")

    assert response.status_code == 200
    assert response.json() == {
        "repo": "canonical/repo",
        "analyzed": True,
        "githubRepoId": 123,
        "currentStars": 100,
        "suspectedNonLegitStars": 25,
        "estimatedLegitStars": 75,
        "suspectedNonLegitPercent": 25.0,
        "breakdown": {"lowActivity": 20, "lockstep": 10, "overlap": 5},
        "analyzedThrough": "2025-01-01",
        "dataSource": "StarScout Zenodo dataset",
        "warnings": [],
    }


def test_star_integrity_api_returns_not_analyzed_state() -> None:
    app = create_app()
    app.dependency_overrides[get_star_integrity_service] = lambda: StarIntegrityService(
        FakeAggregateRepository({})
    )
    client = TestClient(app)

    response = client.get("/repos/owner/missing/star-integrity")

    assert response.status_code == 200
    assert response.json()["analyzed"] is False
    assert response.json()["suspectedNonLegitStars"] is None
    assert response.json()["breakdown"] is None
    assert response.json()["warnings"] == [
        "Repository has no StarScout suspicious-star aggregate."
    ]


def test_star_integrity_api_rejects_invalid_owner_or_repo() -> None:
    app = create_app()
    app.dependency_overrides[get_star_integrity_service] = lambda: StarIntegrityService(
        FakeAggregateRepository({})
    )
    client = TestClient(app)

    response = client.get("/repos/bad%20owner/repo/star-integrity")

    assert response.status_code == 422
