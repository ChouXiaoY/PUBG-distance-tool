import sys
import math
import threading
from PyQt5 import QtCore, QtGui, QtWidgets
import keyboard


class TransparentOverlay(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        # 初始化比例
        self.pixel_per_100m = None  # 需要先测量
        self.scale = None  # 每像素对应多少米

        self.setWindowFlags(
            QtCore.Qt.WindowStaysOnTopHint |
            QtCore.Qt.FramelessWindowHint |
            QtCore.Qt.Tool
        )
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.setWindowState(QtCore.Qt.WindowFullScreen)

        # 半透明灰色背景
        self.background_color = QtGui.QColor(128, 128, 128, 50)

        self.is_setting_scale = True  # 初始进入比例设置模式
        self.scale_start = None
        self.scale_end = None

        self.start_point = None
        self.end_point = None

        self.show()

    def paintEvent(self, event):
        qp = QtGui.QPainter(self)
        qp.fillRect(self.rect(), self.background_color)

        pen = QtGui.QPen(QtCore.Qt.red, 2)
        qp.setPen(pen)

        if self.is_setting_scale and self.scale_start and self.scale_end:
            # 绘制比例测量线
            qp.drawLine(self.scale_start, self.scale_end)

            dx = self.scale_end.x() - self.scale_start.x()
            dy = self.scale_end.y() - self.scale_start.y()
            pixel_distance = math.hypot(dx, dy)

            text = f"设置比例: {pixel_distance:.2f} px = 100m"
            qp.setFont(QtGui.QFont('Arial', 16))
            midpoint = QtCore.QPoint(
                (self.scale_start.x() + self.scale_end.x()) // 2,
                (self.scale_start.y() + self.scale_end.y()) // 2
            )
            qp.drawText(midpoint, text)

        if not self.is_setting_scale and self.start_point and self.end_point:
            # 绘制正常测量线
            qp.drawLine(self.start_point, self.end_point)

            dx = self.end_point.x() - self.start_point.x()
            dy = self.end_point.y() - self.start_point.y()
            pixel_distance = math.hypot(dx, dy)

            meter_distance = pixel_distance * self.scale

            text = f"{meter_distance:.2f} m"
            qp.setFont(QtGui.QFont('Arial', 16))
            midpoint = QtCore.QPoint(
                (self.start_point.x() + self.end_point.x()) // 2,
                (self.start_point.y() + self.end_point.y()) // 2
            )
            qp.drawText(midpoint, text)

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            if self.is_setting_scale:
                if not self.scale_start:
                    self.scale_start = event.pos()
                elif not self.scale_end:
                    self.scale_end = event.pos()

                    # 计算比例
                    dx = self.scale_end.x() - self.scale_start.x()
                    dy = self.scale_end.y() - self.scale_start.y()
                    pixel_distance = math.hypot(dx, dy)

                    self.pixel_per_100m = pixel_distance
                    self.scale = 100 / self.pixel_per_100m
                    print(f"比例设置完成：{self.pixel_per_100m:.2f}像素 = 100米")

                    self.is_setting_scale = False  # 进入正常测量模式

                    self.update()
                else:
                    # 重新开始设置
                    self.scale_start = event.pos()
                    self.scale_end = None
                    self.update()

            else:
                if not self.start_point:
                    self.start_point = event.pos()
                elif not self.end_point:
                    self.end_point = event.pos()
                    self.update()
                else:
                    # 第三次点击重置
                    self.start_point = event.pos()
                    self.end_point = None
                    self.update()

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Escape:
            self.close()
        elif event.key() == QtCore.Qt.Key_R:
            # 按R键重新进入比例设置模式
            self.is_setting_scale = True
            self.scale_start = None
            self.scale_end = None
            self.start_point = None
            self.end_point = None
            self.update()


def launch_overlay():
    app = QtWidgets.QApplication(sys.argv)
    overlay = TransparentOverlay()

    sys.exit(app.exec_())


def start_hotkey_listener():
    while True:
        keyboard.wait('ctrl+alt+d')
        threading.Thread(target=launch_overlay).start()


if __name__ == "__main__":
    listener_thread = threading.Thread(target=start_hotkey_listener, daemon=True)
    listener_thread.start()

    print("按 Ctrl + Alt + D 启动测量，Esc退出窗口，R重新设置比例。")
    keyboard.wait('esc')

