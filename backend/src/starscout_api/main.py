from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from starscout_api.api import router
from starscout_api.core.rate_limit import RepoIntegrityRateLimitMiddleware
from starscout_api.core.settings import Settings, get_settings


def create_app(settings: Settings | None = None) -> FastAPI:
    app_settings = settings or get_settings()
    app = FastAPI(
        title=app_settings.app_name,
        version=app_settings.app_version,
        docs_url="/docs" if app_settings.enable_docs else None,
        redoc_url="/redoc" if app_settings.enable_docs else None,
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origin_regex=app_settings.cors_allow_origin_regex,
        allow_credentials=False,
        allow_methods=["GET", "OPTIONS"],
        allow_headers=["Accept", "Content-Type"],
    )
    app.add_middleware(
        RepoIntegrityRateLimitMiddleware,
        requests_per_minute=app_settings.repo_integrity_rate_limit_per_minute,
    )

    @app.get("/health", tags=["system"])
    def health() -> dict[str, str]:
        return {"status": "ok", "service": app_settings.app_name}

    app.include_router(router)

    return app


app = create_app()
