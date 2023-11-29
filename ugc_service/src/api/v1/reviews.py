from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends

from models.models import ReviewModel, SavedDataModel
from services.reviews_service import ReviewsService, get_service
from services.auth_service import security_jwt

router = APIRouter()


@router.post(
    path='',
    response_model=SavedDataModel,
)
async def reviews(
    user: Annotated[dict, Depends(security_jwt)],
    user_id: UUID,
    movie_id: UUID,
    review_text: str,
    score: int,
    service: ReviewsService = Depends(get_service),
) -> SavedDataModel:
    return await service.create({'user_id': str(user_id), 'movie_id': str(movie_id), 'review_text': review_text, 'score': score})


@router.get(
    path='',
    response_model=list[ReviewModel],
)
async def get_tilm_rating_list(
    user: Annotated[dict, Depends(security_jwt)],
    movie_id: UUID,
    service: ReviewsService = Depends(get_service),
) -> list[ReviewModel]:
    return await service.get_list({'movie_id': str(movie_id)})


@router.delete(
    path='',
)
async def film_rating(
    user: Annotated[dict, Depends(security_jwt)],
    user_id: UUID,
    movie_id: UUID,
    service: ReviewsService = Depends(get_service),
) -> dict[str, str]:
    await service.delete({'user_id': str(user_id), 'movie_id': str(movie_id)})

    return {'ok': 'deleted'}


@router.put(
    path='',
    response_model=list[SavedDataModel],
)
async def update_tilm_rating_list(
    user: Annotated[dict, Depends(security_jwt)],
    user_id: UUID,
    movie_id: UUID,
    review_text: str,
    score: int,
    service: ReviewsService = Depends(get_service),
) -> SavedDataModel:
    return await service.update({'user_id': str(user_id), 'movie_id': str(movie_id), 'review_text': review_text, 'score': score})

