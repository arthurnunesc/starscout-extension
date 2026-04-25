from starscout_api.importer.aggregate import aggregate_repo_facts
from starscout_api.importer.models import SuspiciousStarFact


def test_aggregate_counts_are_derived_from_deduped_facts() -> None:
    facts = [
        SuspiciousStarFact(
            repo="owner/repo-a",
            actor="alice",
            starred_at="2024-01-01T00:00:00Z",
            low_activity=True,
            lockstep=True,
        ),
        SuspiciousStarFact(
            repo="owner/repo-a",
            actor="bob",
            starred_at="2024-01-02T00:00:00Z",
            low_activity=True,
            lockstep=False,
        ),
        SuspiciousStarFact(
            repo="owner/repo-b",
            actor="carol",
            starred_at="2024-01-03T00:00:00Z",
            low_activity=False,
            lockstep=True,
        ),
    ]

    aggregates = aggregate_repo_facts(facts, analyzed_through="2025-01-01")

    assert aggregates[0].repo == "owner/repo-a"
    assert aggregates[0].suspected_non_legit_stars == 2
    assert aggregates[0].low_activity_count == 2
    assert aggregates[0].lockstep_count == 1
    assert aggregates[0].overlap_count == 1
    assert aggregates[1].repo == "owner/repo-b"
    assert aggregates[1].suspected_non_legit_stars == 1
    assert aggregates[1].low_activity_count == 0
    assert aggregates[1].lockstep_count == 1
    assert aggregates[1].overlap_count == 0
