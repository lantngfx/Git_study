# coding: utf-8

import os
import yaml


class YamlLoader(yaml.Loader):

    def __init__(self, stream):
        super(YamlLoader, self).__init__(stream)
        self._root = os.path.split(stream.name)[0]

    def include(self, node):
        filename = os.path.join(self._root, self.construct_scalar(node))
        with open(filename, 'rb') as f:
            return yaml.load(f, YamlLoader)


YamlLoader.add_constructor('!include', YamlLoader.include)


class YamlConfig(object):

    def __init__(self, path):
        self._config = {}
        with open(path, 'rb') as f:
            self._config = yaml.load(f, Loader=YamlLoader)

    def get(self, section, key, default=None):
        try:
            return self._config[section][key]
        except (KeyError, IndexError):
            return default

    def getint(self, section, key, default=0):
        try:
            return int(self._config[section][key])
        except (KeyError, IndexError):
            return default

    def getlist(self, section):
        return list(self._config[section])

    def __getitem__(self, section):
        return self._config[section]


class _OptionValue(object):
    UNSET = object()

    def __init__(self, default=None):
        self._value = _OptionValue.UNSET
        self._default = default

    def set(self, value):
        self._value = value

    def value(self):
        return self._default if self._value is _OptionValue.UNSET else self._value

    @property
    def default(self):
        return self._default

    @default.setter
    def default(self, default):
        self._default = default


class Options(object):

    def __init__(self):
        self.__dict__['_options'] = {}

    @staticmethod
    def _normalize_name(name):
        return name.replace('_', '-')

    def __getattr__(self, name):
        name = self._normalize_name(name)
        if isinstance(self._options.get(name), _OptionValue):
            return self._options[name].value()
        raise AttributeError("Unrecognized option %r" % name)

    def __setattr__(self, name, value):
        name = self._normalize_name(name)
        if isinstance(self._options.get(name), _OptionValue):
            self._options[name].set(value)
        else:
            _option = _OptionValue()
            _option.set(value)
            self._options[name] = _option

    def __contains__(self, name):
        return self._normalize_name(name) in self._options

    def __getitem__(self, name):
        return self.__getattr__(name)

    def __setitem__(self, name, value):
        self.__setattr__(name, value)

    def define(self, name, default):
        name = self._normalize_name(name)
        if name in self._options:
            self._options[name].default = default
        else:
            _option = _OptionValue(default=default)
            self._options[name] = _option


options = Options()
