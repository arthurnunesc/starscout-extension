from dataclasses import dataclass


@dataclass(frozen=True)
class RepoAggregateRecord:
    repo: str
    suspected_non_legit_stars: int
    low_activity_count: int
    lockstep_count: int
    overlap_count: int
    analyzed_through: str


@dataclass(frozen=True)
class IntegrityBreakdown:
    low_activity: int
    lockstep: int
    overlap: int


@dataclass(frozen=True)
class StarIntegrityResult:
    repo: str
    analyzed: bool
    github_repo_id: int | None
    current_stars: int | None
    suspected_non_legit_stars: int | None
    estimated_legit_stars: int | None
    suspected_non_legit_percent: float | None
    breakdown: IntegrityBreakdown | None
    analyzed_through: str | None
    data_source: str
    warnings: list[str]
