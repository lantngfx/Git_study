# coding: utf-8

import time
from datetime import datetime, date
from collections import defaultdict
import xlsxwriter


def _u(s, strip=True, charset='utf-8'):
    if isinstance(s, datetime):
        return s.strftime('%Y-%m-%d %H:%M:%S')
    if isinstance(s, date):
        return s.strftime('%Y-%m-%d')
    if isinstance(s, str):
        s = s.decode(charset)
    if strip and isinstance(s, unicode):
        s = s.strip()
    return s


def _s(u, strip=True, charset='utf-8'):
    if isinstance(u, unicode):
        u = u.encode(charset)
    if strip and isinstance(u, str):
        u = u.strip()
    return u


class SheetWriter(object):

    def __init__(self, book, sheet_name, start_row=0, default_max_width=20, **options):
        self._book = book
        self._cache_format = {}
        self._sheet = self._book.add_worksheet(_u(sheet_name))
        self.header_row = start_row
        self.row = start_row
        self.default_max_width = default_max_width
        self._col_width = defaultdict(lambda: 10)
        self._options = options
        self.set_header_format(self._get_cell_format(bold=True))

    def _get_cell_format(self, **properties):
        if not properties:
            return None
        ks = properties.keys()
        ks.sort()
        key = ';'.join(map(lambda k: u'{}-{}'.format(k, properties[k]), ks))

        if key not in self._cache_format:
            self._cache_format[key] = self._book.add_format(properties)
        return self._cache_format[key]

    @property
    def current_row(self):
        return self.row

    def set_header_format(self, _fmt):
        self._sheet.set_row(self.header_row, cell_format=_fmt)

    def write_merge(self, value, first_row=0, last_row=0, first_col=0, last_col=0, bold=False, center=True, bg_color=0,
                    bottom=0):
        if first_col > last_col:
            first_col, last_col = last_col, first_col
        if first_row > last_row:
            first_row, last_row = last_row, first_row
        properties = {}
        if bold:
            properties['bold'] = True
        if bg_color:
            properties['bg_color'] = bg_color
        if bottom:
            properties['bottom'] = bottom
        if center:
            properties['valign'] = 'vcenter'
        cell_format = self._get_cell_format(**properties)
        if first_col == last_col:
            try:
                self._col_width[first_col] = min(
                    self.default_max_width, max(self.get_text_width(value), self._col_width[first_col])
                )
            except TypeError:
                pass
        if first_row == last_row:
            columns = last_col - first_col + 1
            width = self.get_text_width(value)
            width = max(width, sum(map(lambda x: self._col_width[x], xrange(first_col, last_col + 1))))
            width = min(self.default_max_width * columns, width) / 1.0 / columns
            for c in xrange(first_col, last_col + 1):
                self._col_width[c] = min(self.default_max_width, max(self._col_width[c], width))

        self._sheet.merge_range(first_row=first_row, first_col=first_col, last_row=last_row, last_col=last_col,
                                data=_u(value), cell_format=cell_format)

    def write(self, values=None, row=None, bold=False, col_span=1, bg_color=0, bottom=0, height=None, **properties):
        """
        在excel中写入一行数据
        :param values: 数据列表
        :param row: 写入数据的行号,默认在excel尾部写入
        :param bold: 是否加粗
        :param col_span: 数据跨列,当values中只有一个数据时有效
        :param bg_color: 背景色
        :param bottom: 下边框线宽度
        :param height: 行高
        :param properties:
        :return: 
        """
        if values is None:
            values = []
        if not isinstance(values, list):
            raise TypeError('values must be list object')
        if bold:
            properties['bold'] = True
        if bg_color:
            properties['bg_color'] = bg_color
        if bottom:
            properties['bottom'] = bottom
        cell_format = self._get_cell_format(**properties)
        if row is None:
            row = self.row
            self.row += 1
        else:
            self.row = max(row, self.row + 1)
        if col_span > 1 == len(values):
            self._sheet.merge_range(row, 0, row, col_span - 1, _u(values[0]), cell_format=cell_format)
        else:
            for col, v in enumerate(values):
                v = _u(v)
                if height:
                    self._sheet.set_row(row, height)
                self._sheet.write(row, col, v, cell_format)
                try:
                    self._col_width[col] = min(
                        self.default_max_width, max(self.get_text_width(v), self._col_width[col]))
                except TypeError:
                    pass

    @classmethod
    def get_text_width(cls, text):
        text = unicode(_u(text))
        width = 0
        for c in unicode(_u(text)):
            if ord(c) < 256:
                width += 1
            else:
                width += 2.4
        return width

    def finish(self):
        for col, width in self._col_width.iteritems():
            if self._options.get('auto_filter', True):
                width += 2
            self._sheet.set_column(firstcol=col, lastcol=col, width=width)
        if self._options.get('auto_filter', True):
            self._sheet.autofilter(0, 0, 0, len(self._col_width) - 1)
        if self._options.get('freeze_header', True):
            self._sheet.freeze_panes(1, 0)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.finish()

    @staticmethod
    def get_columns_name(i, j):
        def _get_name(_index):
            l = []
            _a = _index
            while 1:
                _a, _b = divmod(_a, 26)
                l.append(chr(_b + 65))
                if not _a:
                    break
                _a -= 1
            return ''.join(l[::-1])

        def _inner():
            for x in xrange(i, j):
                yield _get_name(x)
        return list(_inner())


class XlsxTool(object):

    def __init__(self, filename, **properties):
        filename = _u(filename)
        if not filename.endswith('.xlsx'):
            filename += '.%d.xlsx' % time.time()
        self.filename = _u(filename)
        if u':' in self.filename:
            self.filename = self.filename.replace(u':', u'：')
        properties.setdefault('font_size', 11)
        properties.setdefault('font_name', 'Times New Roman')
        self._book = xlsxwriter.Workbook(self.filename, options={
            'default_format_properties': properties
        })
        self._current_sheet = None

    def sheet(self, sheet_name=None, start_row=0, default_max_width=40,
              auto_filter=True, freeze_header=True, **options):
        return SheetWriter(self._book, sheet_name, start_row=start_row, default_max_width=default_max_width,
                           auto_filter=auto_filter, freeze_header=freeze_header, **options)

    def __del__(self):
        self.close()

    def close(self):
        if self._book:
            self._book.close()
            self._book = None
