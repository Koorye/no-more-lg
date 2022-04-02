import os
import time
from os import system, name
from legym_fix.api import login


def clear_screen():
    if name == 'nt':
        system('cls')
    else:
        system('clear')

def print_green(s, end='\n'):
    print('\033[32m' + s + '\033[0m', end=end)

def print_red(s, end='\n'):
    print('\033[31m' + s + '\033[0m', end=end)

def show_info(user):
    print('姓名：', end='')
    print_green(user.nick_name, end='')
    print('，组织：', end='')
    print_green(user.organization, end='')
    print('，学校：', end='')
    print_green(user.school)


def save_user(username, password):
    with open('user_info.cfg', 'w') as f:
        f.write(f'{username}:{password}')

def remove_user():
    os.remove('user_info.cfg')

def show_activity(user):
    print('正在搜索活动，请耐心等待...')
    activities = user.get_activities().search()
    activities = list(filter(lambda x: x.state != 'blocked', activities))

    if len(activities) == 0:
        print_red('没有可选的活动！')
        return

    for acticity in activities:
        code, name, status, interval = acticity.code, acticity.name, acticity.state, acticity.timeInterval
        if status == 'available':
            status = '可报名'
        elif status == 'registered':
            status = '已报名'
        elif status == 'signed':
            status = '已签到一次'
        elif status == 'completed':
            status = '已完成'
        
        if interval:
            interval = f'{interval:.2f}min'
        else:
            interval = '-'

        print('代码：', end='')
        print_green(code, end='')
        print('\t名称：', end='')
        print_green(name, end='')

        print('\t状态：', end='')
        if status in ['可报名', '已报名']:
            print_green(status, end='')
        else:
            print_red(status, end='')

        print('\t剩余时间：', end='')
        if interval == '-':
            print_green(interval)
        else:
            print_red(interval)


def handle_register(user, code):
    res = user.register(code=code)
    if isinstance(res, list):
        res = res[0]

    if res[1]:
        msg = '报名成功！'
    else:
        msg = '报名失败！'
    
    return msg



def handle_sign(user, code):
    res = user.sign(code=code)
    if isinstance(res, list):
        res = res[0]

    if res[1]:
        msg = '签到成功！'
    else:
        msg = '签到失败！'
        
    return msg


def main():
    clear_screen()
    if os.path.exists('user_info.cfg'):
        with open('user_info.cfg') as f:
            s = f.readlines()
            username, password = s[0].split(':')
            print_green('检测到之前保存的用户配置！')
            time.sleep(1)
    else:
        username = input('请输入用户名：')
        password = input('请输入密码：')
        save_user(username, password)
        print_green('当前用户信息已保存！')
        time.sleep(1)
    
    user = login(username, password)
    
    msg = None
    while True:
        clear_screen()
        show_info(user)
        show_activity(user)
            
        print('---------------------------------------------------------')
        print('1. ', end='')
        print_green('活动报名：r(空格)活动代码')
        print('2. ', end='')
        print_green('活动签到：s(空格)活动代码')
        print('3. ', end='')
        print_green('活动刷新：s')
        print('4. ', end='')
        print_green('退出：q')
        print('5. ', end='')
        print_green('删除用户配置并退出：d')
        print('---------------------------------------------------------')

        if msg is not None:
            if msg.endswith('成功！'):
                print_green(msg)
            else:
                print_red(msg) 

        s = input('请输入命令：')
        s = s.split(' ')
        if len(s) == 1:
            op = s[0]
            if op == 'q':
                exit(0)
            elif op == 'd':
                print_red('确定删除用户配置？这将导致保存的用户名和密码丢失(y/n)：', end='')
                res = input()
                if res == 'y':
                    remove_user()
                    exit(0)
                else:
                    msg = '当前操作已取消！'
            elif op == 's':
                msg = '活动刷新成功！'
            else:
                msg = '不支持的操作类型！'
        elif len(s) == 2:
            op, code = s[0], s[1]
            if op == 'r':
                msg = handle_register(user, code)
            elif op == 's':
                msg = handle_sign(user, code)
            else:
                msg = '不支持的操作类型！'
        else:
            msg = '不支持的操作类型！'

if __name__ == '__main__':
    main()
