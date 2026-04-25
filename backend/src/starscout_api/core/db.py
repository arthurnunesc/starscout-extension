import psycopg
from psycopg import Connection

from starscout_api.core.settings import Settings, get_settings


def connect_postgres(settings: Settings | None = None) -> Connection:
    app_settings = settings or get_settings()
    return psycopg.connect(app_settings.database_url)
