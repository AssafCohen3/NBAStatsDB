import datetime
import logging
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


def init_socket(app):
    socketio.init_app(app, async_mode='threading', cors_allowed_origins="*", logger=False, engineio_logger=False, log_output=False)
    logging.getLogger('socketio').setLevel(logging.ERROR)
    logging.getLogger('engineio').setLevel(logging.ERROR)
    # logging.getLogger('geventwebsocket.handler').setLevel(logging.ERROR)
