from typing import Annotated

from fastapi import APIRouter, Depends, Path, Response
from pydantic import BaseModel, Field

from starscout_api.core.db import connect_postgres
from starscout_api.core.settings import get_settings
from starscout_api.github.client import GitHubClient
from starscout_api.integrity.models import StarIntegrityResult
from starscout_api.integrity.service import StarIntegrityService
from starscout_api.integrity.star_counts import GitHubStarCountProvider
from starscout_api.persistence.postgres.repositories import (
    PostgresGitHubRepoCache,
    PostgresRepoAggregateRepository,
)

router = APIRouter()

OwnerPath = Annotated[
    str,
    Path(pattern=r"^[A-Za-z0-9](?:[A-Za-z0-9-]{0,37}[A-Za-z0-9])?$", max_length=39),
]
RepoPath = Annotated[str, Path(pattern=r"^[A-Za-z0-9_.-]+$", max_length=100)]


class IntegrityBreakdownResponse(BaseModel):
    low_activity: int = Field(alias="lowActivity")
    lockstep: int
    overlap: int

    model_config = {"populate_by_name": True}


class StarIntegrityResponse(BaseModel):
    repo: str
    analyzed: bool
    github_repo_id: int | None = Field(alias="githubRepoId")
    current_stars: int | None = Field(alias="currentStars")
    suspected_non_legit_stars: int | None = Field(alias="suspectedNonLegitStars")
    estimated_legit_stars: int | None = Field(alias="estimatedLegitStars")
    suspected_non_legit_percent: float | None = Field(alias="suspectedNonLegitPercent")
    breakdown: IntegrityBreakdownResponse | None
    analyzed_through: str | None = Field(alias="analyzedThrough")
    data_source: str = Field(alias="dataSource")
    warnings: list[str]

    model_config = {"populate_by_name": True}


def get_star_integrity_service() -> StarIntegrityService:
    settings = get_settings()
    connection = connect_postgres()
    return StarIntegrityService(
        PostgresRepoAggregateRepository(connection),
        GitHubStarCountProvider(
            GitHubClient(token=settings.github_token),
            PostgresGitHubRepoCache(connection),
            settings.github_repo_cache_ttl_seconds,
        ),
    )


@router.get(
    "/repos/{owner}/{repo}/star-integrity",
    response_model=StarIntegrityResponse,
    response_model_by_alias=True,
    tags=["repos"],
)
def get_star_integrity(
    owner: OwnerPath,
    repo: RepoPath,
    response: Response,
    service: Annotated[StarIntegrityService, Depends(get_star_integrity_service)],
) -> StarIntegrityResult:
    max_age = get_settings().api_cache_max_age_seconds
    response.headers["Cache-Control"] = f"public, max-age={max_age}"
    return service.get_integrity(f"{owner}/{repo}")
