from datetime import date
from typing import Any, Dict
from app.exceptions import InvalidDatesException, MoreThan30DaysException, UnexpectedError, ServiceUnavailableException
from app.logger import logger
from sqlalchemy.exc import SQLAlchemyError


def handle_exception(
    exception: Exception,
    expecting_exception: Exception, 
    extra: dict[str, Any] = None, 
    msg: str = ""
):
    if isinstance(exception, expecting_exception):
        logger.error(msg, extra, exc_info=True)
        raise exception
    

def handle_unexpected_exception(
    exception: Exception, 
    extra: dict[str, Any] = None
):
    extra["exception"] = type(exception).__name__
    logger.error(msg="", extra=extra, exc_info=True)
    raise UnexpectedError


def handle_db_exception(
    exception: Exception, 
    extra: dict[str, Any]
):
    if isinstance(exception, SQLAlchemyError):
        logger.error(msg="", extra=extra, exc_info=True)
        raise ServiceUnavailableException
    

def validate_dates(
    date_from: date, 
    date_to: date
):
    if date_from >= date_to:
        raise InvalidDatesException
    elif (date_to - date_from).days > 30:
        raise MoreThan30DaysException