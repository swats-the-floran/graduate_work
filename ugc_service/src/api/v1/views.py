from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends

from models.models import SavedDataModel, ViewModel
from services.views_service import ViewsService, get_service
from services.auth_service import security_jwt

router = APIRouter()


@router.post(
    path='',
    response_model=SavedDataModel,
)
async def views(
    user: Annotated[dict, Depends(security_jwt)],
    user_id: UUID,
    movie_id: UUID,
    chunk: int,
    service: ViewsService = Depends(get_service),
) -> SavedDataModel:
    return await service.create({'user_id': str(user_id), 'movie_id': str(movie_id), 'chunk': chunk})


@router.get(
    path='',
    response_model=list[ViewModel],
)
async def get_tilm_rating_list(
    user: Annotated[dict, Depends(security_jwt)],
    user_id: UUID,
    movie_id: UUID,
    service: ViewsService = Depends(get_service),
) -> list[ViewModel]:
    return await service.get_list({'user_id': str(user_id), 'movie_id': str(movie_id)})

