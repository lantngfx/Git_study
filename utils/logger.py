# coding: utf-8

import os
import logging
from datetime import datetime
from logging.handlers import RotatingFileHandler, BaseRotatingHandler


class TimeSplitRotatingHandler(BaseRotatingHandler):

    def __init__(self, filename, rollover_fmt='%Y%m%d', mode='a', encoding=None, delay=0):
        self._last_log_suffix = self._get_log_suffix()
        self.rollover_fmt = rollover_fmt
        self._tmp_log_suffix = ''
        super(TimeSplitRotatingHandler, self).__init__(filename=filename, mode=mode, encoding=encoding, delay=delay)

    def _get_log_suffix(self, ts=0):
        if ts <= 0:
            return datetime.now().strftime(self.rollover_fmt)
        return datetime.fromtimestamp(ts).strftime(self.rollover_fmt)

    def doRollover(self):
        if self.stream:
            self.stream.close()
            self.stream = None
        root, ext = os.path.splitext(self.baseFilename)
        dfn = root + '_%s' % self._last_log_suffix + ext
        if os.path.exists(dfn):
            os.remove(dfn)
        if os.path.exists(self.baseFilename):
            os.rename(self.baseFilename, dfn)
        self._last_log_suffix, self._tmp_log_suffix = self._tmp_log_suffix, ''
        if not self.delay:
            self.stream = self._open()

    def shouldRollover(self, record):
        if self.stream is None:                 # delay was set...
            self.stream = self._open()
        suffix = self._get_log_suffix(record.created)
        if self._last_log_suffix == suffix:
            return 0
        self._tmp_log_suffix = suffix
        return 1


class Log(object):

    formatter = logging.Formatter('%(asctime)s [%(levelname)s] {%(module)s.py line %(lineno)d} %(message)s')
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    rotating_file_handler_max_bytes = 1024 * 1024 * 1024
    rotating_file_handler_backup_count = 5

    def __init__(self, name, level=logging.DEBUG):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)

    def add_stream_log(self, level=logging.DEBUG):
        if not self._has_handler(logging.StreamHandler):
            self.stream_handler.setLevel(level)
            self.logger.addHandler(self.stream_handler)

    def add_file_log(self, filename, level=logging.INFO):
        if not self._has_handler(RotatingFileHandler):
            file_handler = RotatingFileHandler(filename, maxBytes=self.rotating_file_handler_max_bytes,
                                               backupCount=self.rotating_file_handler_backup_count)
            file_handler.setFormatter(self.formatter)
            file_handler.setLevel(level)
            self.logger.addHandler(file_handler)

    def _has_handler(self, handler):
        for h in self.logger.handlers:
            if type(h) == handler:
                return True
        return False

    def get_logger(self):
        return self.logger


def get_logger(name=None, stream=True, filename=None, level=None):
    level = level or logging.DEBUG
    _log = Log(name=name, level=level)
    if stream:
        _log.add_stream_log(logging.INFO)
    if filename:
        _log.add_file_log(filename, logging.DEBUG)
    return _log.get_logger()


log = get_logger(None, stream=True)
