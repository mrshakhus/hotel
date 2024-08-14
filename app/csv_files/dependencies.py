import shutil
from fastapi import UploadFile
import pandas as pd


def save_file_return_df(file: UploadFile, file_name: str):
    file_path = f"app/static/csv_files/{file_name}.csv"
    with open(file_path, "wb+") as file_object:
        shutil.copyfileobj(file.file, file_object)

    df = pd.read_csv(file_path, delimiter=';', encoding='utf-8')
    return df