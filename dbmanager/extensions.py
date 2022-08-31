import datetime
from typing import Optional

from flask.json import JSONEncoder

from dbmanager.DBManager import DbManager

db_manager: Optional[DbManager] = DbManager()


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
