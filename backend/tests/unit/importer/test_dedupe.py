from starscout_api.importer.dedupe import dedupe_suspicious_stars
from starscout_api.importer.models import RawSuspiciousStar, SuspiciousSource


def test_dedupe_merges_low_activity_and_lockstep_on_same_key() -> None:
    records = [
        RawSuspiciousStar(
            repo="owner/repo",
            actor="alice",
            starred_at="2024-01-01T00:00:00Z",
            source=SuspiciousSource.LOW_ACTIVITY,
        ),
        RawSuspiciousStar(
            repo="owner/repo",
            actor="alice",
            starred_at="2024-01-01T00:00:00Z",
            source=SuspiciousSource.LOCKSTEP,
        ),
        RawSuspiciousStar(
            repo="owner/repo",
            actor="bob",
            starred_at="2024-01-02T00:00:00Z",
            source=SuspiciousSource.LOCKSTEP,
        ),
    ]

    facts = dedupe_suspicious_stars(records)

    assert len(facts) == 2
    assert facts[0].repo == "owner/repo"
    assert facts[0].actor == "alice"
    assert facts[0].low_activity is True
    assert facts[0].lockstep is True
    assert facts[1].actor == "bob"
    assert facts[1].low_activity is False
    assert facts[1].lockstep is True
