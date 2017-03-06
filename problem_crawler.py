# encoding=utf-8

import urllib2
import MySQLdb
import re
from bs4 import BeautifulSoup
from database import update_problem
from utils import logger, DATABASE_INFO

# problem_id title description input output sample_input sample_output source time_limit memory_limit

# problem source
# LEVEL1-2
# LEVEL2-15
# LEVEL3-12


def getinfo(level, pid):
    base_url = 'https://www.patest.cn/contests/gplt/'
    problem_grade = 'L%d-' % level
    problem_num = '%03d' % pid
    url = base_url + problem_grade + problem_num
    page = urllib2.urlopen(url)
    soup = BeautifulSoup(page, 'html5lib')
    problem_info = soup.find('div', {'id': 'problemInfo'})
    limit = problem_info.find_all('div', {'class': 'limit'})
    time_limit = limit[0].find('div', {'class': 'value'}).text.strip()
    memory_limit = limit[1].find('div', {'class': 'value'}).text.strip()
    time_limit = str(time_limit).split(' ')[0]  # ms
    memory_limit = str(memory_limit).split(' ')[0]  # kb

    # 注意时间单位是ms
    time_limit = int(time_limit)

    memory_limit = int(memory_limit) / 1024  # mb
    source = 'LEVEL{level}-{pid}'.format(level=level, pid=pid)

    title = soup.find('h1').text.strip()[7:].strip()

    input_des = ''
    output_des = ''
    sample_input = ''
    sample_output = ''

    content = soup.find('div', {'id': 'problemContent'})
    content = str(content)
    content = re.split('<b>\s*.*：\s*</b>|<p><b>\s*.*：\s*</b></p>', content)
    content[0] = content[0].replace('<div id="problemContent">', '').strip()
    content[-1] = content[-1].replace('</div>', '').strip()

    content = [str(ele).strip() for ele in content]

    length = len(content)
    if length == 1:
        description = content[0]
    else:  # 5 7 9
        description = content[0]
        input_des = content[1]
        output_des = content[2]
        left = (length - 3) / 2
        arr = 2
        for i in range(1, left + 1):
            p = arr + 2 * i - 1
            content[p] = content[p].replace('<pre>', '').replace('</pre>', '')
            content[p+1] = content[p+1].replace('<pre>', '').replace('</pre>', '')
            sample_input += '输入样例{i}：\n{des}'.format(i=i, des=content[p])
            sample_output += '输出样例{i}：\n{des}'.format(i=i, des=content[p+1])

    # title description input output sample_input sample_output source time_limit memory_limit
    return {'title': title.encode("utf-8"), 'description': description, 'input': input_des, 'output': output_des,
            'sample_input': sample_input, 'sample_output': sample_output, 'source': source,
            'time_limit': time_limit, 'memory_limit': memory_limit}


def dev():
    db = MySQLdb.connect(DATABASE_INFO['ip'], DATABASE_INFO['user'],
                         DATABASE_INFO['pwd'], DATABASE_INFO['database'], charset='utf8')
    for lev, cnt in [[1, 32], [2, 16], [3, 12]]:
        for pi in range(1, cnt + 1):
            s = 'start: lev:{lev} pid:{pid}.'.format(lev=lev, pid=pi)
            logger.info(s)
            info = getinfo(lev, pi)
            for ele in info:
                if type(info[ele]) == str:
                    info[ele] = info[ele].replace("'", "\\\'").replace('"', '\\\"')
            update_problem(db, info)


def init():
    sql = """CREATE TABLE detail (
             solution_id  INT NOT NULL,
             total_score  INT,
             case_result TEXT ) default charset = utf8;"""
    db = MySQLdb.connect(DATABASE_INFO['ip'], DATABASE_INFO['user'],
                         DATABASE_INFO['pwd'], DATABASE_INFO['database'], charset='utf8')
    cursor = db.cursor()
    cursor.execute(sql)

if __name__ == '__main__':
    # lev:1 pid:11. lev:1 pid:21.
    # 创建detail表
    # init()
    # 导入题目信息
    # dev()
