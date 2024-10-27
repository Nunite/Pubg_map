import pyautogui
import math
import threading
from PySide6.QtWidgets import QApplication, QLabel
from PySide6.QtCore import Qt, Slot
from PySide6.QtGui import QFont
import json
import re
from pynput import keyboard

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
        print("选择对应地图尺寸的缩放比例(输入0表示退出):")
        count = 1
        for Item in self.data['list']:
            print(f"{count}:尺寸:{Item['name']} 缩放比例:{Item['value']}")
            count += 1
        while True:
            ChooseItem = input()
            if ChooseItem == '0':
                break
            elif not ChooseItem.isdigit() or int(ChooseItem) not in range(1, count):
                print("请输入有效数字！")
            else:
                index = int(ChooseItem) - 1
                ScaleValue = float(self.data['list'][index]['value'])
                return ScaleValue


class TextOverlay(QLabel):
    def __init__(self, text):
        super().__init__()
        self.setText(text)
        self.setFont(QFont("Arial", 16, QFont.Bold))
        self.setStyleSheet("color: white;")
        self.setWindowFlags(Qt.FramelessWindowHint |
                            Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.adjustSize()


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


@Slot(float)
def display_distance(distance):
    data = round(distance, 2)
    print(f"接收到的距离: {data}")
    overlay.setText(f"两个位置之间的距离为: {data} m")
    overlay.adjustSize()


def toggle_overlay_visibility():
    global overlay_visible
    overlay_visible = not overlay_visible
    overlay.setVisible(overlay_visible)
    print("显示框状态切换:", "显示" if overlay_visible else "隐藏")


def on_press(key):
    try:
        if key == keyboard.Key.ctrl_l:
            handle_key_combination(shift_pressed=False)
        elif key == keyboard.Key.ctrl_r:
            handle_key_combination(shift_pressed=True)
        elif key == keyboard.Key.alt_gr:  # 右 Alt 键
            toggle_overlay_visibility()
    except AttributeError:
        pass


def start_keyboard_listener():
    with keyboard.Listener(on_press=on_press) as listener:
        listener.join()


if __name__ == '__main__':
    Fjson = JsonIO(
        "D:\Code_Development\Learn\Python\Pubg\Distance\Src\config.json")
    ratio = Fjson.GetScaleValue()

    app = QApplication([])

    overlay = TextOverlay("")
    overlay.show()
    overlay.move(100, 100)

    # 使用 threading.Thread 启动键盘监听线程
    listener_thread = threading.Thread(target=start_keyboard_listener)
    listener_thread.daemon = True  # 改为使用 daemon 属性
    listener_thread.start()

    # 启动 Qt 应用程序
    app.exec()
