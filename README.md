# gpltcrawler
craw problem info and submit code to https://www.patest.cn/contests/gplt

## How to use

1. add username and password in user-pwd.json

2. change config in utils.py
    1. set SERVER var to True or False.
    
    2. set your database connection like this:
            
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
