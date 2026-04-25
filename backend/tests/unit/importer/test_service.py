from dataclasses import dataclass, field

from starscout_api.importer.models import ImportSnapshot, RepoAggregate, SuspiciousStarFact
from starscout_api.importer.service import ImportService
from starscout_api.importer.source import FixtureStarScoutSource


@dataclass
class InMemoryImportStore:
    schema_initialized: bool = False
    snapshots: list[ImportSnapshot] = field(default_factory=list)
    facts: list[SuspiciousStarFact] = field(default_factory=list)
    aggregates: list[RepoAggregate] = field(default_factory=list)

    def setup_schema(self) -> None:
        self.schema_initialized = True

    def persist(
        self,
        snapshot: ImportSnapshot,
        facts: list[SuspiciousStarFact],
        aggregates: list[RepoAggregate],
    ) -> None:
        self.snapshots = [snapshot]
        self.facts = facts
        self.aggregates = aggregates


def test_service_collects_snapshot_and_persists_deduped_results() -> None:
    source = FixtureStarScoutSource(
        low_activity=[
            {"repo": "owner/repo", "actor": "alice", "starred_at": "2024-01-01T00:00:00Z"},
            {"repo": "owner/repo", "actor": "bob", "starred_at": "2024-01-02T00:00:00Z"},
        ],
        lockstep=[
            {"repo": "owner/repo", "actor": "alice", "starred_at": "2024-01-01T00:00:00Z"},
        ],
    )
    store = InMemoryImportStore()

    result = ImportService(source=source, store=store).run(
        source_name="fixture",
        source_version="v1",
        analyzed_through="2025-01-01",
    )

    assert store.schema_initialized is True
    assert result.snapshot.low_activity_count == 2
    assert result.snapshot.lockstep_count == 1
    assert result.snapshot.deduped_fact_count == 2
    assert result.snapshot.aggregate_count == 1
    assert len(store.facts) == 2
    assert store.aggregates[0].overlap_count == 1
