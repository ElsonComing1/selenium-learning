import functools

def common_exception(func_main):
    @functools.wraps(func_main)
    def wrapper(*args,**kwargs):
        try:
            return func_main(*args,**kwargs)
        except Exception as e:
            # e 就是错误的内容
            raise e

    return wrapper