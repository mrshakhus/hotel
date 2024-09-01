from fastapi import APIRouter, Depends, Request, UploadFile
from fastapi_versioning import version
from pandas import DataFrame

from app.csv_files.dependencies import save_file_return_df
from app.csv_files.service import SCV_filesService
from app.limiter import limiter


router = APIRouter(
    prefix = "/csv_files",
    tags = ["Загрузка CSV файлов"]
)


@router.post("/hotels", status_code=201)
@version(1)
@limiter.limit("1/second")
async def upload_hotels_csv_file(
    request: Request,
    df: DataFrame = Depends(save_file_return_df)
):
    await SCV_filesService.add_hotels(df)


@router.post("/rooms", status_code=201)
@version(1)
@limiter.limit("1/second")
async def upload_rooms_csv_file(
    request: Request,
    df: DataFrame = Depends(save_file_return_df)
):
    await SCV_filesService.add_rooms(df)