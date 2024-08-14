from fastapi import APIRouter, Depends, UploadFile
from pandas import DataFrame

from app.csv_files.dao import SCV_filesDAO
from app.csv_files.dependencies import save_file_return_df


router = APIRouter(
    prefix = "/csv_files",
    tags = ["Загрузка CSV файлов"]
)


@router.post("/hotels")
async def upload_hotels_csv_file(df: DataFrame = Depends(save_file_return_df)):
    await SCV_filesDAO.add_hotels(df)


@router.post("/rooms")
async def upload_rooms_csv_file(df: DataFrame = Depends(save_file_return_df)):
    await SCV_filesDAO.add_rooms(df)

    

