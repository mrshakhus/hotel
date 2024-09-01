from pandas import DataFrame

from app.csv_files.dao import SCV_filesDAO
from app.exceptions import BookingAPIException
from app.utils.exception_handlers import handle_exception, handle_unexpected_exception


class SCV_filesService():
    @staticmethod
    async def add_hotels(
        df: DataFrame
    ) -> None:
        try:
            await SCV_filesDAO.add_hotels(df)

        except(
            BookingAPIException,
            Exception
        ) as e:
            extra = {
                "df": df
            }
            handle_exception(e, BookingAPIException, extra)
            handle_unexpected_exception(e, extra)

    
    @staticmethod
    async def add_rooms(
        df: DataFrame
    ) -> None:
        try:
            await SCV_filesDAO.add_rooms(df)

        except(
            BookingAPIException,
            Exception
        ) as e:
            extra = {
                "df": df
            }
            handle_exception(e, BookingAPIException, extra)
            handle_unexpected_exception(e, extra)