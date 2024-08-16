from datetime import date
from app.exceptions import InvalidDatesException, MoreThan30DaysException, ServiceUnavailableException, UnexpectedErrorException
from app.logger import logger
from sqlalchemy.exc import SQLAlchemyError


def handle_exception(exception, expecting_exception, extra, msg=""):
    if isinstance(exception, expecting_exception):
        logger.error(msg, extra, exc_info=True)
        raise exception


def handle_db_exception(e: Exception, extra: dict):
    if isinstance(e, SQLAlchemyError):
        msg = "Database Exception: Cannot get info"
        logger.error(msg, extra=extra, exc_info=True)
        raise ServiceUnavailableException
    else:
        msg = "Unknown Exception: Cannot get info"
        logger.error(msg, extra=extra, exc_info=True)
        raise UnexpectedErrorException
    

def validate_dates(date_from: date, date_to: date):
    if date_from >= date_to:
        raise InvalidDatesException
    elif (date_to - date_from).days > 30:
        raise MoreThan30DaysException