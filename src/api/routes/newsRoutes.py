from fastapi import APIRouter, Form, UploadFile, File, Depends
from fastapi_versionizer.versionizer import api_version

from src.core.common.result import Result
from src.core.models.news import NewsInputModel, NewsOutputModel
from src.core.interfaces.services.newsService import INewsService
from src.core.injectorDependency import get_news_service

router = APIRouter(prefix="/news", tags=["News"])


@router.post("/run", response_model=Result[NewsOutputModel])
@api_version(1)
async def run(dto: NewsInputModel,
    service: INewsService = Depends(get_news_service)
):
    result = await service.run(dto)

    if not result.success:
        raise ValueError(result.message)
    
    return result