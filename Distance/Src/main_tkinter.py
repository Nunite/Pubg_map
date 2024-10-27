import pyautogui
import math
import threading
import json
import re
from pynput import keyboard
import tkinter as tk
from tkinter import simpledialog

# 全局变量初始化
position1 = None
ratio = None
overlay_visible = True  # 用于控制显示框的可见性


def is_float(value):
    pattern = r'^-?\d+(\.\d+)?$'
    match = re.match(pattern, value)
    return bool(match)


class JsonIO:
    def __init__(self, filepath):
        self.filepath = filepath
        self.data = None
        self.GetDataFromJson()

    def GetDataFromJson(self):
        with open(self.filepath, 'r', encoding="utf-8") as f:
            self.data = json.load(f)
        return self.data

    def WriteDataToJson(self):
        with open(self.filepath, 'w', encoding="utf-8") as f:
            json.dump(self.data, f, indent=4, ensure_ascii=False)

    def GetScaleValue(self):
        print("选择对应地图尺寸的缩放比例:")
        count = 1
        scale_options = []

        for Item in self.data['list']:
            print(f"{count}: 尺寸: {Item['name']} 缩放比例: {Item['value']}")
            scale_options.append((count, Item['value']))
            count += 1
        # scale_options.append((0, "退出"))

        # 使用对话框获取用户输入
        while True:
            options_text = "\n".join(
                f"{num}: {value}" for num, value in scale_options)
            user_input = simpledialog.askstring("选择缩放比例", options_text)

            if user_input is None:
                print("对话框已关闭，程序结束。")
                exit(0)  # 用户关闭对话框，退出程序

            if user_input.isdigit():
                choice = int(user_input)
                if 0 < choice < count:
                    if choice == 0:
                        exit(0)  # 用户选择退出
                    else:
                        ScaleValue = float(
                            self.data['list'][choice - 1]['value'])
                        return ScaleValue
            else:
                print("请输入有效数字！")


class TextOverlay(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("距离计算器")
        self.geometry("350x100")  # 设置窗口大小
        self.attributes("-topmost", True)  # 窗口始终在最上层
        self.overrideredirect(True)  # 去掉窗口边框
        self.wm_attributes("-transparentcolor", "black")  # 设置透明颜色为黑色
        self.label = tk.Label(self, text="", font=(
            "Arial", 16, "bold"), fg="white", bg="black")
        self.label.pack(expand=True, fill=tk.BOTH)

    def update_text(self, text):
        self.label.config(text=text)

    def toggle_visibility(self):
        global overlay_visible
        overlay_visible = not overlay_visible
        if overlay_visible:
            self.deiconify()  # 显示窗口
        else:
            self.withdraw()  # 隐藏窗口


def handle_key_combination(shift_pressed):
    global position1, ratio
    print("处理键盘组合")
    if position1 is None:
        position1 = pyautogui.position()
        print("记录第一个位置：", position1)
    else:
        position2 = pyautogui.position()
        print("记录第二个位置：", position2)
        distance = math.sqrt(
            (position2[0] - position1[0]) ** 2 +
            (position2[1] - position1[1]) ** 2
        )
        print(f"两个位置之间的距离为: {distance * ratio} m")
        if shift_pressed:
            ratio = 1000 / distance if distance != 0 else float('inf')
            ratio = round(ratio, 2)
            print(f"1000 / distance 的比值为: {ratio}")
        if distance is not None:
            display_distance(distance * ratio)
        position1 = None


def display_distance(distance):
    data = round(distance, 2)
    print(f"接收到的距离: {data}")
    overlay.update_text(f"两个位置之间的距离为: {data} m")


def toggle_overlay_visibility():
    overlay.toggle_visibility()


def on_press(key):
    try:
        if key == keyboard.Key.ctrl_l:
            handle_key_combination(shift_pressed=False)
        elif key == keyboard.Key.ctrl_r:
            handle_key_combination(shift_pressed=True)
        elif key == keyboard.Key.alt_gr:  # 右 Alt 键
            toggle_overlay_visibility()
        elif key == keyboard.Key.esc:  # ESC 键退出程序
            print("退出程序")
            overlay.quit()  # 退出 Tkinter 主循环
            overlay.destroy()  # 关闭 Tkinter 窗口
    except AttributeError:
        pass


def start_keyboard_listener():
    with keyboard.Listener(on_press=on_press) as listener:
        listener.join()


if __name__ == '__main__':
    # 创建 Tkinter 根窗口
    root = tk.Tk()
    root.withdraw()  # 隐藏根窗口

    # 读取配置文件
    Fjson = JsonIO(
        "D:\Code_Development\Learn\Python\Pubg\Distance\Src\config.json")
    ratio = Fjson.GetScaleValue()

    overlay = TextOverlay()
    overlay.geometry("+100+100")  # 设置窗口初始位置

    # 使用 threading.Thread 启动键盘监听线程
    listener_thread = threading.Thread(target=start_keyboard_listener)
    listener_thread.daemon = True  # 改为使用 daemon 属性
    listener_thread.start()

    # 启动 Tkinter 应用程序
    overlay.mainloop()
