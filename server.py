# encoding=utf-8
# detail
# solution_id total_score case_result(json)

# problem source
# LEVEL1-2
# LEVEL2-15
# LEVEL3-12

import MySQLdb
import Queue
import time
import json
from threading import Thread
from utils import logger, RESULT_MAP, DATABASE_INFO
from database import wait2que, submit, update, update_compile_info


class SubmitWorker(Thread):
    def __init__(self, uid, pwd, queue):
        self.uid = uid
        self.pwd = pwd
        self.time_stamp = 0
        self.queue = queue
        self.db = MySQLdb.connect(DATABASE_INFO['ip'], DATABASE_INFO['user'],
                                  DATABASE_INFO['pwd'], DATABASE_INFO['database'], charset='utf8')
        super(SubmitWorker, self).__init__()

    def run(self):
        while True:
            sid = self.queue.get()
            cur_time = time.time()

            if cur_time - self.time_stamp < 15:
                wait_time = int(15 + self.time_stamp - cur_time + 1)
                logger.info('{uid} should wait for {wait}s.'.format(uid=self.uid, wait=wait_time))
                time.sleep(wait_time)

            res = submit(self.db, sid, self.uid, self.pwd)

            if not res:
                s = '{uid} submit {sid} failed.'.format(uid=self.uid, sid=sid)
                logger.exception(s)

                self.time_stamp = time.time()
                self.queue.task_done()

            else:
                result = res['result']
                score = int(result[2])

                status = str(result[1].encode("utf-8"))
                try:
                    status = RESULT_MAP[status]
                except Exception as e:
                    info = e.__class__.__name__ + ' :unrecognized result:{res}.'.format(res=status)
                    logger.warning(info)
                    status = RESULT_MAP['default']

                if status == 11:  # compile error
                    compile_info = res['compile_info']
                    update_compile_info(self.db, sid, compile_info)

                time_s = int(result[5]) if result[5] else 0
                memory_s = int(result[6]) if result[6] else 0
                case_result = json.dumps(res['case_result'], ensure_ascii=False)
                # db, solution_id, score, result_id, time_s, memory_s, case_result
                update(self.db, sid, score, status, time_s, memory_s, case_result)

                self.time_stamp = time.time()
                self.queue.task_done()


def main():
    # 将一些提交更新为wait，模拟实时比赛
    # init_db = MySQLdb.connect(DATABASE_INFO['ip'], DATABASE_INFO['user'],
    #                    DATABASE_INFO['pwd'], DATABASE_INFO['database'], charset='utf8')
    # result2wait(init_db)

    # 正式过程
    que = Queue.Queue()
    db = MySQLdb.connect(DATABASE_INFO['ip'], DATABASE_INFO['user'],
                         DATABASE_INFO['pwd'], DATABASE_INFO['database'], charset='utf8')
    # 根据json文件里的用户密码数量创建对应个数worker
    info = json.load(open('user-pwd.json'))
    for ele in info:
        uid = ele['user']
        pwd = ele['pwd']
        worker = SubmitWorker(uid, pwd, que)
        worker.daemon = True
        worker.start()
    # problem_id 1039 solution_id 5054
    try:
        logger.info('start monitor.')
        flag = True
        while True:
            if flag:
                logger.info('try getting queueing submission.')

            flag = wait2que(db, que)

            que.join()
            if flag:
                logger.info('get queueing submission end.')
            time.sleep(3)

    except KeyboardInterrupt:
        print ''
        logger.warning('user abort.')

if __name__ == '__main__':
    main()
