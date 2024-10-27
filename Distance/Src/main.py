import keyboard
import pyautogui
import math
from PySide6.QtWidgets import QApplication, QLabel
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QFont
import json
import re


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
        with open('Distance/Src/config.json', 'r', encoding="utf-8") as f:
            self.data = json.load(f)
        return self.data

    def WriteDataToJson(self):
        with open('Distance/Src/config.json', 'w', encoding="utf-8") as f:
            json.dump(self.data, f, indent=4, ensure_ascii=False)

    def ChangeData(self, ScaleValue=None):
        print("请选择序号更改对应地图尺寸的缩放比例(输入0表示退出):")
        count = 1
        for Item in self.data["list"]:
            print(f"{count}:尺寸:{Item['name']} 缩放比例:{Item['value']}")
            count += 1
        while True:
            ChooseItem = input()
            if ChooseItem == '0':
                break
            elif not ChooseItem.isdigit() or int(ChooseItem) not in range(1, count):
                print("请输入有效数字！")
            else:
                # 获取用户选择的下标
                index = int(ChooseItem) - 1
                # 获取对应的数据项
                selected_item = self.data["list"][index]
                if ScaleValue is None:
                    print(f"已选择{selected_item['name']},请输入要修改的缩放比例为(输入0放弃修改):")
                    while True:
                        ScaleValue = input()
                        if ScaleValue == '0':
                            print("已放弃修改")
                            break
                        elif not is_float(ScaleValue):
                            print("请输入数字")
                        else:
                            ScaleValue = float(ScaleValue)
                            self.data["list"][index]["value"] = ScaleValue
                            self.WriteDataToJson()
                            print(
                                f"修改完成，新数值为:{self.data['list'][index]['name']},{self.data['list'][index]['value']}")
                            break
                else:
                    ScaleValue = float(ScaleValue)
                    self.data["list"][index]["value"] = ScaleValue
                    self.WriteDataToJson()
                    print(
                        f"修改完成，新数值为:{self.data['list'][index]['name']},{self.data['list'][index]['value']}")
                break

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
                # 获取用户选择的下标
                index = int(ChooseItem) - 1
                ScaleValue = float(self.data['list'][index]['value'])
                return ScaleValue


class TextOverlay(QLabel):
    def __init__(self, text):
        super().__init__()

        # 设置文字
        self.setText(text)
        self.setFont(QFont("Arial", 16, QFont.Bold))
        self.setStyleSheet("color: white;")

        # 设置窗口无边框和透明背景
        # 使用 Qt.Tool 以隐藏在任务栏
        self.setWindowFlags(Qt.FramelessWindowHint |
                            Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)

        # 自动调整窗口大小以适应文字
        self.adjustSize()


class KeyboardListener(QThread):
    update_distance = Signal(float)
    # update_ratio = Signal(float)  # 新信号用于传递比值

    def __init__(self):
        super().__init__()
        self.position1 = None
        self.distance = None  # 用于存储上一次的距离

    def run(self):
        keyboard.add_hotkey("ctrl+g", self.on_ctrl_key)  # 处理 Ctrl+G
        # 处理 Ctrl+Shift+G
        keyboard.add_hotkey("ctrl+shift+g", self.on_ctrl_key)

        while True:
            keyboard.wait()

    def on_ctrl_key(self):
        global ratio
        if self.position1 is None:
            self.position1 = pyautogui.position()
            print("记录第一个位置：", self.position1)
        else:
            position2 = pyautogui.position()
            print("记录第二个位置：", position2)
            self.distance = math.sqrt(
                (position2[0] - self.position1[0]) ** 2 + (position2[1] - self.position1[1]) ** 2)
            print(f"两个位置之间的距离为: {self.distance*ratio} m")

            # 计算并发送比值（仅在按下 Ctrl+Shift+G 时）
            if keyboard.is_pressed("ctrl+shift+g"):
                ratio = 1000 / \
                    self.distance if self.distance != 0 else float(
                        'inf')  # 防止除以零
                ratio = round(ratio, 2)
                print(f"1000 / distance 的比值为: {ratio}")
                # self.update_ratio.emit(ratio)  # 发送比值信号

            # 发送信号给主线程更新距离
            else:
                self.update_distance.emit(self.distance*ratio)
            # 重置位置
            self.position1 = None


def display_distance(distance):
    data = round(distance, 2)
    overlay.setText(f"两个位置之间的距离为: {data} m")
    overlay.adjustSize()


# def display_ratio(ratio):
#     overlay.setText(f"1000 / distance 的比值为: {ratio:.2f}")
#     overlay.adjustSize()

# 外部设置单独的按键识别作线程关闭处理


def close_thread():
    listener.terminate()
    app.exit()


Fjson = JsonIO("Distance/Src/config.json")
ratio = Fjson.GetScaleValue()

app = QApplication()

overlay = TextOverlay("")
overlay.show()
overlay.move(0, 0)

listener = KeyboardListener()
listener.update_distance.connect(display_distance)
# listener.update_ratio.connect(display_ratio)  # 连接比值更新的信号
listener.start()


keyboard.add_hotkey('ctrl+q', close_thread)

app.setQuitOnLastWindowClosed(False)

app.exec()
