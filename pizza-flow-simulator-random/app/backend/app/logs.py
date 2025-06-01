''' Logs singleton '''
import os
import json
import logging
from logging import Formatter
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request


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
        if 'sqs_body' in record.__dict__:
            json_record['sqs_body'] = record.__dict__['sqs_body']
        if record.levelno == logging.ERROR and record.exc_info:
            json_record["err"] = self.formatException(record.exc_info)
        return json.dumps(json_record)

class DevFormatter(Formatter):
    ''' For a better develop experience '''
    class bcolors:
        HEADER = '\033[95m'
        OKBLUE = '\033[94m'
        OKCYAN = '\033[96m'
        OKGREEN = '\033[92m'
        WARNING = '\033[93m'
        FAIL = '\033[91m'
        ENDC = '\033[0m'
        BOLD = '\033[1m'
        UNDERLINE = '\033[4m'
    def colorForLevel(self, level):
        rc = self.bcolors.OKGREEN
        if level > 20:
            rc = self.bcolors.WARNING
        if level > 30:
            rc = self.bcolors.FAIL
        return rc
    
    def format(self, record):
        json_record = {}
        msg = record.getMessage()
        json_record['level'] = record.levelname or record.levelno or None
        if "method" in record.__dict__:
            json_record["method"] = record.__dict__["method"]
        if "req" in record.__dict__:
            json_record["req"] = record.__dict__["req"]
        if "res" in record.__dict__:
            json_record["res"] = record.__dict__["res"]
        if record.levelno == logging.ERROR and record.exc_info:
            json_record["err"] = self.formatException(record.exc_info)
        #if record.args:
        
        prefix = self.colorForLevel(record.levelno)
        if hasattr(record, 'req'):
            method = record.req.get('method', 'GET')
            msg = f'{method} {record.req["endpoint"]} {record.res.get('status_code')}'
            if method == 'POST' or method == 'PUT':
                msg += f' {record.req["body"]}'
                prefix = self.bcolors.OKBLUE
            if method == 'DELETE' or record.res.get('status_code', 200) >= 400:
                prefix = self.bcolors.FAIL
            if record.levelno == logging.ERROR and record.exc_info:
                msg+= self.formatException(record.exc_info)
        return f'{prefix}{msg}{self.bcolors.ENDC}'


logger = logging.getLogger(__name__)
handler = logging.StreamHandler()
log_fmt = os.getenv('LOG_FMT', 'json')
if log_fmt == 'json':
    handler.setFormatter(JsonFormatter())
elif log_fmt == 'dev':
    handler.setFormatter(DevFormatter())
handler.setLevel(10)
logger.setLevel(10)
logger.handlers = [handler]

logging.getLogger("uvicorn.access").disabled = True

#pylint: disable-next=too-few-public-methods
class LogMiddleware(BaseHTTPMiddleware):
    ''' Middleware for Starlette '''
    async def dispatch(self, request: Request, call_next):
        try:
            body = None
            if log_fmt == 'dev':
                body = await request.body()
            
        except Exception as e:
            pass
        response = await call_next(request)
        logger.info(
            "HTTP request",
            extra={
                "req": {
                    "method": request.method,
                    "endpoint": str(request.url.path),
                    "headers": dict(request.headers),
                    "query": dict(request.query_params),
                    'body': body,
                },
                "res": { "status_code": response.status_code, },
                "method": "http"
            },
        )
        return response
