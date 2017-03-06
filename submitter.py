# encoding=utf-8
from utils import logger
from robobrowser import RoboBrowser
import time
import html5lib


class GPLT:
    # base information:
    URL_HOME = 'https://www.patest.cn/'
    URL_LOGIN = URL_HOME + 'users/sign_in'
    URL_SUBMIT = URL_HOME + 'contests/gplt/'

    # language
    LANGUAGE = {
        'C': '3',
        'C++': '2',
        'JAVA': '10',
    }

    def __init__(self, user_id, password):
        self.user_id = user_id
        self.password = password
        self.browser = RoboBrowser(parser='html5lib')
        self.compile_info = None
        self.result_url = None
        self.result = None
        self.case_result = None

    def login(self):
        self.browser.open(GPLT.URL_LOGIN)
        enter_form = self.browser.get_form('new_user')
        if not enter_form:
            return False

        enter_form['user[handle]'] = self.user_id
        enter_form['user[password]'] = self.password

        self.browser.submit_form(enter_form)

        checks = list(map(lambda x: x.getText()[1:].strip(),
                          self.browser.select('span.btn.btn-primary.btn-xs')))
        if self.user_id not in checks:
            return False

        return True

    def submit(self, problem_grade, problem_num, language, src_code):
        problem_grade = 'L%d-' % problem_grade
        problem_num = '%03d' % problem_num

        try:
            language = int(language)
        except Exception as e:
            logger.warning('language not int code.')
            try:
                language = GPLT.LANGUAGE[str(language).upper()]
            except Exception as e:
                logger.exception(e)
                return False

        self.browser.open(GPLT.URL_SUBMIT + problem_grade + problem_num)

        try:
            submit_form = self.browser.get_form()
            submit_form['code'] = src_code
            submit_form['compiler_id'] = str(language)
        except Exception as e:
            logger.exception(e.__class__.__name__ + ": maybe submit quickly.")
            return False

        self.browser.submit_form(submit_form)

        self.result_url = self.browser.url
        if self.browser.url[22:33] != 'submissions':
            return False

        return True

    def get_result(self):
        # require after submit redirect
        self.browser.open(self.result_url)
        table = self.browser.find('table')
        table_body = table.find('tbody')
        row = table_body.find('tr')
        cols = row.find_all('td')
        data = [ele.text.strip() for ele in cols]
        # 时间  结果	得分	题目	语言	用时(ms)	内存(kB)	用户

        logger.info('[user:{user}] status:{status}.'.format(user=self.user_id, status=data[1].encode('utf-8')))

        if data[1] in [u'等待评测', u'正在评测']:
            return False

        self.result = data

        if data[1] == u'编译错误':
            self.browser.open(self.result_url + '/log')
            info = self.browser.find('pre').text
            self.compile_info = str(info.encode('utf8'))

        table = self.browser.find('table', {'id': 'case_result_list'})
        if not table:
            logger.warning('No test case info!')
            return True

        table_body = table.find('tbody')
        rows = table_body.find_all('tr')
        case_result = []
        for row in rows:
            cols = row.find_all('td')
            cols = [ele.text.strip() for ele in cols]
            case_result.append([ele.encode('utf8') for ele in cols])

        self.case_result = case_result
        return True


def _submit(problem_grade, problem_num, language, src_code, username, password):
    try:
        g = GPLT(username, password)
        logger.info('[user:{user}]'.format(user=username))
        if g.login():
            logger.info('[user:{user}] login success.'.format(user=username))
            if g.submit(problem_grade, problem_num, language, src_code):
                logger.info('[user:{user}] submit success.'.format(user=username))
                flag = g.get_result()
                while not flag:
                    time.sleep(1)
                    flag = g.get_result()
                return {'result': g.result, 'case_result': g.case_result, 'compile_info': g.compile_info}
    except Exception as e:
        info = e.__class__.__name__ + ":" + e.message
        logger.exception(info)
        return {}


if __name__ == '__main__':
    src = '''
    #include<bits/stdc++.h>
    using namespace std;
    map<char,string> M;
qwewqewqewq
    string s;
    int main(){
      M['0']="ling";M['1']="yi";
    M['2']="er";M['3']="san";
    M['4']="si";M['5']="wu";M['6']="liu";
    M['7']="qi";M['8']="ba";
    M['9']="jiu";
      while(cin>>s){
        for(int i=0;i<s.length();i++){
            if(i==0)cout<<M[s[i]];
          else cout<<" "<<M[s[i]];
        }
        cout<<endl;
      }
        return 0;
    }
    '''
    inf = _submit(1, 7, 'c++', src)
    print inf['compile_info'] , type(inf['compile_info'])
