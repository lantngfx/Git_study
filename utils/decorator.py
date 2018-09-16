# coding: utf-8

import functools


class ClassProperty(object):

    def __init__(self, func_get, func_set=None):
        self.func_get = func_get
        self.func_set = func_set

    def __get__(self, instance, owner=None):
        if owner is None:
            owner = type(instance)
        return self.func_get.__get__(instance, owner)()

    def __set__(self, instance, value):
        if not self.func_set:
            raise AttributeError("Can't set attribute.")

    def setter(self, func):
        if not isinstance(func, (classmethod, staticmethod)):
            func = classmethod(func)
        self.func_set = func
        return self


def class_property(func):
    if not isinstance(func, (classmethod, staticmethod)):
        func = classmethod(func)
    return ClassProperty(func)


def lazy_property(func):

    attr_name = '_lazy_{}'.format(func.__name__)

    @property
    @functools.wraps(func)
    def _inner(self):
        if not hasattr(self, attr_name):
            setattr(self, attr_name, func(self))
        return getattr(self, attr_name)

    return _inner


def cache_classmethod(func):
    """该装饰器，用于修饰缓存生成的数据"""

    attr_name = '_lazy_{}'.format(func.__name__)

    @functools.wraps(func)
    def _inner(cls, *args, **kwargs):
        if not hasattr(cls, attr_name):
            setattr(cls, attr_name, func(cls, *args, **kwargs))
        return getattr(cls, attr_name)
    return classmethod(_inner)
