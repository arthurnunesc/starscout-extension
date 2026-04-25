from dataclasses import dataclass

from starscout_api.importer.aggregate import aggregate_repo_facts
from starscout_api.importer.dedupe import dedupe_suspicious_stars
from starscout_api.importer.models import ImportSnapshot
from starscout_api.importer.source import StarScoutSource
from starscout_api.persistence.postgres.repositories import ImportStore


@dataclass(frozen=True)
class ImportResult:
    snapshot: ImportSnapshot


class ImportService:
    def __init__(self, source: StarScoutSource, store: ImportStore) -> None:
        self._source = source
        self._store = store

    def run(self, source_name: str, source_version: str, analyzed_through: str) -> ImportResult:
        low_activity = list(self._source.iter_low_activity())
        lockstep = list(self._source.iter_lockstep())
        facts = dedupe_suspicious_stars([*low_activity, *lockstep])
        aggregates = aggregate_repo_facts(facts, analyzed_through)
        snapshot = ImportSnapshot(
            source_name=source_name,
            source_version=source_version,
            analyzed_through=analyzed_through,
            low_activity_count=len(low_activity),
            lockstep_count=len(lockstep),
            deduped_fact_count=len(facts),
            aggregate_count=len(aggregates),
        )

        self._store.setup_schema()
        self._store.persist(snapshot=snapshot, facts=facts, aggregates=aggregates)

        return ImportResult(snapshot=snapshot)
