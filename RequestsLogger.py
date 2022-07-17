import logging
from logging import LogRecord


class MyLoggingHandler(logging.Handler):

    def emit(self, record: LogRecord) -> None:
        if record.funcName == '_make_request' and str(record.args[6]).startswith('2'):
            print('%s %s://%s%s' % (record.args[3], record.args[0], record.args[1], record.args[4]))
