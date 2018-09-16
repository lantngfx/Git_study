# coding: utf-8

import time
import MySQLdb
import MySQLdb.cursors
import logging


log = logging.getLogger()


class MySqlClient(object):

    MySQLError = MySQLdb.MySQLError

    def __init__(self, host='localhost', port=3306, user=None, password=None, db=None, charset='utf8', max_retry=0):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.db = db
        self.charset = charset
        self.max_retry = max_retry

        self._conn = None
        self._cursor = None
        self.connect()

    def clone(self):
        return MySqlClient(host=self.host, port=self.port, user=self.user, password=self.password, db=self.db,
                           charset=self.charset)

    def __del__(self):
        self.close()

    def close(self):
        if self._cursor:
            self._cursor.close()
            self._cursor = None
        if self._conn:
            self._conn.close()
            self._conn = None

    def connect(self):
        count = 0
        while 1:
            if self._conn:
                try:
                    return self._conn.ping()
                except MySQLdb.MySQLError:
                    pass
                try:
                    self.close()
                except MySQLdb.MySQLError:
                    pass
            try:
                count += 1
                self._conn = MySQLdb.connect(host=self.host, port=self.port, user=self.user,
                                             passwd=self.password, db=self.db, charset=self.charset)
                self._cursor = self._conn.cursor(MySQLdb.cursors.DictCursor)
            except MySQLdb.MySQLError, e:
                log.error(u'reconnect failed {}'.format(e))
                if 0 < self.max_retry < count:
                    raise MySQLdb.MySQLError('connection failed')
                time.sleep(5)

    def query(self, sql, *args):
        try:
            self.execute(sql, *args)
            return self._cursor.fetchall()
        except Exception, e:
            log.error('mysql client query %r, args=%r. error %r' % (sql, args, e))
            return None

    def first(self, sql, *args):
        try:
            self.execute(sql, *args)
            return self._cursor.fetchone()
        except Exception, e:
            log.error('mysql client first %r, args=%r. error %r' % (sql, args, e))
            return None

    def execute(self, sql, *args):
        self.connect()
        try:
            args = args or None
            self._cursor.execute(sql, args)
            self._conn.commit()
            return True
        except Exception, e:
            log.error('mysql client execute %r, args=%r. error %r' % (sql, args, e))
            raise

    def iter_query(self, sql, *args):
        self.connect()
        cursor = self._conn.cursor(MySQLdb.cursors.SSDictCursor)
        try:
            args = args or None
            cursor.execute(sql, args)
            for item in cursor:
                yield item
                del item
            self._conn.commit()
        except Exception, e:
            log.error('mysql client query %r, args=%r. error %r' % (sql, args, e))
            raise
        finally:
            cursor.close()

    def insert_many(self, sql, *values):
        self.connect()
        try:
            values = values or None
            self._cursor.executemany(sql, values)
            self._conn.commit()
            return True
        except MySQLdb.MySQLError, e:
            log.error('insert many error, sql, e = {}'.format((sql, e)))
            raise


class SqlTool(object):

    def __init__(self, table_name):
        self._table_name = table_name
        self._primary_keys = []
        self._columns = []
        self._values = {}

    def primary_key(self, *args):
        """指明主键或唯一键"""
        self._primary_keys = list(args)
        return self

    def columns(self, *args):
        """指明表的字段"""
        self._columns = [k for k in args if k not in self._primary_keys]
        return self

    def data(self, **kwargs):
        """数据"""
        self._values = kwargs
        return self

    @property
    def update_query(self):
        """返回更新语句和参数"""
        update = ', '.join(map(lambda x: '{k} = %s'.format(k=x), self._columns))
        primary = ' and '.join(map(lambda x: '{k} = %s'.format(k=x), self._primary_keys))
        params = (map(lambda x: self._values.get(x), self._columns) +
                  map(lambda x: self._values.get(x), self._primary_keys))

        return 'update {table_name} set {update} where {primary} ' \
               ''.format(table_name=self._table_name, update=update, primary=primary), tuple(params)

    @property
    def insert_query(self):
        """返回插入语句和参数"""
        keys = set(self._columns + self._primary_keys)
        columns = ', '.join(keys)
        values = ', '.join(['%s'] * len(keys))
        params = map(lambda x: self._values.get(x), keys)
        return 'insert into {table_name}({columns}) values ({values})' \
               ''.format(table_name=self._table_name, columns=columns, values=values), tuple(params)


