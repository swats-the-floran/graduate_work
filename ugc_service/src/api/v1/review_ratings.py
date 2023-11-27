from typing import Annotated

from fastapi import APIRouter, Depends

from models.models import ReviewRatingModel, SavedDataModel
from services.review_ratings_service import ReviewRatingsService, get_service
from services.auth_service import security_jwt

router = APIRouter()


@router.post(
    path='',
    response_model=SavedDataModel,
)
async def create_review_rating(
    user: Annotated[dict, Depends(security_jwt)],
    user_id: int,
    author_id: int,
    movie_id: int,
    score: int,
    service: ReviewRatingsService = Depends(get_service),
) -> SavedDataModel:
    return await service.create({'user_id': user_id, 'author_id': author_id, 'movie_id': movie_id, 'score': score})


@router.get(
    path='',
    response_model=list[ReviewRatingModel],
)
async def get_tilm_rating_list(
    user: Annotated[dict, Depends(security_jwt)],
    user_id: int,
    movie_id: int,
    service: ReviewRatingsService = Depends(get_service),
) -> list[ReviewRatingModel]:
    return await service.get_list({'user_id': user_id, 'movie_id': movie_id})


@router.delete(
    path='',
)
async def film_rating(
    user: Annotated[dict, Depends(security_jwt)],
    user_id: int,
    author_id: int,
    movie_id: int,
    service: ReviewRatingsService = Depends(get_service),
) -> dict[str, str]:
    await service.delete({'user_id': user_id, 'author_id': author_id, 'movie_id': movie_id})

    return {'ok': 'deleted'}

