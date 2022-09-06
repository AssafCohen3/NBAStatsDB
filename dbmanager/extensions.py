import datetime
import logging
from logging import LogRecord
from typing import Optional
from flask.json import JSONEncoder
from dbmanager.DBManager import DbManager
from dbmanager.tasks.TaskAnnouncer import TaskAnnouncer

db_manager: Optional[DbManager] = DbManager()
announcer = TaskAnnouncer()
logging.basicConfig(level=logging.INFO)


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