class SQL(object):

    @classmethod
    def insert(cls, table_name, **values):
        """
        :param table_name: 数据库表名
        :param values: dict, 数据库表字段对应的值
        :return: sql, params
        >>> SQL.insert('table_name', id=1, db='mysql', version='5.6.7')
        ('insert into `table_name` (`version`, `db`, `id`) values(%s, %s, %s)', ('5.6.7', 'mysql', 1))
        """
        columns = values.keys()
        params = tuple(map(lambda k: values.get(k), columns))
        sql = 'insert into `{table_name}` ({columns}) values({params})' \
              ''.format(table_name=table_name,
                        columns=', '.join(map(lambda k: '`{}`'.format(k), columns)),
                        params=', '.join(['%s'] * len(columns)))
        return sql, params

    @classmethod
    def upsert(cls, table_name, **values):
        """
        :param table_name: 数据库表名
        :param values: dict 数据库表字段对应的值
        :return: sql, params
        >>> SQL.upsert('table_name', id=1, db='mysql')
        ('insert into `table_name` (`db`, `id`) values(%s, %s) on duplicate key update `db` = %s, `id` = %s',
        ('mysql', 1, 'mysql', 1))
        """
        if not isinstance(table_name, str):
            raise TypeError('table_name must be string')
        if not values:
            raise ValueError('need at least one filed value')

        columns = values.keys()
        set_columns = map(lambda k: '`{}` = %s'.format(k), columns)
        sql = 'insert into `{table_name}` ({columns}) values({params}) ' \
              'on duplicate key update {set_columns}' \
              ''.format(table_name=table_name,
                        columns=', '.join(map(lambda k: '`{}`'.format(k), columns)),
                        params=', '.join(['%s'] * len(columns)),
                        set_columns=', '.join(set_columns))
        params = tuple(map(lambda k: values.get(k), columns))
        params = params + params
        return sql, params

    @classmethod
    def update(cls, table_name, values, where):
        """
        构造 update sql 语句
        :param table_name: 表名
        :param values: dict 要更新的数据
        :param where: dict 更新条件(AND)
        :return: sql(str), params(tuple)
        """
        if not isinstance(table_name, str):
            raise TypeError('`table_name` must be string object')
        if not isinstance(values, dict):
            raise TypeError('`values` must be dict object')
        if not isinstance(where, dict):
            raise TypeError('`where` must be dict object')
        set_columns = values.keys()
        where_columns = where.keys()
        sql = 'update `{table_name}` set {set_columns} where {where_columns}'.format(
            table_name=table_name,
            set_columns=', '.join(map(lambda x: '`{}` = %s'.format(x), set_columns)),
            where_columns=' and '.join(map(lambda x: '`{}` = %s'.format(x), where_columns))
        )
        params = tuple(map(lambda x: values.get(x), set_columns) + map(lambda x: where.get(x), where_columns))
        return sql, params

    @classmethod
    def delete(cls, table_name, **where):
        """
        构造 delete sql 语句
        :param table_name: str 表名
        :param where: dict 更新条件
        :return: sql(str), params(tuple)
        """
        if not isinstance(table_name, str):
            raise TypeError('`table_name` must be string object')
        if not where:
            raise ValueError('need at least one filed value')
        where_columns = where.keys()
        sql = 'delete from `{table_name}` where {where_columns}'.format(
            table_name=table_name,
            where_columns=' and '.join(map(lambda x: '`{}` = %s'.format(x), where_columns))
        )
        params = tuple(map(lambda x: where.get(x), where_columns))
        return sql, params

    @classmethod
    def select(cls, table_name, *columns, **where):
        """
        构造查询语言
        :param table_name: 表名
        :param columns: 查询字段
        :param where: 查询条件(and)
        :return: sql(str), params(tuple)
        """
        if not columns:
            columns = ('*',)
        where_columns = where.keys()
        sql = 'select {columns} from `{table_name}` where {where}'.format(
            columns=', '.join(columns),
            table_name=table_name,
            where=' and '.join(map(lambda x: '`{}` = %s'.format(x), where_columns))
        )
        params = tuple(map(lambda x: where.get(x), where_columns))
        return sql, params

    @classmethod
    def update_insert(cls, table_name, duplicate, **data):
        """
        :param table_name: 数据库表名
        :param duplicate: dict 主键字段
        :param data: dict 更新时需要更新的字段
        :return: sql, params
        >>> SQL.update_insert('table_name', {'id': 1}, {'name': 'test'})
        ('insert into `table_name` (`id`, `name`) values(%s, %s) on duplicate key update `name` = %s',
        (1, 'test', 'test'))
        """
        if not isinstance(table_name, str):
            raise TypeError('table_name must be string')
        if not data:
            raise ValueError('need at least one filed value')
        if not isinstance(duplicate, dict) or not isinstance(data, dict):
            raise TypeError('data or update_ata must be dict object')
        upsert_columns = data.keys()
        data.update(duplicate)
        insert_columns = data.keys()
        set_columns = map(lambda k: '`{}` = %s'.format(k), upsert_columns)
        sql = 'insert into `{table_name}` ({columns}) values({params}) ' \
              'on duplicate key update {set_columns}' \
              ''.format(table_name=table_name,
                        columns=', '.join(map(lambda k: '`{}`'.format(k), insert_columns)),
                        params=', '.join(['%s'] * len(insert_columns)),
                        set_columns=', '.join(set_columns))
        insert_params = tuple(map(lambda k: data.get(k), insert_columns))
        upsert_params = tuple(map(lambda k: data.get(k), upsert_columns))
        return sql, insert_params + upsert_params
