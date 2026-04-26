from typing import Protocol

from starscout_api.integrity.models import (
    IntegrityBreakdown,
    RepoAggregateRecord,
    StarCountSnapshot,
    StarIntegrityResult,
)

DATA_SOURCE = "StarScout Zenodo dataset"


class RepoAggregateRepository(Protocol):
    def get_by_repo(self, repo: str) -> RepoAggregateRecord | None: ...


class StarCountProvider(Protocol):
    def get_current_stars(self, aggregate: RepoAggregateRecord) -> StarCountSnapshot: ...


class AggregateStarCountProvider:
    def get_current_stars(self, aggregate: RepoAggregateRecord) -> StarCountSnapshot:
        return StarCountSnapshot(
            repo=aggregate.repo,
            github_repo_id=None,
            current_stars=aggregate.suspected_non_legit_stars,
            warnings=[],
        )


class StarIntegrityService:
    def __init__(
        self,
        aggregates: RepoAggregateRepository,
        star_counts: StarCountProvider | None = None,
    ) -> None:
        self._aggregates = aggregates
        self._star_counts = star_counts or AggregateStarCountProvider()

    def get_integrity(self, repo: str) -> StarIntegrityResult:
        aggregate = self._aggregates.get_by_repo(repo)
        if aggregate is None:
            return StarIntegrityResult(
                repo=repo,
                analyzed=False,
                github_repo_id=None,
                current_stars=None,
                suspected_non_legit_stars=None,
                estimated_legit_stars=None,
                suspected_non_legit_percent=None,
                breakdown=None,
                analyzed_through=None,
                data_source=DATA_SOURCE,
                warnings=["Repository has no StarScout suspicious-star aggregate."],
            )

        star_count = self._star_counts.get_current_stars(aggregate)
        current_stars = star_count.current_stars
        suspected = aggregate.suspected_non_legit_stars
        warnings = list(star_count.warnings)
        if current_stars < suspected:
            warnings.append("Current star count is lower than suspected suspicious-star count.")

        return StarIntegrityResult(
            repo=star_count.repo,
            analyzed=True,
            github_repo_id=star_count.github_repo_id,
            current_stars=current_stars,
            suspected_non_legit_stars=suspected,
            estimated_legit_stars=max(current_stars - suspected, 0),
            suspected_non_legit_percent=_percentage(suspected, current_stars),
            breakdown=IntegrityBreakdown(
                low_activity=aggregate.low_activity_count,
                lockstep=aggregate.lockstep_count,
                overlap=aggregate.overlap_count,
            ),
            analyzed_through=aggregate.analyzed_through,
            data_source=DATA_SOURCE,
            warnings=warnings,
        )


def _percentage(numerator: int, denominator: int) -> float:
    if denominator <= 0:
        return 0.0
    return round((numerator / denominator) * 100, 2)
