from collections.abc import Iterable

from starscout_api.importer.models import RawSuspiciousStar, SuspiciousSource, SuspiciousStarFact


def dedupe_suspicious_stars(records: Iterable[RawSuspiciousStar]) -> list[SuspiciousStarFact]:
    merged: dict[tuple[str, str, str], SuspiciousStarFact] = {}

    for record in records:
        key = (record.repo, record.actor, record.starred_at)
        existing = merged.get(key)

        low_activity = record.source == SuspiciousSource.LOW_ACTIVITY
        lockstep = record.source == SuspiciousSource.LOCKSTEP

        if existing is None:
            merged[key] = SuspiciousStarFact(
                repo=record.repo,
                actor=record.actor,
                starred_at=record.starred_at,
                low_activity=low_activity,
                lockstep=lockstep,
            )
            continue

        merged[key] = SuspiciousStarFact(
            repo=existing.repo,
            actor=existing.actor,
            starred_at=existing.starred_at,
            low_activity=existing.low_activity or low_activity,
            lockstep=existing.lockstep or lockstep,
        )

    return sorted(merged.values(), key=lambda fact: (fact.repo, fact.actor, fact.starred_at))
