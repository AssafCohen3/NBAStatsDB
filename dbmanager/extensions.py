import datetime
import http.client
import logging
import os
import sys
from logging import LogRecord
from logging.handlers import TimedRotatingFileHandler
from typing import Optional
from flask.json import JSONEncoder
from dbmanager.DBManager import DbManager
from dbmanager.tasks.TaskAnnouncer import TaskAnnouncer


db_manager: Optional[DbManager] = DbManager()
announcer = TaskAnnouncer()


class CustomJSONEncoder(JSONEncoder):
    def default(self, obj):
        try:
            if isinstance(obj, datetime.date):
                return obj.isoformat()
            iterable = iter(obj)
        except TypeError:
            pass
        else:
            return list(iterable)
        return JSONEncoder.default(self, obj)


class SocketIOFilter(logging.Filter):
    def filter(self, record: LogRecord) -> bool:
        message = record.args[0] if len(record.args) > 0 else ''
        return not \
            (message.startswith('GET /socket.io') or
             message.startswith('POST /socket.io'))


class MyTimedRotatingFileHandler(TimedRotatingFileHandler):

    def __init__(self, filename: str, *args, **kwargs) -> None:
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        super().__init__(filename, *args, **kwargs)


def setup_logging(file_name):
    # the file handler receives all messages from level DEBUG on up, regardless
    file_handler = MyTimedRotatingFileHandler(
        'logs/' + file_name + ".log",
        when="midnight"
    )
    file_handler.setLevel(logging.DEBUG)
    handlers = [file_handler]

    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setLevel(logging.INFO)
    handlers.append(stream_handler)

    logging.getLogger("requests").setLevel(logging.DEBUG)
    logging.getLogger("requests.").setLevel(logging.DEBUG)

    http.client.HTTPConnection.debuglevel = 1
    http_client_logger = logging.getLogger("http.client")

    def print_to_log(*args):
        http_client_logger.debug(" ".join(args))
    http.client.print = print_to_log

    logformat = "%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s] %(name)s:  %(message)s"
    logging.basicConfig(
        format=logformat, datefmt="%Y-%m-%d %H:%M:%S",
        handlers=handlers, level=logging.DEBUG
    )
