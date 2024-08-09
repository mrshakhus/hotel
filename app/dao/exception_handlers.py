from app.exceptions import ServiceUnavailableException, UnexpectedErrorException
from app.logger import logger
from sqlalchemy.exc import SQLAlchemyError

def handle_db_exception(e: Exception, extra: dict):
    if isinstance(e, SQLAlchemyError):
        msg = "Database Exception: Cannot get info"
        logger.error(msg, extra=extra, exc_info=True)
        raise ServiceUnavailableException
    else:
        msg = "Unknown Exception: Cannot get info"
        logger.error(msg, extra=extra, exc_info=True)
        raise UnexpectedErrorException