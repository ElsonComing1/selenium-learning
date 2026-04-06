'''__init__.py 文件向外面的目录暴露同层级的文件级变量'''
from .exceptionTools import common_exception,type_parse
from .logger import setup_logger,log
# 外层使用可以直接写最外层目录不用完整书写绝对路径；上面使用的相对路径

__all__=[
    'common_exception',
    'setup_logger'
]
# __all__用于设置白名单，import * 时，直接默认是__all__中的名单，不会是其他变量。
# 不可以隐式调用，显示调用；单向调用