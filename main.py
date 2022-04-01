import os
from PIL import Image, ImageTk
import time
import threading
import tkinter as tk
import traceback
from tkinter import ttk
from tkinter import messagebox
from legym_fix.api import login


user = None
select_idx = None
code, name, status = None, None, None
is_loop = False
stop_loop = False

class Catcher: 
    def __init__(self, func, subst, widget):
        self.func = func 
        self.subst = subst
        self.widget = widget
    def __call__(self, *args):
        try:
            if self.subst:
                args = self.subst(*args)
            return self.func(*args)
        except SystemExit:
            raise
        except BaseException as e:
            messagebox.showerror(title='Error', message=e)
            traceback.print_exc(file=open('error.log', 'a'))

    
def handle_login():
    global user
    user = login(username.get(), password.get())
    user_info.delete('1.0', 'end')
    user_info.insert('insert', f'Name: {user.nick_name}\nOrganization: {user.organization}\nSchool: {user.school}')

def handle_save_user():
    global username, password
    username, password = username.get(), password.get()
    if username is None or password is None:
        messagebox.showerror(title='Error', message=f'请先填写用户名和密码！')
        return

    with open('user_info.cfg', 'w') as f:
        f.write(f'{username}:{password}')

def handle_get_activity():
    if user is None:
        messagebox.showerror(title='Error', message=f'请先登录！')
        return
        
    activities = user.get_activities().search()
    if len(activities) == 0:
        messagebox.showinfo(title='Info', message=f'没有可选的活动！')

    x = activity_info.get_children()
    for item in x:
        activity_info.delete(item)

    for idx, acticity in enumerate(activities):
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
        activity_info.insert('', idx, text=f'{idx}', values=[code, name, status, interval])


def handle_select_activity(event):
    global code, name, status
    idx = event.widget.selection()[0]
    code, name, status, _ = activity_info.item(idx)['values']

def handle_register():
    res = user.register(code=code, name=name)
    if isinstance(res, list):
        res = res[0]
    if res[1]:
        messagebox.showinfo(title='Success',message=f'{res[2]}')
    else:
        messagebox.showerror(title='Error', message=f'{res[2]}')
    handle_get_activity()

def handle_sign():
    res = user.sign(code=code, name=name)
    if isinstance(res, list):
        res = res[0]

    if res[1]:
        messagebox.showinfo(title='Success',message=f'{res[2]}')
    else:
        messagebox.showerror(title='Error', message=f'{res[2]}')
    handle_get_activity()

def loop_sign():
    global stop_loop
    step = 1
    res = user.sign(code=code, name=name)

    if isinstance(res, list):
        res = res[0]

    activity = user.get_activities().search(code=code, name=name)[0]
    loop_sign_info.insert('insert', f'step{step}: {res[2]}, 当前状态: {activity.state}\n') 
    
    handle_get_activity()

    while activity.state != 'completed':
        if stop_loop:
            break

        step += 1
        time.sleep(30)

        res = user.sign(code=code, name=name)
        if isinstance(res, list):
            res = res[0]
            
        activity = user.get_activities().search(code=code, name=name)[0]
        loop_sign_info.insert('insert', f'step{step}: {res[2]}, 当前状态: {activity.state}\n') 
        loop_sign_info.see('end')

        handle_get_activity()

t = threading.Thread(target=loop_sign)

def handle_loop_sign():
    global is_loop, stop_loop
    stop_loop = False
    if not is_loop:
        t.start()
    is_loop = True

def handle_stop_loop_sign():
    global is_loop, stop_loop
    stop_loop = True
    is_loop = False


window = tk.Tk()
window.title('No More Legym V0.3')

tk.CallWrapper = Catcher

frame1 = tk.Frame(window, relief=tk.RAISED, borderwidth=2)
frame1.pack(side='left', fill='y', ipadx=13, ipady=13, expand=0)

tk.Label(frame1, text='Username:啊啊').pack()
username = tk.Entry(frame1)
username.pack()

tk.Label(frame1, text='Password:').pack()
password = tk.Entry(frame1)
password.pack()

login_btn = tk.Button(frame1, text='Login', command=handle_login)
login_btn.pack()

save_user_btn = tk.Button(frame1, text='Save User', command=handle_save_user)
save_user_btn.pack()

user_info = tk.Text(frame1, width=60, height=5)
user_info.pack()

get_activity_btn = tk.Button(frame1, text='Get Activity', command=handle_get_activity)
get_activity_btn.pack()

img_open = Image.open("yui.png")
img_png = ImageTk.PhotoImage(img_open)
label_img = tk.Label(frame1, image = img_png)
label_img.pack()

activity_info = ttk.Treeview()
activity_info['columns'] = ['code','name','status', 'interval']
activity_info.column('code', width=100)
activity_info.column('name', width=300)
activity_info.column('status', width=100)
activity_info.column('interval', width=100)
activity_info.heading('code', text='code')
activity_info.heading('name', text='name')
activity_info.heading('status', text='status')
activity_info.heading('interval', text='time interval')
activity_info.bind('<<TreeviewSelect>>', handle_select_activity)
activity_info.pack()

frame2 = tk.Frame(frame1, relief=tk.RAISED, borderwidth=0)
frame2.pack(ipadx=13, ipady=13, expand=0)

register_btn = tk.Button(frame2, text='Register', command=handle_register)
register_btn.pack(side='left')

sign_btn = tk.Button(frame2, text='Sign', command=handle_sign)
sign_btn.pack(side='left')

loop_sign_btn = tk.Button(frame2, text='Loop Sign', command=handle_loop_sign)
loop_sign_btn.pack(side='left')

stop_loop_sign_btn = tk.Button(frame2, text='Stop Loop Sign', command=handle_stop_loop_sign)
stop_loop_sign_btn.pack(side='left')

loop_sign_info = tk.Text(window, width=114, height=30)
loop_sign_info.pack()

tk.Label(window, text='Copyright ©2022- Koorye designed, All Rights Reserved.').pack(side='bottom', anchor='s')

if os.path.exists('user_info.cfg'):
    with open('user_info.cfg') as f:
        s = f.readlines()
        username_, password_ = s[0].split(':')
    username.insert(0, username_)
    password.insert(0, password_)

window.mainloop()