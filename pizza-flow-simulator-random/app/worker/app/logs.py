''' Logs singleton '''
import json
import logging
import os
from logging import Formatter

class JsonFormatter(Formatter):
    ''' A JSON formatter for logs '''
    def __init__(self):
        super().__init__()

    def format(self, record):
        json_record = {}
        json_record["message"] = record.getMessage()
        json_record['level'] = record.levelname or record.levelno or None
        if "method" in record.__dict__:
            json_record["method"] = record.__dict__["method"]
        if "req" in record.__dict__:
            json_record["req"] = record.__dict__["req"]
        if "res" in record.__dict__:
            json_record["res"] = record.__dict__["res"]
        if record.levelno == logging.ERROR and record.exc_info:
            json_record["err"] = self.formatException(record.exc_info)
        return json.dumps(json_record)

logger = logging.getLogger(__name__)
handler = logging.StreamHandler()
if os.getenv("LOG_FORMAT") == "json":
    handler.setFormatter(JsonFormatter())
handler.setLevel(10)
logger.setLevel(10)
logger.handlers = [handler]
