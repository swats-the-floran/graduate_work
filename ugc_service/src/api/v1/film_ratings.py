from typing import Annotated, List
from uuid import UUID

from fastapi import APIRouter, Depends, Query

from models.models import FilmAvgRatingModel, SavedDataModel
from services.film_ratings_service import FilmRatingsService, get_service
from services.auth_service import security_jwt

router = APIRouter()


@router.post(
    path='',
    response_model=SavedDataModel,
)
async def create_film_rating(
    # user: Annotated[dict, Depends(security_jwt)],
    user_id: UUID,
    movie_id: UUID,
    score: int,
    service: FilmRatingsService = Depends(get_service),
) -> SavedDataModel:
    return await service.create({'user_id': str(user_id), 'movie_id': str(movie_id), 'score': score})


@router.get(
    path='',
    response_model=list[FilmAvgRatingModel],
)
async def get_tilm_rating_list(
    # user: Annotated[dict, Depends(security_jwt)],
    film_ids: Annotated[List[UUID], Query()],
    service: FilmRatingsService = Depends(get_service),
) -> list[FilmAvgRatingModel]:
    return await service.get_list([str(film_id) for film_id in film_ids])


@router.delete(
    path='',
)
async def film_rating(
    # user: Annotated[dict, Depends(security_jwt)],
    user_id: UUID,
    movie_id: UUID,
    service: FilmRatingsService = Depends(get_service),
) -> dict[str, str]:
    await service.delete({'user_id': str(user_id), 'movie_id': str(movie_id)})

    return {'ok': 'deleted'}

