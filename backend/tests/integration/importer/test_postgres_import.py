import os

import psycopg
import pytest

from starscout_api.importer.service import ImportService
from starscout_api.importer.source import FixtureStarScoutSource
from starscout_api.persistence.postgres.repositories import PostgresImportStore

pytestmark = pytest.mark.integration


def test_postgres_import_is_idempotent_for_same_source_dataset() -> None:
    database_url = os.getenv("TEST_POSTGRES_DSN")
    if not database_url:
        pytest.skip("TEST_POSTGRES_DSN is not set")

    source = FixtureStarScoutSource(
        low_activity=[
            {"repo": "owner/repo", "actor": "alice", "starred_at": "2024-01-01T00:00:00Z"},
            {"repo": "owner/repo", "actor": "bob", "starred_at": "2024-01-02T00:00:00Z"},
        ],
        lockstep=[
            {"repo": "owner/repo", "actor": "alice", "starred_at": "2024-01-01T00:00:00Z"},
            {"repo": "owner/repo", "actor": "carol", "starred_at": "2024-01-03T00:00:00Z"},
        ],
    )

    with psycopg.connect(database_url) as connection:
        _truncate_phase_two_tables(connection)
        store = PostgresImportStore(connection)
        service = ImportService(source=source, store=store)

        service.run(source_name="fixture", source_version="v1", analyzed_through="2025-01-01")
        service.run(source_name="fixture", source_version="v1", analyzed_through="2025-01-01")

        with connection.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM suspicious_star_facts")
            facts_count = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM repo_aggregates")
            aggregate_count = cursor.fetchone()[0]
            cursor.execute(
                """
                SELECT
                    low_activity_count,
                    lockstep_count,
                    overlap_count,
                    suspected_non_legit_stars
                FROM repo_aggregates
                WHERE repo = %s
                """,
                ("owner/repo",),
            )
            aggregate_row = cursor.fetchone()
            cursor.execute("SELECT COUNT(*) FROM import_runs")
            import_run_count = cursor.fetchone()[0]

    assert facts_count == 3
    assert aggregate_count == 1
    assert aggregate_row == (2, 2, 1, 3)
    assert import_run_count == 1


def _truncate_phase_two_tables(connection: psycopg.Connection) -> None:
    with connection.cursor() as cursor:
        cursor.execute(
            """
            DROP TABLE IF EXISTS repo_aggregates;
            DROP TABLE IF EXISTS suspicious_star_facts;
            DROP TABLE IF EXISTS import_runs;
            """
        )
    connection.commit()
