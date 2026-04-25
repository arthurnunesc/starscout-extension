from collections.abc import Sequence
from typing import Protocol

from psycopg import Connection

from starscout_api.importer.models import ImportSnapshot, RepoAggregate, SuspiciousStarFact
from starscout_api.persistence.postgres.schema import SCHEMA_SQL


class ImportStore(Protocol):
    def setup_schema(self) -> None: ...

    def persist(
        self,
        snapshot: ImportSnapshot,
        facts: Sequence[SuspiciousStarFact],
        aggregates: Sequence[RepoAggregate],
    ) -> None: ...


class PostgresImportStore:
    def __init__(self, connection: Connection) -> None:
        self._connection = connection

    def setup_schema(self) -> None:
        with self._connection.cursor() as cursor:
            cursor.execute(SCHEMA_SQL)
        self._connection.commit()

    def persist(
        self,
        snapshot: ImportSnapshot,
        facts: Sequence[SuspiciousStarFact],
        aggregates: Sequence[RepoAggregate],
    ) -> None:
        with self._connection.transaction():
            with self._connection.cursor() as cursor:
                self._upsert_import_run(cursor, snapshot)
                self._upsert_facts(cursor, facts)
                self._upsert_aggregates(cursor, aggregates)

    @staticmethod
    def _upsert_import_run(cursor, snapshot: ImportSnapshot) -> None:
        cursor.execute(
            """
            INSERT INTO import_runs (
                source_name,
                source_version,
                analyzed_through,
                low_activity_count,
                lockstep_count,
                deduped_fact_count,
                aggregate_count,
                status
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (source_name, source_version)
            DO UPDATE SET
                analyzed_through = EXCLUDED.analyzed_through,
                low_activity_count = EXCLUDED.low_activity_count,
                lockstep_count = EXCLUDED.lockstep_count,
                deduped_fact_count = EXCLUDED.deduped_fact_count,
                aggregate_count = EXCLUDED.aggregate_count,
                status = EXCLUDED.status,
                updated_at = NOW()
            """,
            (
                snapshot.source_name,
                snapshot.source_version,
                snapshot.analyzed_through,
                snapshot.low_activity_count,
                snapshot.lockstep_count,
                snapshot.deduped_fact_count,
                snapshot.aggregate_count,
                snapshot.status,
            ),
        )

    @staticmethod
    def _upsert_facts(cursor, facts: Sequence[SuspiciousStarFact]) -> None:
        for fact in facts:
            cursor.execute(
                """
                INSERT INTO suspicious_star_facts (repo, actor, starred_at, low_activity, lockstep)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (repo, actor, starred_at)
                DO UPDATE SET
                    low_activity = suspicious_star_facts.low_activity OR EXCLUDED.low_activity,
                    lockstep = suspicious_star_facts.lockstep OR EXCLUDED.lockstep
                """,
                (fact.repo, fact.actor, fact.starred_at, fact.low_activity, fact.lockstep),
            )

    @staticmethod
    def _upsert_aggregates(cursor, aggregates: Sequence[RepoAggregate]) -> None:
        for aggregate in aggregates:
            cursor.execute(
                """
                INSERT INTO repo_aggregates (
                    repo,
                    suspected_non_legit_stars,
                    low_activity_count,
                    lockstep_count,
                    overlap_count,
                    analyzed_through
                )
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (repo)
                DO UPDATE SET
                    suspected_non_legit_stars = EXCLUDED.suspected_non_legit_stars,
                    low_activity_count = EXCLUDED.low_activity_count,
                    lockstep_count = EXCLUDED.lockstep_count,
                    overlap_count = EXCLUDED.overlap_count,
                    analyzed_through = EXCLUDED.analyzed_through
                """,
                (
                    aggregate.repo,
                    aggregate.suspected_non_legit_stars,
                    aggregate.low_activity_count,
                    aggregate.lockstep_count,
                    aggregate.overlap_count,
                    aggregate.analyzed_through,
                ),
            )
