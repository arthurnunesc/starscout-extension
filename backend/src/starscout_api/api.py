import re
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from starscout_api.core.db import connect_postgres
from starscout_api.integrity.models import StarIntegrityResult
from starscout_api.integrity.service import StarIntegrityService
from starscout_api.persistence.postgres.repositories import PostgresRepoAggregateRepository

router = APIRouter()

_REPO_PART_PATTERN = re.compile(r"^[A-Za-z0-9_.-]+$")


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
    connection = connect_postgres()
    return StarIntegrityService(PostgresRepoAggregateRepository(connection))


@router.get(
    "/repos/{owner}/{repo}/star-integrity",
    response_model=StarIntegrityResponse,
    response_model_by_alias=True,
    tags=["repos"],
)
def get_star_integrity(
    owner: str,
    repo: str,
    service: Annotated[StarIntegrityService, Depends(get_star_integrity_service)],
) -> StarIntegrityResult:
    if not _is_valid_repo_part(owner) or not _is_valid_repo_part(repo):
        raise HTTPException(status_code=422, detail="Invalid GitHub owner or repo name.")

    return service.get_integrity(f"{owner}/{repo}")


def _is_valid_repo_part(value: str) -> bool:
    return bool(value) and len(value) <= 100 and bool(_REPO_PART_PATTERN.fullmatch(value))
