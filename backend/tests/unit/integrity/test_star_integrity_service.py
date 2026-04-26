from starscout_api.integrity.models import RepoAggregateRecord
from starscout_api.integrity.service import StarIntegrityService


class FakeAggregateRepository:
    def __init__(self, aggregate: RepoAggregateRecord | None) -> None:
        self._aggregate = aggregate

    def get_by_repo(self, repo: str) -> RepoAggregateRecord | None:
        return self._aggregate if self._aggregate and self._aggregate.repo == repo else None


class FixedStarCountProvider:
    def __init__(self, current_stars: int) -> None:
        self._current_stars = current_stars

    def get_current_stars(self, aggregate: RepoAggregateRecord) -> int:
        return self._current_stars


def test_integrity_result_contains_aggregate_metrics_and_percentage() -> None:
    aggregate = RepoAggregateRecord(
        repo="owner/repo",
        suspected_non_legit_stars=25,
        low_activity_count=20,
        lockstep_count=10,
        overlap_count=5,
        analyzed_through="2025-01-01",
    )
    service = StarIntegrityService(
        FakeAggregateRepository(aggregate),
        FixedStarCountProvider(current_stars=100),
    )

    result = service.get_integrity("owner/repo")

    assert result.analyzed is True
    assert result.repo == "owner/repo"
    assert result.current_stars == 100
    assert result.suspected_non_legit_stars == 25
    assert result.estimated_legit_stars == 75
    assert result.suspected_non_legit_percent == 25.0
    assert result.breakdown is not None
    assert result.breakdown.low_activity == 20
    assert result.breakdown.lockstep == 10
    assert result.breakdown.overlap == 5
    assert result.analyzed_through == "2025-01-01"
    assert result.warnings == []


def test_integrity_result_reports_not_analyzed_without_zero_claim() -> None:
    service = StarIntegrityService(FakeAggregateRepository(None))

    result = service.get_integrity("owner/missing")

    assert result.analyzed is False
    assert result.suspected_non_legit_stars is None
    assert result.suspected_non_legit_percent is None
    assert result.breakdown is None
    assert result.warnings == ["Repository has no StarScout suspicious-star aggregate."]


def test_integrity_result_clamps_estimated_legit_stars_when_suspicious_exceeds_total() -> None:
    aggregate = RepoAggregateRecord(
        repo="owner/repo",
        suspected_non_legit_stars=25,
        low_activity_count=20,
        lockstep_count=10,
        overlap_count=5,
        analyzed_through="2025-01-01",
    )
    service = StarIntegrityService(
        FakeAggregateRepository(aggregate),
        FixedStarCountProvider(current_stars=10),
    )

    result = service.get_integrity("owner/repo")
    assert result.estimated_legit_stars == 0
    assert result.suspected_non_legit_percent == 250.0
    assert result.warnings == ["Current star count is lower than suspected suspicious-star count."]
