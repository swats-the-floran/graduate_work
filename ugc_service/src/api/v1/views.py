from typing import Annotated

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
    user_id: int,
    movie_id: int,
    chunk: int,
    service: ViewsService = Depends(get_service),
) -> SavedDataModel:
    return await service.create({'user_id': user_id, 'movie_id': movie_id, 'chunk': chunk})


@router.get(
    path='',
    response_model=list[ViewModel],
)
async def get_tilm_rating_list(
    user: Annotated[dict, Depends(security_jwt)],
    user_id: int,
    movie_id: int,
    service: ViewsService = Depends(get_service),
) -> list[ViewModel]:
    return await service.get_list({'user_id': user_id, 'movie_id':  movie_id})

