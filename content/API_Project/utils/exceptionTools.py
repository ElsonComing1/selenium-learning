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
        param_names = list(sig.parameters.keys())

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
