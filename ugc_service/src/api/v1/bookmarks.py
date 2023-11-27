from typing import Annotated

from fastapi import APIRouter, Depends

from models.models import BookmarkModel, SavedDataModel
from services.bookmarks_service import BookmarksService, get_service
from services.auth_service import security_jwt

router = APIRouter()


@router.post(
    path='',
    response_model=SavedDataModel,
)
async def add_bookmark(
    user: Annotated[dict, Depends(security_jwt)],
    user_id: int,
    movie_id: int,
    service: BookmarksService = Depends(get_service),
) -> SavedDataModel:
    return await service.create({'user_id': user_id, 'movie_id': movie_id})


@router.get(
    path='',
    response_model=list[BookmarkModel],
)
async def get_bookmark_list(
    user: Annotated[dict, Depends(security_jwt)],
    user_id: int,
    service: BookmarksService = Depends(get_service),
) -> list[BookmarkModel]:
    return await service.get_list({'user_id': user_id})


@router.delete(
    path='',
)
async def delete_bookmark(
    user: Annotated[dict, Depends(security_jwt)],
    user_id: int,
    movie_id: int,
    service: BookmarksService = Depends(get_service),
) -> dict[str, str]:
    await service.delete({'user_id': user_id, 'movie_id': movie_id})

    return {'ok': 'deleted'}

