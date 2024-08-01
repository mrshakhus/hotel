import shutil
import pandas as pd
from fastapi import APIRouter, UploadFile

from app.csv_files.dao import SCV_files


router = APIRouter(
    prefix = "/csv_files",
    tags = ["Загрузка csv файлов"]
)


def save_file_retutn_df(file: UploadFile, file_name: str):
    file_path = f"app/static/csv_files/{file_name}.csv"
    with open(file_path, "wb+") as file_object:
        shutil.copyfileobj(file.file, file_object)

    df = pd.read_csv(file_path, delimiter=';', encoding='utf-8')
    return df


@router.post("/hotels")
async def upload_hotels_csv_file(file: UploadFile):
    df = save_file_retutn_df(file, "hotels")
    await SCV_files.add_hotels(df)


@router.post("/rooms")
async def upload_rooms_csv_file(file: UploadFile):
    df = save_file_retutn_df(file, "rooms")
    await SCV_files.add_rooms(df)

    

