from collections.abc import Sequence
from datetime import UTC, datetime, timedelta
from typing import Protocol

from psycopg import Connection

from starscout_api.github.client import GitHubRepositoryMetadata
from starscout_api.importer.models import ImportSnapshot, RepoAggregate, SuspiciousStarFact
from starscout_api.integrity.models import RepoAggregateRecord
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


class PostgresRepoAggregateRepository:
    def __init__(self, connection: Connection) -> None:
        self._connection = connection

    def get_by_repo(self, repo: str) -> RepoAggregateRecord | None:
        with self._connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    repo,
                    suspected_non_legit_stars,
                    low_activity_count,
                    lockstep_count,
                    overlap_count,
                    analyzed_through
                FROM repo_aggregates
                WHERE repo = %s
                """,
                (repo,),
            )
            row = cursor.fetchone()

        if row is None:
            return None

        return RepoAggregateRecord(
            repo=row[0],
            suspected_non_legit_stars=row[1],
            low_activity_count=row[2],
            lockstep_count=row[3],
            overlap_count=row[4],
            analyzed_through=row[5],
        )


class PostgresGitHubRepoCache:
    def __init__(self, connection: Connection) -> None:
        self._connection = connection

    def get_fresh(self, repo: str, ttl: timedelta) -> GitHubRepositoryMetadata | None:
        with self._connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    canonical_full_name,
                    github_repo_id,
                    github_node_id,
                    stargazers_count,
                    fetched_at
                FROM github_repo_cache
                WHERE repo = %s
                """,
                (repo,),
            )
            row = cursor.fetchone()

        if row is None:
            return None

        fetched_at = row[4]
        if fetched_at.tzinfo is None:
            fetched_at = fetched_at.replace(tzinfo=UTC)
        if fetched_at < datetime.now(UTC) - ttl:
            return None

        return GitHubRepositoryMetadata(
            repo=row[0],
            github_repo_id=row[1],
            github_node_id=row[2],
            current_stars=row[3],
        )

    def save(self, repo: str, metadata: GitHubRepositoryMetadata) -> None:
        with self._connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO github_repo_cache (
                    repo,
                    canonical_full_name,
                    github_repo_id,
                    github_node_id,
                    stargazers_count,
                    fetched_at
                )
                VALUES (%s, %s, %s, %s, %s, NOW())
                ON CONFLICT (repo)
                DO UPDATE SET
                    canonical_full_name = EXCLUDED.canonical_full_name,
                    github_repo_id = EXCLUDED.github_repo_id,
                    github_node_id = EXCLUDED.github_node_id,
                    stargazers_count = EXCLUDED.stargazers_count,
                    fetched_at = NOW()
                """,
                (
                    repo,
                    metadata.repo,
                    metadata.github_repo_id,
                    metadata.github_node_id,
                    metadata.current_stars,
                ),
            )
        self._connection.commit()
