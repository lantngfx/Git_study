# coding: utf-8

import uuid
import urllib
import datetime
from decimal import Decimal
from bson.objectid import ObjectId
import json
import json.encoder


class JSONEncoder(json.JSONEncoder):

    DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S'
    DATE_FORMAT = '%Y-%m-%d'

    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return obj.strftime(self.DATETIME_FORMAT)
        if isinstance(obj, datetime.date):
            return obj.strftime(self.DATE_FORMAT)
        if isinstance(obj, Decimal):
            return StringTool.format_decimal(obj)
        if isinstance(obj, ObjectId):
            return str(obj)
        return super(JSONEncoder, self).default(obj)

    def encode(self, o):
        if isinstance(o, str):
            o = StringTool.u(o, charset=self.encoding)
        if isinstance(o, unicode):
            if self.ensure_ascii:
                json.encoder.encode_basestring_ascii(o)
            else:
                json.encoder.encode_basestring(o)
        chunks = self.iterencode(o, _one_shot=True)
        if not isinstance(chunks, (list, tuple)):
            chunks = list(chunks)
        return ''.join(map(lambda s: StringTool.s(s, charset=self.encoding), chunks))


class StringTool(object):

    @classmethod
    def s(cls, u, strip=True, charset='utf-8', default=''):
        """将unicode转换为str"""
        if not isinstance(u, (str, unicode)):
            return default
        if isinstance(u, unicode):
            u = u.encode(charset)
        return u.strip() if strip else u

    @classmethod
    def u(cls, s, strip=True, charset='utf-8', default=u''):
        """将str转换为unicode"""
        if not isinstance(s, (str, unicode)):
            return default
        if isinstance(s, str):
            s = s.decode(charset)
        return s.strip() if strip else s

    @classmethod
    def right_index(cls, s, sub, start=None, end=None):
        """从右边查找字符串中该字符出现的位置,未找到是返回-1"""
        if isinstance(s, (str, unicode)):
            try:
                return s.rindex(sub, start, end)
            except (ValueError, TypeError):
                return -1
        return -1

    @classmethod
    def index(cls, s, sub, start=None, end=None):
        """从左边查找字符串中字符出现的位置,未找到是返回-1"""
        if isinstance(s, (str, unicode)):
            try:
                return s.index(sub, start, end)
            except (ValueError, TypeError):
                return -1
        return -1

    @classmethod
    def url_encode(cls, query, do_seq=0):
        return urllib.urlencode(cls.s(query), do_seq)

    @classmethod
    def _split_key_value(cls, s, sep='=', default=''):
        l = s.split(sep, 1)
        if len(l) == 2:
            return l[0], urllib.unquote(l[1])
        return l[0], default

    @classmethod
    def url_decode(cls, s, sep='&'):
        s = cls.s(s)
        if not isinstance(s, str):
            return {}
        data = {}
        for s in s.split(sep):
            k, v = cls._split_key_value(s)
            data[k] = v
        return data

    @classmethod
    def to_int(cls, s, default=0):
        if not s:
            return default
        try:
            return int(s)
        except ValueError:
            return default

    @classmethod
    def to_float(cls, s, default=0):
        s = cls.s(s)
        if not s:
            return default
        try:
            return float(s)
        except ValueError:
            return default

    @classmethod
    def to_bool(cls, obj, false={0, '0', 'n', 'no', 'false', 'none'}):
        if not obj:
            return False
        if isinstance(obj, (str, unicode)):
            obj = cls.s(obj).lower()
        if isinstance(obj, (int, float, long)):
            obj = cls.to_int(obj)
        if obj in false:
            return False
        return True

    @classmethod
    def format_decimal(cls, d):
        if isinstance(d, Decimal):
            ds = str(d)
            if ds.isdigit():
                return cls.to_int(ds)
            else:
                return cls.to_float(ds)
        if isinstance(d, (float, int, long)):
            return d
        return 0

    @classmethod
    def format_number(cls, number):
        if isinstance(number, Decimal):
            return cls.format_decimal(number)
        if isinstance(number, (int, long)):
            return number
        if isinstance(number, float):
            return int(number) if number.is_integer() else number
        if isinstance(number, (str, unicode)):
            number = cls.s(number)
            if number.isdigit():
                return cls.to_int(number)
            return cls.to_float(number)
        return 0

    @classmethod
    def round_number(cls, number, bit=2):
        """保留小数点后bit位"""
        number = cls.format_number(number)
        if not isinstance(number, (int, long, float)):
            raise ValueError('%r is not a number' % number)
        return round(number, bit) if bit > 0 else cls.to_int(round(number, bit))

    @classmethod
    def json_dumps(cls, obj, ensure_ascii=False, _cls=JSONEncoder, **kwargs):
        return cls.s(json.dumps(obj, ensure_ascii=ensure_ascii, cls=_cls, **kwargs))

    @classmethod
    def json_loads(cls, s):
        try:
            return json.loads(s)
        except (ValueError, TypeError):
            return {}

    @classmethod
    def uuid(cls):
        return uuid.uuid1().hex

    @classmethod
    def sid(cls):
        return str(ObjectId())
        # return hashlib.md5(os.urandom(24) + str(time.time())).hexdigest()

    @classmethod
    def dict_get(cls, obj, key, default=None):
        if key in obj:
            return obj[key]
        return default
        # try:
        #     return obj[key]
        # except KeyError:
        #     return default
