# gpltcrawler
craw problem info and submit code to https://www.patest.cn/contests/gplt

## require
   
   1. ubuntu 14.04 or higher
   
   2. <code>sudo apt-get install libmysqld-dev</code>

## How to use

1. add username and password in user-pwd.json

2. change config in utils.py
    1. install the pip requirement use <code>pip install -r requirements.txt</code>.
    
    2. set <code>user_json_file</code> to your user-pwd file name.

    3. set <code>SERVER</code> to True or False.
    
    4. set your database connection like this:
            
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
     
     5. run <code>python server.py</code>.