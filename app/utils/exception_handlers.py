from datetime import date
from typing import Dict
from app.exceptions import InvalidDatesException, MoreThan30DaysException, RuntimeException, ServiceUnavailableException, UnexpectedErrorException
from app.logger import logger
from sqlalchemy.exc import SQLAlchemyError


def handle_exception(
    exception: Exception,
    expecting_exception: Exception, 
    extra: Dict[str, any], 
    msg: str = ""
):
    if isinstance(exception, expecting_exception):
        logger.error(msg, extra, exc_info=True)
        raise exception
    

def handle_runtime_exception(
    exception: Exception, 
    extra: Dict[str, any]
):
    extra["exception"] = type(exception).__name__
    logger.error(msg="", extra=extra, exc_info=True)
    raise RuntimeException


def handle_db_exception(
    exception: Exception, 
    extra: Dict[str, any]
):
    if isinstance(exception, SQLAlchemyError):
        logger.error(msg="", extra=extra, exc_info=True)
        raise ServiceUnavailableException
    else:
        extra["exception"] = type(exception).__name__
        logger.error(msg="", extra=extra, exc_info=True)
        raise UnexpectedErrorException
    

def validate_dates(
    date_from: date, 
    date_to: date
):
    if date_from >= date_to:
        raise InvalidDatesException
    elif (date_to - date_from).days > 30:
        raise MoreThan30DaysException