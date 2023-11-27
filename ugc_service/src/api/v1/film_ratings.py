from typing import Annotated

from fastapi import APIRouter, Depends

from models.models import FilmRatingModel, SavedDataModel
from services.film_ratings_service import FilmRatingsService, get_service
from services.auth_service import security_jwt

router = APIRouter()


@router.post(
    path='',
    response_model=SavedDataModel,
)
async def create_film_rating(
    user: Annotated[dict, Depends(security_jwt)],
    user_id: int,
    movie_id: int,
    score: int,
    service: FilmRatingsService = Depends(get_service),
) -> SavedDataModel:
    return await service.create({'user_id': user_id, 'movie_id': movie_id, 'score': score})


@router.get(
    path='',
    response_model=list[FilmRatingModel],
)
async def get_tilm_rating_list(
    user: Annotated[dict, Depends(security_jwt)],
    movie_id: int,
    service: FilmRatingsService = Depends(get_service),
) -> list[FilmRatingModel]:
    return await service.get_list({'movie_id': movie_id})


@router.delete(
    path='',
)
async def film_rating(
    user: Annotated[dict, Depends(security_jwt)],
    user_id: int,
    movie_id: int,
    service: FilmRatingsService = Depends(get_service),
) -> dict[str, str]:
    await service.delete({'user_id': user_id, 'movie_id': movie_id})

    return {'ok': 'deleted'}

