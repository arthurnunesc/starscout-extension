from starscout_api.core.db import connect_postgres
from starscout_api.core.settings import get_settings
from starscout_api.importer.service import ImportService
from starscout_api.importer.source import MongoStarScoutSource
from starscout_api.persistence.postgres.repositories import PostgresImportStore


def main() -> None:
    settings = get_settings()
    source = MongoStarScoutSource(settings.mongodb_url, settings.mongodb_database)

    with connect_postgres(settings) as connection:
        service = ImportService(source=source, store=PostgresImportStore(connection))
        result = service.run(
            source_name="starscout-mongodb",
            source_version=settings.analyzed_through,
            analyzed_through=settings.analyzed_through,
        )

    print(
        "Imported "
        f"{result.snapshot.deduped_fact_count} suspicious facts across "
        f"{result.snapshot.aggregate_count} repositories"
    )


if __name__ == "__main__":
    main()
