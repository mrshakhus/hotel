from fastapi import APIRouter, Depends, Request, UploadFile
from fastapi_versioning import version
from pandas import DataFrame

from app.csv_files.dao import SCV_filesDAO
from app.csv_files.dependencies import save_file_return_df
from app.limiter import limiter


router = APIRouter(
    prefix = "/csv_files",
    tags = ["Загрузка CSV файлов"]
)


@router.post("/hotels")
@version(1)
@limiter.limit("1/second")
async def upload_hotels_csv_file(
    request: Request,
    df: DataFrame = Depends(save_file_return_df)
):
    await SCV_filesDAO.add_hotels(df)


@router.post("/rooms")
@version(1)
@limiter.limit("1/second")
async def upload_rooms_csv_file(
    request: Request,
    df: DataFrame = Depends(save_file_return_df)
):
    await SCV_filesDAO.add_rooms(df)