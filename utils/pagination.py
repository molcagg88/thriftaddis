from fastapi import Query
from db.models import PaginationModel


def getPaginationParams(limit: int = Query(30, ge=1, le=100, description="Max listings per page"),
                        offset: int = Query(0, ge=0, detail="Number of items to skip"))->PaginationModel:
    return PaginationModel(limit=limit, offset=offset)