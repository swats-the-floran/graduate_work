from typing import Annotated, List
from uuid import UUID

from fastapi import APIRouter, Depends, Query

from models.models import ReviewAvgRatingModel, SavedDataModel
from services.review_ratings_service import ReviewRatingsService, get_service
from services.auth_service import security_jwt

router = APIRouter()


@router.post(
    path='',
    response_model=SavedDataModel,
)
async def create_review_rating(
    # user: Annotated[dict, Depends(security_jwt)],
    review_id: UUID,
    user_id: UUID,
    score: int,
    service: ReviewRatingsService = Depends(get_service),
) -> SavedDataModel:
    return await service.create({'user_id': str(user_id), 'review_id': str(review_id), 'score': score})


@router.get(
    path='',
    response_model=list[ReviewAvgRatingModel],
)
async def get_review_rating_list(
    # user: Annotated[dict, Depends(security_jwt)],
    review_ids: Annotated[List[UUID], Query()],
    service: ReviewRatingsService = Depends(get_service),
) -> list[ReviewAvgRatingModel]:
    return await service.get_list([str(review_id) for review_id in review_ids])


@router.delete(
    path='',
)
async def review_rating(
    # user: Annotated[dict, Depends(security_jwt)],
    review_id: UUID,
    user_id: UUID,
    service: ReviewRatingsService = Depends(get_service),
) -> dict[str, str]:
    await service.delete({'user_id': str(user_id), 'review_id': str(review_id)})

    return {'ok': 'deleted'}

