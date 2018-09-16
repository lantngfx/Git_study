# coding: utf-8

import os
import datetime
import logging
from raven.conf import setup_logging

from utils.sentry_client import handler


class LevelFilter(logging.Filter):
    """
    http://stackoverflow.com/a/7447596/190597 (robert)
    """
    def __init__(self, level):
        super(LevelFilter, self).__init__()
        self.level = level

    def filter(self, record):
        return record.levelno == self.level


def gen_handler(log_path, error=False):
    log_path = log_path
    str_format = "%(asctime)s: %(name)s:%(levelname)s:%(message)s"
    date_fmt = "%Y-%m-%dT%H:%M:%S"

    if error:
        name = "{0}error.log-{1}".format(log_path, datetime.date.today())
        handler = logging.FileHandler(filename=name)
        handler.setLevel(level=logging.ERROR)
        handler.addFilter(LevelFilter(logging.ERROR))
    else:
        name = "{0}info.log-{1}".format(log_path, datetime.date.today())
        handler = logging.FileHandler(filename=name)
        handler.setLevel(level=logging.INFO)
        handler.addFilter(LevelFilter(logging.INFO))

    formatter = logging.Formatter(str_format, date_fmt)
    handler.setFormatter(formatter)

    return handler


class BaseLogger(object):

    def __init__(self, name):
        self.logger = logging.getLogger(name)
        self.level = logging.INFO

    def gen_logger(self, log_path):
        # set produce log level
        self.logger.setLevel(self.level)

        # gen two handler and set it on the logger
        handler_info = gen_handler(log_path)
        handler_error = gen_handler(log_path, error=True)
        self.logger.addHandler(handler_info)
        self.logger.addHandler(handler_error)
        # inti sentry
        handler.setLevel(logging.ERROR)
        setup_logging(handler)

        return self.logger


def _get_log_path():
    log_path = '{}/log/'.format(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    if not os.path.isdir(log_path):
        os.makedirs(log_path)
    return log_path


logger = BaseLogger('medivh').gen_logger(_get_log_path())
