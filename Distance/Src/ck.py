# -*- coding: utf-8 -*-
"""
Created on Sun Aug 25 11:52:41 2024

@author: ZHOU
"""
import threading
import tkinter as tk  # 调用窗口tk

from pynput import mouse, keyboard

font_style = ("Arial", 10, "bold")
global width
width = 0

global admin
admin = tk.Tk()

global flag
global judg_y
global judg_x
global judg_flag
global judg_size
flag = 0
judg_x = 0
judg_y = 0
judg_flag = 0

global win_flag
win_flag = 1
CheckVar = tk.IntVar()


def set_win():
    global win_flag
    if win_flag:
        admin.withdraw()
        win_flag = 0
    else:
        admin.update()
        admin.deiconify()
        win_flag = 1


def callback(k, li):
    global admin

    global flag
    global judg_y
    global judg_x
    global judg_flag
    global judg_size
    global width

    if flag == 0:
        if 'alt_l' in k:
            flag = 1

    elif flag == 1:
        if '97' in k or '98' in k or '99' in k or '100' in k or '101' in k or '102' in k or '103' in k or '104' in k:
            i = int(k.split("<")[1].split(">")[0])-96
            judg_flag = width/i
            print("地图大小：", judg_flag)
            tk.Label(admin, text="", justify=tk.LEFT, bg="white",
                     font=font_style, fg="blue").place(x=130, y=0, width=50, height=20)
            tk.Label(admin, text=str(i), justify=tk.LEFT, bg="white",
                     font=font_style, fg="blue").place(x=180, y=0, width=20, height=20)
            tk.Label(admin, text="", justify=tk.LEFT, bg="white",
                     font=font_style, fg="blue").place(x=200, y=0, width=120, height=20)

            flag = 1
        elif "'1'" == k or "'2'" == k or "'3'" == k or "'4'" == k or "'5'" == k:
            if judg_flag < 1:
                flag = 0
                print("请先确定地图大小")
            else:
                try:
                    judg_size = (int(k.split("'")[1])*1)
                    judg_size = int(pow(2, judg_size-1))
                    if judg_size == 2:
                        judg_size = 2.1
                    print("缩放大小: ", judg_size)
                    flag = 2
                except:
                    flag = 0
    elif flag == 2:
        if k == '' and 'right' in li[2]:
            judg_x = int(li[0])
            judg_y = int(li[1])
            flag = 3

    elif flag == 3:
        if k == '' and 'right' in li[2]:
            x = int(li[0])
            y = int(li[1])

            f = pow(pow(abs(x-judg_x), 2)+pow(abs(y-judg_y), 2), 0.5)
            re = int((f/judg_flag*1000)/judg_size)
            print(re, judg_size)

            tk.Label(admin, text=str(re), justify=tk.LEFT,
                     font=font_style).place(x=0, y=0, width=50, height=20)

            judg_x = 0
            judg_y = 0
            flag = 0
            judg_size = 0
    else:
        judg_x = 0
        judg_y = 0
        flag = 0
        judg_size = 0


def on_mouse_move(x, y):
    pass
#    print(f'鼠标移动到位置: ({x}, {y})')


def on_mouse_click(x, y, button, pressed):
    if pressed:
        callback('', [x, y, str(button)])
#        print(f'{button} 按下于位置: ({x}, {y})')
    else:
        pass
#        print(f'{button} 释放于位置: ({x}, {y})')


def on_mouse_scroll(x, y, dx, dy):
    pass
    # dx 和 dy 表示滚动的水平方向和垂直方向的量
    # 在大多数鼠标上，只有 dy 会变化，表示垂直滚动
#    print(f'Scrolled at {x}, {y} ({dx}, {dy})')


def on_key_press(key):
    callback(str(key), [])


def release_callback(k):
    global flag
    global judg_y
    global judg_x
    global judg_flag
    global judg_size

    if "'m'" == k:
        if not CheckVar.get():
            set_win()

    if 'alt_l' in k:
        judg_x = 0
        judg_y = 0
        flag = 0
        judg_size = 0


def on_key_release(key):
    release_callback(str(key))
#    try:
#        print(f'{key.char} 被释放')
#    except AttributeError:
#        print(f'{key} 被释放')


global mouse_listener
global keyboard_listener
# 创建鼠标监听器
mouse_listener = mouse.Listener(
    on_move=on_mouse_move, on_click=on_mouse_click, on_scroll=on_mouse_scroll)

# 创建键盘监听器，同时监听按下和释放事件
keyboard_listener = keyboard.Listener(
    on_press=on_key_press, on_release=on_key_release)


def key_start():
    global mouse_listener
    global keyboard_listener
    mouse_listener.start()
    keyboard_listener.start()
    mouse_listener.join()
    keyboard_listener.join()


global t
t = threading.Thread(target=key_start)


def gui():
    global admin
    admin.title("网易独家音乐人MikeZhou")
    admin.attributes('-topmost', 1)
    admin.resizable(0, 0)

    adminfram = tk.Frame(admin, width=320, height=20)
    adminfram.grid_propagate(0)
    adminfram.grid()

    tk.Checkbutton(admin, text="始终", variable=CheckVar, onvalue=1,
                   offvalue=0).place(x=80, y=0, width=50, height=20)

    e1 = tk.Entry(adminfram)
    e1.delete(0, tk.END)  # 将输入框里面的内容清空
    e1.insert(0, "")
    e1.place(x=0, y=0, width=80, height=20)

    tk.Label(admin, text='地图:', justify=tk.LEFT, bg="white",
             font=font_style, fg="blue").place(x=130, y=0, width=50, height=20)

    Button = 0

    def go_key():
        global width
        global t

        try:
            i = int(float(str(e1.get())))
            if i < 100:
                print("太小了")
                return
            width = i
            print("已设置屏幕大小:", width)
        except:
            print("输入整形")
            e1.delete(0, tk.END)  # 将输入框里面的内容清空
            e1.insert(0, "")
            return

        e1.config(state='normal')
        e1.delete(0, tk.END)  # 将输入框里面的内容清空
        e1.insert(0, "")
        tk.Label(admin, text="", justify=tk.LEFT, bg="white",
                 font=font_style).place(x=0, y=0, width=130, height=20)
        tk.Label(admin, text="", justify=tk.LEFT, bg="white",
                 font=font_style).place(x=180, y=0, width=20, height=20)
        Button.destroy()

        admin.overrideredirect(True)
        admin.attributes("-transparentcolor", "white")
        tk.Label(admin, text='屏幕: '+str(width), justify=tk.LEFT, bg="white",
                 font=font_style, fg="blue").place(x=200, y=0, width=120, height=20)

        t.setDaemon(True)
        t.start()

    Button = tk.Button(adminfram, width=30, text="设置屏幕大小", command=go_key)
    Button.place(x=200, y=0, width=120, height=20)
    admin.mainloop()


def main():
    global mouse_listener
    global keyboard_listener
    gui()
    keyboard_listener.stop()
    mouse_listener.stop()


if __name__ == '__main__':
    main()
