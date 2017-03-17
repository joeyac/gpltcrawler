# encoding=utf-8
import logging


logging.basicConfig(
    level=logging.DEBUG,
    format="%(name)s: %(asctime)s [%(module)s:%(funcName)s] [%(levelname)s]- %(message)s",
    filename='server.log',
    filemode='a',
)

# 定义一个Handler打印INFO及以上级别的日志到sys.stderr
console = logging.StreamHandler()
console.setLevel(logging.INFO)
# 设置日志打印格式
formatter = logging.Formatter("%(name)s: %(asctime)s [%(module)s:%(funcName)s] [%(levelname)s]- %(message)s",)
console.setFormatter(formatter)
# 将定义好的console日志handler添加到root logger
logging.getLogger('').addHandler(console)

error = logging.FileHandler('error.log')
error.setLevel(logging.WARNING)
formatter = logging.Formatter("%(name)s: %(asctime)s [%(module)s:%(funcName)s] [%(levelname)s]- %(message)s",)
error.setFormatter(formatter)
logging.getLogger('').addHandler(error)

logger = logging

WAIT_CODE = 0

RESULT_MAP = {
    '编译错误': 11,
    '答案正确': 4,
    '部分正确': 14,  # extra add
    '格式错误': 5,
    '答案错误': 6,
    '运行超时': 7,
    '内存超限': 8,
    'default': 10,  # runtime error
}


LANG_MAP = {
    0: '3',   # c
    1: '2',   # c++
    3: '10',  # java
}


SERVER = False

if SERVER:
    DATABASE_INFO = {
        'ip': 'localhost',
        'user': 'testuser',
        'pwd': 'testuser',
        'database': 'oj',
    }
else:
    DATABASE_INFO = {
        'ip': 'localhost',
        'user': 'testuser',
        'pwd': 'testuser',
        'database': 'oj',
    }

user_json_file = 'new-user-pwd.json'
