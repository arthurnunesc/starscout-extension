from collections.abc import Iterable, Iterator
from typing import Protocol

from pymongo import MongoClient

from starscout_api.importer.models import RawSuspiciousStar, SuspiciousSource


class StarScoutSource(Protocol):
    def iter_low_activity(self) -> Iterable[RawSuspiciousStar]: ...

    def iter_lockstep(self) -> Iterable[RawSuspiciousStar]: ...


class FixtureStarScoutSource:
    def __init__(
        self,
        low_activity: Iterable[dict[str, object]],
        lockstep: Iterable[dict[str, object]],
    ) -> None:
        self._low_activity = list(low_activity)
        self._lockstep = list(lockstep)

    def iter_low_activity(self) -> Iterator[RawSuspiciousStar]:
        yield from _normalize_records(self._low_activity, SuspiciousSource.LOW_ACTIVITY)

    def iter_lockstep(self) -> Iterator[RawSuspiciousStar]:
        yield from _normalize_records(self._lockstep, SuspiciousSource.LOCKSTEP)


class MongoStarScoutSource:
    def __init__(self, mongo_url: str, database_name: str) -> None:
        self._mongo_url = mongo_url
        self._database_name = database_name

    def iter_low_activity(self) -> Iterator[RawSuspiciousStar]:
        with MongoClient(self._mongo_url) as client:
            collection = client[self._database_name]["low_activity_stars"]
            query = {"low_activity": True}
            projection = {"repo": 1, "actor": 1, "starred_at": 1}
            cursor = collection.find(query, projection)
            yield from _normalize_records(cursor, SuspiciousSource.LOW_ACTIVITY)

    def iter_lockstep(self) -> Iterator[RawSuspiciousStar]:
        with MongoClient(self._mongo_url) as client:
            collection = client[self._database_name]["clustered_stars"]
            query = {"clustered": True}
            projection = {"repo": 1, "actor": 1, "starred_at": 1}
            cursor = collection.find(query, projection)
            yield from _normalize_records(cursor, SuspiciousSource.LOCKSTEP)


def _normalize_records(
    records: Iterable[dict[str, object]],
    source: SuspiciousSource,
) -> Iterator[RawSuspiciousStar]:
    for record in records:
        repo = str(record["repo"]).strip()
        actor = str(record["actor"]).strip()
        starred_at = str(record["starred_at"]).strip()

        if not repo or not actor or not starred_at:
            continue

        yield RawSuspiciousStar(
            repo=repo,
            actor=actor,
            starred_at=starred_at,
            source=source,
        )
