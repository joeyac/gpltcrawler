# encoding=utf-8
from utils import logger, WAIT_CODE
from utils import RESULT_MAP, LANG_MAP
from submitter import _submit
import time


def update_problem(db, info):
    cursor = db.cursor()
    sql = 'select max(problem_id) from problem;'
    cursor.execute(sql)
    result = cursor.fetchone()
    new_id = result[0] + 1
    # problem_id title description input output sample_input sample_output source time_limit memory_limit
    sql = "insert into problem (problem_id, title, description, input, output," \
          "sample_input, sample_output, source,  time_limit, memory_limit)" \
          "VALUES ({problem_id}, '{title}', '{description}', '{input}', '{output}', " \
          "'{sample_input}', '{sample_output}', '{source}', {time_limit}, {memory_limit});"\
          .format(problem_id=new_id, title=info['title'], description=info['description'],
                  input=info['input'], output=info['output'], sample_input=info['sample_input'],
                  sample_output=info['sample_output'], source=info['source'],
                  time_limit=info['time_limit'], memory_limit=info['memory_limit'])
    try:
        cursor.execute(sql)
        db.commit()
    except Exception as e:
        logger.exception(e)
        db.rollback()


def wait2que(db, queue):
    # 将等待的提交加入队列
    cursor = db.cursor()
    sql = 'select * from solution where problem_id <> 0 and result={wait};'.format(wait=WAIT_CODE)
    try:
        cursor.execute(sql)
        results = cursor.fetchall()
        flag = False
        for row in results:
            # 将solution_id 加入队列
            flag = True
            queue.put(row[0])
        return flag
    except Exception as e:
        logger.exception(e)
        logger.error('unable to fetch data.')
        return False


def update(db, solution_id, score, result_id, time_s, memory_s, case_result):
    cursor = db.cursor()
    # update solution table
    sql1 = "UPDATE solution SET result = {result}, time={time}, memory={memory} WHERE solution_id = {s_id};"\
           .format(result=result_id, time=time_s, memory=memory_s, s_id=solution_id)

    # update detail table
    sql2 = "INSERT INTO detail(solution_id, total_score, case_result) " \
           "VALUES ({s_id}, {score}, '{case}')".format(s_id=solution_id, score=score, case=case_result)
    try:
        cursor.execute(sql1)
        cursor.execute(sql2)
        db.commit()
    except Exception as e:
        logger.exception(e)
        db.rollback()


def update_compile_info(db, solution_id, info):
    cursor = db.cursor()
    info = str(info).replace("'", "\\\'").replace('"', '\\\"')

    sql = "INSERT into compileinfo(solution_id, error) VALUES({s_id},'{info}')".format(s_id=solution_id, info=info)
    try:
        cursor.execute(sql)
        db.commit()
    except Exception as e:
        logger.exception(e)
        db.rollback()


def submit(db, solution_id, uid, pwd):
    # problem_grade, problem_num, language, src_code, username, password
    cursor = db.cursor()
    # get information of problem
    info_sql = "select * from problem where problem_id =" \
               "(select problem_id from solution where solution_id = {sid})".format(sid=solution_id)

    sql = "select * from solution where solution_id ={sid}".format(sid=solution_id)

    sql_code = "select * from source_code where solution_id ={sid}".format(sid=solution_id)

    try:
        cursor.execute(info_sql)
        info = cursor.fetchone()

        cursor.execute(sql)
        result = cursor.fetchone()

        cursor.execute(sql_code)
        src_code = cursor.fetchone()[1]
        # LEVEL3-12
        problem_grade = int(info[9][5:6])
        problem_num = int(info[9][7:])
        language = LANG_MAP[result[7]]

        logger.info('Submitting {sid} by {uid}.'.format(sid=solution_id, uid=uid))
        res = _submit(problem_grade, problem_num, language, src_code, uid, pwd)
        logger.info('Get result of {sid} by {uid}.'.format(sid=solution_id, uid=uid))
        return res

    except Exception as e:
        logger.exception(e)
        return {}


def test_submit(solution_id, uid):
    logger.info('Submitting {sid} by {uid}.'.format(sid=solution_id, uid=uid))
    time.sleep(2)
    res = '答案错误'
    try:
        res = RESULT_MAP[res]
    except:
        res = RESULT_MAP['default']

    logger.info('get result of {sid} by {uid}.'.format(sid=solution_id, uid=uid))
    return res
