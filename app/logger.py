import json
import logging
import os
from datetime import datetime, timezone
import sys

from pythonjsonlogger import jsonlogger

from app.config import settings

logger = logging.getLogger()

logHandler = logging.StreamHandler(sys.stdout)
logHandler.stream = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)


class CustomJsonFormatter(jsonlogger.JsonFormatter):
    
    def format(self, record):
        log_record = self._get_log_record(record)
        return json.dumps(log_record, ensure_ascii=False)
    
    def _get_log_record(self, record):
        """
        Преобразует запись в словарь.
        """
        log_record = {
            'timestamp': datetime.fromtimestamp(record.created, tz=timezone.utc).strftime('%Y-%m-%dT%H:%M:%S.%fZ'),
            'level': record.levelname,
            'message': record.getMessage(),
            'module': record.module,
            'funcName': record.funcName,
            'exc_info': self.formatException(record.exc_info) if record.exc_info else None,
            'taskName': getattr(record, 'taskName', None),
            'token': getattr(record, 'token', None),
        }
        return log_record


formatter = CustomJsonFormatter(
    "%(timestamp)s %(level)s %(message)s %(module)s %(funcName)s"
)

logHandler.setFormatter(formatter)
logger.addHandler(logHandler)
logger.setLevel(settings.LOG_LEVEL)
