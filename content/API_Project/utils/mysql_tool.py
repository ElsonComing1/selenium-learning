from pathlib import Path
import sys,os
if not str(Path(__file__).parent.parent) in sys.path:
    sys.path.insert(0, str(Path(__file__).parent.parent))

import pymysql
from config import common_varaints as cv
from dotenv import load_dotenv
from utils import type_parse, mysql_args_parse
import datetime
from dbutils.pooled_db import PooledDB


class Mysql_tool:
    def __init__(
        self,
        host: str = "localhost",
        port: int = 3306,
        user: str = None,
        password: str = None,
        db: str = None,
    ):
        # self.conn = pymysql.connect(
        #     host=host,
        #     port=port,
        #     user=user,
        #     password=password,
        #     database=db,
        #     charset="utf8mb4",
        #     autocommit=False,
        #     cursorclass=pymysql.cursors.DictCursor,
        # )
        # 使用PooledDB类，创建mysql连接池，池中会至少保存多少个，最多多少个，来使得进程或者线程更加便利
        # 创建池子
        self.pool = PooledDB(
            creator=pymysql,
            host=host,
            port=int(port),
            user=user,
            password=password,
            database=db,
            charset="utf8mb4",
            cursorclass=pymysql.cursors.DictCursor,
            mincached=2,  # 内存总至少得有两个连接进程活着
            maxcached=5,  # 最多只有5个进程被建立
            maxshared=0,  # 最多共享连接数，是线程之间，同一个进程能否被共享。建议0；否者适用于单线程的协程
            maxconnections=10,  # 最大连接数是只能为10个，也就是只能有十个进程或者线程会想用pool池
            blocking=True,  # 没吃上就等着
            maxusage=None,  # 连上使用次数是没有限制的
            setsession=[
                "SET SESSION wait_timeout=28800"
            ],  # 防止连接被mysql踢掉，用之前的setup
            ping=1,  # 避免拿到的连接是死的
        )
        # 从池子中，拿去一个连接
        self.conn = self.pool.connection()
        if password is None or user is None or db is None:
            raise ValueError(f"你输入的值中有不正确值，请你检查")
            # raise用于内部，上抛问题
            # assert 会触发对应的except类型;

        # autocommit用于测试时，手动提交，避免污染数据
        # pymysql.cursors.Dictcursor设置cursor的返回类型

    @mysql_args_parse
    @type_parse(
        table=str, columns=list | str, con_key=str, conditions=str, enabled_commit=bool
    )
    def get_single(
        self,
        table: str = None,
        columns: list | str = [],
        con_key: str = None,
        conditions: str = None,
        enabled_commit: bool = False,
    ):
        try:
            sql = (
                f"select {columns} from {table} where {con_key}=%s"
                if con_key and conditions
                else f"select {columns} from {table}"
            )

            # 只有值才是%s, 且永远是%s, 表名等就是字符
            cursor = self.conn.cursor()
            cursor.execute(sql, (conditions,) if con_key and conditions else None)
            return cursor.fetchone()
            # 元组必须要有,
        except Exception as e:
            self.conn.rollback()
            # 失败回滚
            raise e
        finally:
            cursor.close()

    @mysql_args_parse
    @type_parse(
        table=str,
        columns=list | str,
        con_key=str,
        conditions=str,
        number=int,
        enabled_commit=bool,
    )
    def get_many(
        self,
        table: str = None,
        columns: list | str = None,
        con_key: str = None,
        conditions: str = None,
        number: int = 10,
        enabled_commit: bool = False,
    ):
        try:
            sql = (
                f"select {columns} from {table} where {con_key}=%s"
                if con_key and conditions
                else f"select {columns} from {table}"
            )
            cursor = self.conn.cursor()
            cursor.execute(sql, (conditions,) if con_key and conditions else None)
            return cursor.fetchmany(number)
        except Exception as e:
            self.conn.rollback()
            # 失败回滚
            raise e
        finally:
            cursor.close()

    @mysql_args_parse
    @type_parse(table=str, values=dict, enabled_commit=bool)
    def insert_single(
        self, table: str = None, values: dict = None, enabled_commit: bool = False
    ):
        # dict能明确顺序
        try:
            if not table.replace("_", "").isalnum():
                raise ValueError(f"非法表名{table}")
            fields = []
            data = []
            placeholders = []

            for key, value in values.items():
                if not key.replace("_", "").isalnum():
                    raise ValueError(f"非法字段{key}")
                fields.append(f"`{key}`")
                # 加反引号目的为了，避免关键字干扰
                data.append(value)
                placeholders.append("%s")
            fields_sql = ",".join(fields)
            placeholders_sql = ",".join(placeholders)
            sql = f"insert into `{table}` ({fields_sql}) values ({placeholders_sql})"
            cursor = self.conn.cursor()
            cursor.execute(sql, data)
            # self.conn.commit()    # 装饰器完成是否提交
            # 由于只是测试，因此，多数是不需要提交的；如果需要提交需要改变参数值enabled_commit即可
            # 而且其fixture中，是常结合self.conn.rollback进行回滚，避免污染数据。
            return cursor.lastrowid  # 返回自增ID
        except Exception as e:
            self.conn.rollback()
            # 失败回滚
            raise e
        finally:
            cursor.close()

    @mysql_args_parse
    # @type_parse(table=str,columns=list[str],values=list[list|set]|set[list|set])
    def insert_many(
        self,
        table: str = None,
        columns: list[str] = [None],
        values: list[list | set] | set[list | set] = None,
        enabled_commit: bool = False,
    ):
        try:
            if not isinstance(values, (list, set)):
                # isinstance只能检查外层
                raise TypeError(f"你输入的参数类型不对，当前是{values.__class__}")
            if not columns or not values or len(columns) != len(values[0]):
                raise ValueError(f"columns与values的长度不一致")
            placeholder_sql = ",".join(["%s" for i in range(len(columns))])
            fields_sql = ",".join([column for column in columns])
            sql = f"insert `{table}` ({fields_sql}) values ({placeholder_sql})"
            cursor = self.conn.cursor()
            cursor.executemany(sql, values)
            # self.conn.commit()
            return cursor.rowcount
        except Exception as e:
            self.conn.rollback()
            raise e
        finally:
            cursor.close()

    @mysql_args_parse
    @type_parse(
        table=str,
        set_key=str,
        new_value=str,
        con_key=str,
        con_value=str,
        enabled_commit=bool,
    )
    def update_row(
        self,
        table: str = None,
        set_key: str = None,
        new_value: str = None,
        con_key: str = None,
        con_value: str = None,
        enabled_commit: bool = False,
    ):
        try:
            if not table.replace("_", "").isalnum():
                raise ValueError(f"非法表名{table}")
            if None in (set_key, con_key, con_value):
                raise ValueError(f"传递参数有空值")
            sql = f"update `{table}` set `{set_key}`=%s where `{con_key}`=%s"
            cursor = self.conn.cursor()
            cursor.execute(sql, (new_value, con_value))
            # self.conn.commit()
            # 更改完数据后，需要提交数据
            return cursor.rowcount
            # 返回有几行被改
        except Exception as e:
            self.conn.rollback()
            # 失败回滚
            raise e
        finally:
            cursor.close()

    @mysql_args_parse
    @type_parse(table=str, con_key=str, con_value=str, enabled_commit=bool)
    def delete_row(
        self,
        table,
        con_key: str = None,
        con_value: str = None,
        enabled_commit: bool = False,
    ):
        try:
            if not table.replace("_", "").isalnum():
                raise ValueError(f"非法表名{table}")
            if None in (con_key, con_value):
                raise ValueError(f"传递参数有空值")
            sql = f"delete from `{table}` where `{con_key}`={con_value}"
            cursor = self.conn.cursor()
            cursor.execute(cursor)
            # self.conn.commit()
            return cursor.rowcount
        except Exception as e:
            self.conn.rollback()
            # 失败回滚
            raise e
        finally:
            cursor.close()

    def close_connect(self):
        self.conn.close()

    def close_pool(self):
        self.pool.close()


if __name__ == "__main__":
    from core import Config
    load_dotenv(dotenv_path=str(cv.CONFIG_DIR / ".env"))
    host = os.getenv("DB_HOST")
    port = int(os.getenv("DB_PORT"))
    user = os.getenv("DB_USER")
    password = os.getenv("DB_PASSWORD")
    db = os.getenv("DB_NAME")

    mysql_item = Mysql_tool(host=host, port=port, user=user, password=password, db=db)
    # print(mysql_item,type(mysql_item),mysql_item.__class__)
    # data=[
    #     ['4','营业部',datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')],
    #     ['5','维护部',datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')]
    # ]
    data = mysql_item.get_single("departments", "*")
    mysql_item.close_connect()
    mysql_item.close_pool()
    print(data)
