from dataclasses import dataclass
from enum import StrEnum


class SuspiciousSource(StrEnum):
    LOW_ACTIVITY = "low_activity"
    LOCKSTEP = "lockstep"


@dataclass(frozen=True)
class RawSuspiciousStar:
    repo: str
    actor: str
    starred_at: str
    source: SuspiciousSource


@dataclass(frozen=True)
class SuspiciousStarFact:
    repo: str
    actor: str
    starred_at: str
    low_activity: bool
    lockstep: bool


@dataclass(frozen=True)
class RepoAggregate:
    repo: str
    suspected_non_legit_stars: int
    low_activity_count: int
    lockstep_count: int
    overlap_count: int
    analyzed_through: str


@dataclass(frozen=True)
class ImportSnapshot:
    source_name: str
    source_version: str
    analyzed_through: str
    low_activity_count: int
    lockstep_count: int
    deduped_fact_count: int
    aggregate_count: int
    status: str = "completed"
