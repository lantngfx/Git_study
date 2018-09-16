# coding: utf-8


class IntervalMerge(object):

    def __init__(self):
        self._intervals = []

    def add(self, start, end):
        start, end = (start, end) if start < end else (end, start)
        self._intervals.append(dict(st=start, et=end))
        self._intervals.sort(key=lambda x: x['st'])
        tmp = [self._intervals[0]]
        index = 0
        for item in self._intervals:
            st, et = item['st'], item['et']
            if tmp[index]['st'] <= st <= tmp[index]['et']:
                tmp[index]['et'] = max(et, tmp[index]['et'])
            else:
                tmp.append(dict(st=st, et=et))
                index += 1
        self._intervals = tmp

    @property
    def intervals(self):
        return self._intervals

    @property
    def length(self):
        return sum(map(lambda x: x['et'] - x['st'], self._intervals))
