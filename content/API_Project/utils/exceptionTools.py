# exceptionTools.py
import functools
import inspect
from typing import Dict, Any, Type


def common_exception(func_main):
    @functools.wraps(func_main)
    def wrapper(*args, **kwargs):
        try:
            return func_main(*args, **kwargs)
        except Exception as e:
            # e 就是错误的内容
            raise e

    return wrapper


def type_parse(**type_map: Type):
    """
    多参数类型检查器
    用法：
    @type_parse(id=int,name=str,price=float)
    def process(id, name, price):
        pass
    """

    def decorate(func):
        sig = inspect.signature(func)
        # 记录参数
        param_names = list(sig.parameters.keys())
        # 把参数做成列表

        # 回去被装饰函数的参数名称，构成一个列表
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            bound_kwargs = sig.bind(*args, **kwargs)
            # 将参数名称与参数值对应构成字典，但是有默认值的参数，且没有传递值，就需要使用apply_defaults进行使用默认值
            bound_kwargs.apply_defaults()
            # 没有默认值的形参是必传参数
            for param_name, expected_type in type_map.items():
                if param_name not in param_names:
                    raise TypeError(f"参数{param_name}不存在函数签名中")
                value = bound_kwargs.arguments[param_name]
                # 检查类型（允许 None 跳过，除非类型是 type(None)）
                if value is not None and not isinstance(value, expected_type):
                    raise TypeError(
                        f"参数 '{param_name}' 类型错误: "
                        f"期望 {expected_type.__name__}, "
                        f"实际得到 {type(value).__name__} (值: {value!r})"
                    )
            return func(*args, **kwargs)

        return wrapper

    return decorate


def mysql_args_parse(func):
    @functools.wraps(func)
    def wrapper(*args,**kwargs):
        try:
            fun_name=func.__name__
            self=args[0]
            # 绑定参数自动处理位置参数和关键字参数
            sig=inspect.signature(func)
            bound=sig.bind(*args,**kwargs)
            bound.apply_defaults()  # 应用默认值

            # 获取参数值（无论怎么传递）
            argsments=bound.arguments
            table=argsments.get('table')
            columns=argsments.get('columns')
            enabled_commit=kwargs.get('enabled_commit',False)

            # 进行过滤
            if not table or not table.replace("_", "").isalnum():
                raise ValueError(f"非法表名{table}")
            if fun_name in ('get_single','get_many','insert_many',):
                if isinstance(columns, list) and columns != "*":
                    for column in columns:
                        if (
                            not isinstance(column, str)
                            or not column.replace("_", "").isalnum()
                        ):
                            raise ValueError(f"非法字段名: {column}")
                    fields = ",".join(columns)
                else:
                    fields = "*"
            elif fun_name in ('insert_single','update_row','delete_row'):
                pass
            else:
                raise ValueError(f'当前函数名字{fun_name}不在使用范围内，你不能使用该装饰器')

            result= func(*args,**kwargs)
            # 重点，将被装饰函数的执行结果保存起来，不立即返回。
            # 否则后面的代码就不会执行了
            if enabled_commit:
                self.conn.commit()
                print(f"✅ 已自动提交事务")
            return result
        except Exception as e:
            raise e
    return wrapper
