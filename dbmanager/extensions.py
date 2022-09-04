import datetime
import json
import logging
from logging import LogRecord
from typing import Optional

from flask.json import JSONEncoder
from flask_socketio import SocketIO

from dbmanager.DBManager import DbManager

db_manager: Optional[DbManager] = DbManager()
socketio = SocketIO()


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


def init_socket(app):
    socketio.init_app(app, cors_allowed_origins="*", async_mode='threading')
    # socketio.init_app(app, async_mode='threading', cors_allowed_origins="*")
    # logging.getLogger('socketio').setLevel(logging.ERROR)
    # logging.getLogger('engineio').setLevel(logging.ERROR)
    logging.basicConfig(level=logging.INFO)
    logging.getLogger("werkzeug").addFilter(SocketIOFilter())
