# coding: utf-8

import time
import functools
import datetime as sys_datetime
from dateutil import parser
from string_tool import StringTool
from logger import log


class TimeTool(object):

    timedelta = sys_datetime.timedelta
    datetime = sys_datetime.datetime
    time = sys_datetime.time

    weeks_cn = ['周一',  '周二',  '周三',  '周四',  '周五',  '周六',  '周日']

    @classmethod
    def str_to_datetime(cls, s):
        """将日期字符串转换为 datetime 类型, 转换失败返回 None"""
        if isinstance(s, sys_datetime.date):
            return cls.date_to_datetime(s)
        if isinstance(s, sys_datetime.datetime):
            return s
        s = StringTool.s(s)
        if not isinstance(s, str) or not s:
            return None
        try:
            return parser.parse(s)
        except Exception, e:
            log.error('TimeTool str_to_datetime error %s, [%s]' % (e, s))
            return None

    @classmethod
    def date_to_datetime(cls, d):
        if type(d) == sys_datetime.date:
            return sys_datetime.datetime(year=d.year, month=d.month, day=d.day)
        return d

    @classmethod
    def datetime_to_str(cls, d, fmt='%Y-%m-%d %H:%M:%S'):
        """将 datetime 类型, 格式化为字符串, 格式化失败时返回 ''"""
        if not d:
            return ''
        return cls.date_to_datetime(d).strftime(fmt)

    @classmethod
    def datetime_to_millis(cls, d):
        """将 datetime 转换为时间戳"""
        if not d:
            return 0
        return int(time.mktime(cls.date_to_datetime(d).timetuple()) * 1000)

    @classmethod
    def millis_to_datetime(cls, millis):
        """时间戳（毫秒）转datetime"""
        if not millis:
            return None
        try:
            return sys_datetime.datetime.fromtimestamp(millis / 1000.0)
        except ValueError:
            return None

    @classmethod
    def str_to_millis(cls, s):
        """将日期字符串转换为时间戳"""
        return cls.datetime_to_millis(cls.str_to_datetime(s))

    @classmethod
    def millis_to_str(cls, millis, fmt='%Y-%m-%d %H:%M:%S'):
        """将时间戳转换为日期字符串"""
        return cls.datetime_to_str(cls.millis_to_datetime(millis), fmt=fmt)

    @classmethod
    def seconds_to_str(cls, seconds, fmt='%Y-%m-%d %H:%M:%S'):
        return cls.millis_to_str((seconds or 0) * 1000, fmt=fmt)

    @classmethod
    def seconds_to_datetime(cls, seconds):
        return cls.millis_to_datetime((seconds or 0) * 1000)

    @classmethod
    def incr(cls, d, days=1):
        return d + sys_datetime.timedelta(days=days)

    @classmethod
    def get_first_last_date_by_week_number(cls, year, week_number):
        """通过week_number周获取一年第week_number周星期一和星期日"""
        if isinstance(year, int) and year > 0 and isinstance(week_number, int) and 0 <= week_number <= 52:
            year_first = sys_datetime.datetime(year=year, month=1, day=1)
            return (year_first + sys_datetime.timedelta(days=week_number * 7 - year_first.weekday()),
                    year_first + sys_datetime.timedelta(days=week_number * 7 - year_first.weekday() + 7)
                    - sys_datetime.timedelta(microseconds=1))
        return None, None

    @classmethod
    def get_first_last_date_by_month(cls, year, month):
        """通过月份获取，当前月份第一天和最后一天"""
        if isinstance(year, int) and year > 0 and isinstance(month, int) and 0 < month <= 12:
            d = sys_datetime.datetime(year=year, month=month, day=1)
            return cls.get_month_first(d), cls.get_month_last(d)
        return None, None

    @classmethod
    def get_monday(cls, d):
        """通过当前日期获取周一日期"""
        if not isinstance(d, sys_datetime.date):
            return None
        return sys_datetime.datetime(year=d.year, month=d.month, day=d.day) - sys_datetime.timedelta(days=d.weekday())

    @classmethod
    def get_sunday(cls, d):
        """通过当前日期获取周日日期"""
        if not isinstance(d, sys_datetime.date):
            return None
        return (sys_datetime.datetime(year=d.year, month=d.month, day=d.day) -
                sys_datetime.timedelta(days=d.weekday() - 7, microseconds=1))

    @classmethod
    def get_next_monday(cls, d):
        """通过当前日期获取下周周一"""
        d = cls.ensure_datetime(d)
        return cls.get_monday(cls.incr(d, days=7))

    @classmethod
    def get_next_sunday(cls, d):
        """通过当前日期获取下周周日"""
        d = cls.ensure_datetime(d)
        return cls.get_sunday(cls.incr(d, days=7))

    @classmethod
    def get_month_first(cls, d):
        """通过当前日期获取当月第一天号"""
        if not isinstance(d, sys_datetime.date):
            return None
        return sys_datetime.datetime(year=d.year, month=d.month, day=1)

    @classmethod
    def get_month_last(cls, d):
        """通过当前日期获取当月最后一天"""
        return cls.get_next_month_first(d) - sys_datetime.timedelta(microseconds=1)

    @classmethod
    def get_next_month_first(cls, d):
        """获取下个月第一天"""
        if d.month == 12:
            return sys_datetime.datetime(year=d.year + 1, month=1, day=1)
        else:
            return sys_datetime.datetime(year=d.year, month=d.month + 1, day=1)

    @classmethod
    def get_pre_month_first(cls, d):
        """获取上一个月的第一天"""
        if d.month == 1:
            return sys_datetime.datetime(year=d.year - 1, month=12, day=1)
        else:
            return sys_datetime.datetime(year=d.year, month=d.month - 1, day=1)

    @classmethod
    def get_quarter(cls, d):
        """获取年份、季度"""
        if not isinstance(d, sys_datetime.date):
            raise TypeError(u'%r is not a `datetime` object' % d)
        m = d.month / 3
        if d.month % 3:
            m += 1
        return d.year, m

    @classmethod
    def get_quarter_first(cls, d):
        """获取当前季度第一天"""
        year, quarter = cls.get_quarter(d)
        return cls.get_month_first(sys_datetime.datetime(year=year, month=(quarter - 1) * 3 + 1, day=1))

    @classmethod
    def get_quarter_last(cls, d):
        """获取当前季度最后一天"""
        year, quarter = cls.get_quarter(d)
        return cls.get_month_last(sys_datetime.datetime(year=year, month=(quarter - 1) * 3 + 3, day=1))

    @classmethod
    def get_next_quarter_first(cls, d):
        """获取下个季度第一天"""
        return cls.get_next_month_first(cls.get_quarter_last(d))

    @classmethod
    def get_year_first(cls, d):
        return sys_datetime.datetime(d.year, 1, 1)

    @classmethod
    def get_next_year_first(cls, d):
        return sys_datetime.datetime(d.year + 1, 1, 1)

    @classmethod
    def get_year_last(cls, d):
        return cls.get_next_year_first(d) - sys_datetime.timedelta(microseconds=1)

    @classmethod
    def now(cls, days=0):
        """days 为0时，返回当前时间，为其他整数时，返回当前时间前几天或后几天的时间"""
        d = sys_datetime.datetime.now()
        if not isinstance(days, int):    # days不是整数时直接返回当前时间
            return d
        return d + sys_datetime.timedelta(days=days) if days else d

    @classmethod
    def current_millis(cls, days=0):
        """days 为0时，返回当前时间，为其他整数是，返回当前时间前几天或后几天的时间"""
        millis = int(time.time() * 1000)
        if not isinstance(days, int):
            return millis
        return millis + days * 24 * 60 * 60 if days else millis

    @classmethod
    def delta_format(cls, delta):
        if isinstance(delta, sys_datetime.timedelta) and delta.days >= 0:
            l = []
            if delta.days:
                l.append('%d天' % delta.days)
            hour = delta.seconds / 3600
            if hour:
                l.append('%d小时' % hour)
            minute = delta.seconds % 3600 / 60
            if minute:
                l.append('%d分' % minute)
            seconds = delta.seconds % 60
            if seconds:
                l.append('%d秒' % seconds)
            if l:
                return ''.join(l)
            return '0秒'
        return ''

    @classmethod
    def format_query(cls, start, end, _fmt='%Y-%m-%d'):
        if not isinstance(start, sys_datetime.datetime) or not isinstance(end, sys_datetime.datetime):
            raise TypeError('start and end must be datetime object.')
        start = cls.date_to_datetime(start.date())
        end = cls.date_to_datetime(end.date())
        return (TimeTool.datetime_to_str(start, _fmt), TimeTool.datetime_to_str(end, _fmt),
                TimeTool.datetime_to_millis(start) / 1000, TimeTool.datetime_to_millis(end) / 1000)

    @classmethod
    def equal_month(cls, d1, d2):
        """比较两个日期是否是同一个月份"""
        if not isinstance(d1, sys_datetime.datetime) or not isinstance(d2, sys_datetime.datetime):
            return False
        return d1.year == d2.year and d1.month == d2.month

    @classmethod
    def get_date_tips(cls, d, _type='day'):
        """
        传入日期,返回日期的提示信息
        :param d: datetime object
        :param _type: day week month
        :return: str
        """
        if isinstance(d, (str, unicode)):
            d = cls.str_to_datetime(d)
        if isinstance(d, sys_datetime.date):
            d = cls.date_to_datetime(d)
        if isinstance(d, sys_datetime.datetime):
            if _type == 'day':
                return '周' + ('一', '二', '三', '四', '五', '六', '日')[d.weekday()]
            elif _type == 'week':
                y, w, d = d.isocalendar()
                return '%d年第%02d周' % (y, w)
            elif _type == 'month':
                return '%d年%02d月' % (d.year, d.month)
            elif _type == 'quarter':
                year, quarter = cls.get_quarter(d)
                return '%d年%02d季度' % (year, quarter)
        return ''

    @classmethod
    def query_to_datetime(cls, *args):
        """日期字符串转日期datetime"""
        return tuple(cls.str_to_datetime(arg) for arg in args)

    @classmethod
    def query_to_date_str(cls, *args, **kwargs):
        """"""
        dts = functools.partial(cls.datetime_to_str, fmt=kwargs.get('_fmt', '%Y-%m-%d'))
        return tuple(dts(cls.str_to_datetime(arg)) for arg in args)

    @classmethod
    def query_to_millis(cls, *args, **kwargs):
        def func(x):
            if kwargs.get('second', False):
                return cls.datetime_to_millis(x) / 1000
            else:
                return cls.datetime_to_millis(x)
        return tuple(func(cls.str_to_datetime(arg)) for arg in args)

    @classmethod
    def ensure_datetime(cls, date):
        if isinstance(date, (str, unicode)):
            date = cls.str_to_datetime(date)
        elif isinstance(date, sys_datetime.date):
            date = sys_datetime.datetime(year=date.year, month=date.month, day=date.day)
        else:
            pass
        if not isinstance(date, sys_datetime.datetime):
            raise ValueError('date is not a datetime object')
        return date

    @classmethod
    def format_group_date(cls, dt, _type='day', _fmt='%Y-%m-%d'):
        if isinstance(dt, (str, unicode)):
            dt = cls.str_to_datetime(dt)
        if isinstance(dt, sys_datetime.date):
            dt = sys_datetime.datetime(year=dt.year, month=dt.month, day=dt.day)
        if not isinstance(dt, sys_datetime.datetime):
            raise ValueError('dt is not a datetime object')
        if _type == 'day':    # 返回当前日期
            return cls.datetime_to_str(dt, _fmt)
        elif _type == 'week':    # 返回当前周的日范围
            return '%s ~ %s' % (
                cls.datetime_to_str(cls.get_monday(dt), _fmt),
                cls.datetime_to_str(cls.get_sunday(dt), _fmt)
            )
        elif _type == 'month':    # 返回当前月份的日期范围
            return '%s ~ %s' % (
                cls.datetime_to_str(cls.get_month_first(dt), _fmt),
                cls.datetime_to_str(cls.get_month_last(dt), _fmt)
            )
        elif _type == 'quarter':
            return '%s ~ %s' % (
                cls.datetime_to_str(cls.get_quarter_first(dt), _fmt),
                cls.datetime_to_str(cls.get_quarter_last(dt), _fmt)
            )
        else:
            raise ValueError('Parameter _type must be (day|week|month), you get %r' % _type)

    @classmethod
    def diff_month(cls, dt1, dt2):
        """比较两个时间相差几个自然月, 取当月第一天比较"""
        dt1, dt2 = cls.query_to_datetime(dt1, dt2)
        dt1, dt2 = cls.get_month_first(dt1), cls.get_month_first(dt2)
        if not all([dt1, dt2]):
            return 0
        return (dt2.year - dt1.year) * 12 + (dt2.month - dt1.month)

    @classmethod
    def range_month(cls, start, end, reverse=False):
        """获取月份区间"""
        start, end = cls.query_to_datetime(start, end)
        start, end = cls.get_month_first(start), cls.get_month_first(end)
        if reverse:
            index = start
            while index > end:
                yield index
                index = TimeTool.get_pre_month_first(index)
        else:
            index = start
            while index < end:
                yield index
                index = TimeTool.get_next_month_first(index)

    @classmethod
    def compare(cls, dt1, dt2):
        """
        比较两个日期，dt1 > dt2: 1, dt1 == dt2: 0, dt1 < dt2: -1 
        :return: 1, 0, -1
        """
        dt1, dt2 = cls.query_to_datetime(dt1, dt2)
        return cmp(dt1, dt2)

    @classmethod
    def format_interval_date(cls, date, start, end, _type='week', _fmt='%Y-%m-%d'):
        date = cls.ensure_datetime(date)
        start = cls.ensure_datetime(start)
        end = cls.ensure_datetime(end)
        if not (start <= date <= end):
            raise ValueError('start <= date <= end')

        if _type == 'week':
            return '%s ~ %s' % (
                TimeTool.datetime_to_str(max(start, cls.get_monday(date)), _fmt),
                TimeTool.datetime_to_str(min(end, cls.get_sunday(date)), _fmt)
            )
        elif _type == 'month':
            return '%s ~ %s' % (
                TimeTool.datetime_to_str(max(start, cls.get_month_first(date)), _fmt),
                TimeTool.datetime_to_str(min(end, cls.get_month_last(date)), _fmt)
            )
        else:
            raise ValueError('_type must by (week|month)')

    @classmethod
    def get_day_start_end_time(cls, date):
        """获取指定日期的起始时间和结束时间"""
        start = TimeTool.str_to_datetime(date)
        end = start + TimeTool.timedelta(days=1)
        return TimeTool.datetime_to_str(start, '%Y-%m-%d'), TimeTool.datetime_to_str(end, '%Y-%m-%d')
