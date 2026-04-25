from collections.abc import Iterable

from starscout_api.importer.models import RepoAggregate, SuspiciousStarFact


def aggregate_repo_facts(
    facts: Iterable[SuspiciousStarFact],
    analyzed_through: str,
) -> list[RepoAggregate]:
    counters: dict[str, dict[str, int]] = {}

    for fact in facts:
        repo_counter = counters.setdefault(
            fact.repo,
            {
                "suspected_non_legit_stars": 0,
                "low_activity_count": 0,
                "lockstep_count": 0,
                "overlap_count": 0,
            },
        )

        repo_counter["suspected_non_legit_stars"] += 1
        if fact.low_activity:
            repo_counter["low_activity_count"] += 1
        if fact.lockstep:
            repo_counter["lockstep_count"] += 1
        if fact.low_activity and fact.lockstep:
            repo_counter["overlap_count"] += 1

    return [
        RepoAggregate(
            repo=repo,
            suspected_non_legit_stars=counts["suspected_non_legit_stars"],
            low_activity_count=counts["low_activity_count"],
            lockstep_count=counts["lockstep_count"],
            overlap_count=counts["overlap_count"],
            analyzed_through=analyzed_through,
        )
        for repo, counts in sorted(counters.items())
    ]
