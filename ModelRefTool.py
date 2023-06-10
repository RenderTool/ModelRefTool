from PySide2 import QtCore, QtGui, QtWidgets
import qtmax

from pymxs import runtime as rt

class ChildWindow(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(QtCore.Qt.Tool | QtCore.Qt.FramelessWindowHint)
        # self.setWindowTitle("Child Window")

        self.image_label = QtWidgets.QLabel()
        self.image_label.setAlignment(QtCore.Qt.AlignCenter)

        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.addWidget(self.image_label)

        self.images = []  # 用于存储加载的图片
        self.current_image_index = 0  # 当前显示的图片索引

        self.is_transparent = False
        self.opacity = 0.7
        self.setWindowOpacity(self.opacity)

        self.previous_state = None

        self.scale_factor = 1.0  # 图片缩放因子

        self.is_transparent = False#启用穿透

    def set_images(self, image_paths):
        self.images = []  # 清空之前的图片列表
        for path in image_paths:
            pixmap = QtGui.QPixmap(path)
            self.images.append(pixmap)

        if self.images:
            self.current_image_index = 0
            self.scale_factor = 300 / max(pixmap.width(), pixmap.height())  # 计算缩放系数
            self.update_image()
            self.adjust_size_to_image()  # 调整窗口大小以适应图片

        self.show()

    def update_image(self):
        pixmap = self.images[self.current_image_index]
        scaled_pixmap = pixmap.scaled(
            pixmap.width() * self.scale_factor,
            pixmap.height() * self.scale_factor,
            QtCore.Qt.AspectRatioMode.KeepAspectRatio
        )
        self.image_label.setPixmap(scaled_pixmap)
        self.adjust_size_to_image()  # 调整窗口大小以适应图片

    def previous_image(self):
        if self.images:
            self.current_image_index -= 1
            if self.current_image_index < 0:
                self.current_image_index = len(self.images) - 1

            self.update_image()

    def next_image(self):
        if self.images:
            self.current_image_index += 1
            if self.current_image_index >= len(self.images):
                self.current_image_index = 0

            self.update_image()

    def wheelEvent(self, event):
        if not self.is_transparent:
            delta = event.angleDelta().y()
            if delta > 0:
                # 向上滚动，增加缩放因子
                self.scale_factor += 0.1
            else:
                # 向下滚动，减小缩放因子
                self.scale_factor -= 0.1
                if self.scale_factor < 0.1:
                    self.scale_factor = 0.1

            # 获取当前显示的图片
            pixmap = self.images[self.current_image_index]

            # 计算缩放后的尺寸
            scaled_size = QtCore.QSize(pixmap.width() * self.scale_factor, pixmap.height() * self.scale_factor)

            # 缩放图片并保持其比例不变
            scaled_pixmap = pixmap.scaled(scaled_size, QtCore.Qt.KeepAspectRatio)

            # 将缩放后的图片显示在界面上
            self.image_label.setPixmap(scaled_pixmap)
            self.adjust_size_to_image()  # 调整窗口大小以适应图片

    def mousePressEvent(self, e):
         if not self.is_transparent:
            self.start_point = e.globalPos()
            self.window_point = self.frameGeometry().topLeft()

            # 记录当前缩放因子和显示的图片
            self.previous_state = (self.scale_factor, self.current_image_index)

    def mouseMoveEvent(self, e):
         if not self.is_transparent:
            self.ismoving = True
            relpos = e.globalPos() - self.start_point
            self.move(self.window_point + relpos)

    def mouseDoubleClickEvent(self, event):
         if not self.is_transparent:
            # 双击窗口，将图片恢复到初始大小
            pixmap = self.images[self.current_image_index]
            self.scale_factor = 300 / max(pixmap.width(), pixmap.height())  # 计算缩放系数
            self.update_image()

            # 调整窗口大小以适应图片
            self.adjust_size_to_image()

    def adjust_size_to_image(self):
        if self.images:
            pixmap = self.images[self.current_image_index]
            scaled_pixmap = pixmap.scaled(
                pixmap.width() * self.scale_factor,
                pixmap.height() * self.scale_factor,
                QtCore.Qt.AspectRatioMode.KeepAspectRatio
            )

            self.image_label.setPixmap(scaled_pixmap)

            # 调整窗口大小以适应图片
            self.resize(scaled_pixmap.width(), scaled_pixmap.height())
            self.adjustSize()

    def keyPressEvent(self, event):
        modifiers = QtGui.QGuiApplication.keyboardModifiers()
        if event.key() == QtCore.Qt.Key_PageUp:
            self.previous_image()
        elif event.key() == QtCore.Qt.Key_PageDown:
            self.next_image()
        elif modifiers == QtCore.Qt.AltModifier:
            if event.key() == QtCore.Qt.Key_Apostrophe:  # Alt+'
                self.opacity += 0.1
                if self.opacity > 1.0:
                    self.opacity = 1.0
                self.setWindowOpacity(self.opacity)
            elif event.key() == QtCore.Qt.Key_Semicolon:  # Alt+;
                self.opacity -= 0.1
                if self.opacity < 0.1:
                    self.opacity = 0.1
                self.setWindowOpacity(self.opacity)
            elif event.key() == QtCore.Qt.Key_Slash:  # Alt+/
                self.parent().toggle_transparency(True)
            elif event.key() == QtCore.Qt.Key_Period:  # Alt+.
                self.parent().toggle_transparency(False)
            elif event.key() == QtCore.Qt.Key_BracketLeft:
                self.scale_factor -= 0.1
                if self.scale_factor < 0.1:
                    self.scale_factor = 0.1
                self.update_image()
                self.adjust_size_to_image()
            elif event.key() == QtCore.Qt.Key_BracketRight:
                self.scale_factor += 0.1
                self.update_image()
                self.adjust_size_to_image()

class ParentWindow(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.child_window = None
        self.child_window_position = QtCore.QPoint()
        self.child_window_size = QtCore.QSize()
        self.child_window_flags = QtCore.Qt.Tool

        load_btn = QtWidgets.QPushButton("加载图片")
        load_btn.clicked.connect(self.load_images)

        opacity_label = QtWidgets.QLabel("透明度:")
        self.opacity_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.opacity_slider.setMinimum(5)
        self.opacity_slider.setMaximum(100)
        self.opacity_slider.setSliderPosition(70)
        self.opacity_slider.setTickPosition(QtWidgets.QSlider.TicksBelow)
        self.opacity_slider.setTickInterval(10)
        self.opacity_slider.valueChanged.connect(self.update_opacity)

        self.transparent_btn = QtWidgets.QPushButton("穿透")
        self.transparent_btn.setCheckable(True)
        self.transparent_btn.toggled.connect(self.toggle_transparency)

        prev_btn = QtWidgets.QPushButton("上一张")
        prev_btn.clicked.connect(self.previous_image)

        next_btn = QtWidgets.QPushButton("下一张")
        next_btn.clicked.connect(self.next_image)

        button_layout = QtWidgets.QHBoxLayout()
        button_layout.addWidget(load_btn)
        button_layout.addWidget(self.transparent_btn)

        nav_button_layout = QtWidgets.QHBoxLayout()
        nav_button_layout.addWidget(prev_btn)
        nav_button_layout.addWidget(next_btn)

        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.addLayout(button_layout)

        opacity_layout = QtWidgets.QHBoxLayout()
        opacity_layout.addWidget(opacity_label)
        opacity_layout.addWidget(self.opacity_slider)
        main_layout.addLayout(opacity_layout)

        main_layout.addLayout(nav_button_layout)

        self.is_transparent = False
        self.opacity = 0.7

        self.instructions_btn = QtWidgets.QPushButton("说明")
        self.instructions_btn.clicked.connect(self.show_instructions)

        button_layout.addWidget(self.instructions_btn)

        self.installEventFilter(self)
   
    def show_instructions(self):
        instructions = """
        操作说明：
        - 此为帮助建模小伙伴做的参考图工具.
        - 如果你有更好的建议欢迎到B站@青苓君。
        - 使用滑块控制子窗口的透明度。
        - 按下穿透按钮后鼠标会穿透到底下的窗口便于建模。
        - 按下加载图片可以批量导入图片。
        - 快捷键：
        alt+;减少透明度(enter旁边)
        alt+'增加透明度(enter旁边)
        alt+PageUp上一张
        alt+PageDn下一张图片
        alt+鼠标右键启动穿透（关闭需要手动点击）
        鼠标双击恢复默认
        鼠标左键拖拽移动
        鼠标滚轮控制图片缩放
        """
        QtWidgets.QMessageBox.information(self, "操作说明", instructions)
        QtWidgets.QApplication.instance().installEventFilter(self)

    def eventFilter(self, obj, event):
        # Listen for Alt+/ key combination
        if event.type() == QtCore.QEvent.KeyPress:
            modifiers = QtWidgets.QApplication.keyboardModifiers()
            if modifiers == QtCore.Qt.AltModifier and event.key() == QtCore.Qt.Key_Slash:
                self.toggle_transparency(not self.is_transparent)
                return True
        return super().eventFilter(obj, event)

    def changeEvent(self, event):
        if event.type() == QtCore.QEvent.Type.WindowStateChange:
            if self.windowState() & QtCore.Qt.WindowState.Window:
                # Parent window is undocked, recreate the child window
                if self.child_window is not None:
                    self.child_window.close()

                self.child_window = ChildWindow(self)
                self.child_window.move(self.child_window_position)
                self.child_window.resize(self.child_window_size)
                self.child_window.setWindowFlags(self.child_window_flags)
                self.child_window.show()
            elif self.windowState() & QtCore.Qt.WindowState.DockWidget:
                # Parent window is docked, close the child window
                if self.child_window is not None:
                    self.child_window.close()
                self.child_window = None  # 清空子窗口引用

    def load_images(self):
        if self.child_window is not None:
            self.child_window.close()

        self.child_window = ChildWindow(self)
        self.child_window.move(self.pos())
        self.child_window_position = self.child_window.pos()
        self.child_window_size = self.child_window.size()

        file_dialog = QtWidgets.QFileDialog()
        file_dialog.setFileMode(QtWidgets.QFileDialog.ExistingFiles)
        file_dialog.setNameFilter("Images (*.png *.jpg *.bmp)")

        if file_dialog.exec_():
            selected_files = file_dialog.selectedFiles()
            image_paths = []
            for file_path in selected_files:
                if file_path.endswith(('.png', '.jpg', '.bmp')):
                    image_paths.append(file_path)
                else:
                    print(f"{file_path} 非支持格式图片会被忽略.")
            self.child_window.set_images(image_paths)


    def update_opacity(self):
        if self.child_window is not None:
            self.opacity = self.opacity_slider.value() / 100
            self.child_window.setWindowOpacity(self.opacity)

    def toggle_transparency(self, enabled):
        self.is_transparent = enabled
        self.transparent_btn.setChecked(enabled)
        if self.child_window is not None:
            if enabled:
                # 保存子窗口的位置
                self.child_window_position = self.child_window.pos()
                self.child_window_size = self.child_window.size()

                self.child_window.setWindowFlags(QtCore.Qt.Tool | QtCore.Qt.FramelessWindowHint | QtCore.Qt.WindowTransparentForInput | QtCore.Qt.WindowStaysOnTopHint)
                self.child_window.setAttribute(QtCore.Qt.WA_TransparentForMouseEvents, True)
                self.update_opacity()
            else:
                self.child_window.setWindowFlags(QtCore.Qt.Tool| QtCore.Qt.FramelessWindowHint)
                self.child_window.setAttribute(QtCore.Qt.WA_TransparentForMouseEvents, False)
                self.child_window.setWindowFlag(QtCore.Qt.WindowTransparentForInput, False)
                self.child_window.setWindowOpacity(self.opacity)  # 使用当前滑块的值作为透明度

                # 恢复子窗口的位置
                self.child_window.move(self.child_window_position)
                self.child_window.resize(self.child_window_size)

                self.child_window.setMouseTracking(False)
            self.child_window.show()



    def previous_image(self):
        if self.child_window is not None:
            self.child_window.previous_image()

    def next_image(self):
        if self.child_window is not None:
            self.child_window.next_image()


class ModelRefTool(QtWidgets.QDockWidget):
    def __init__(self, parent=None):
        super(ModelRefTool, self).__init__(parent)
        self.setWindowFlags(QtCore.Qt.Tool)
        self.setWindowTitle('参考图工具@B站青苓君V1.0')
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.setMaximumHeight(150)  # 设置窗口的最大高度为150


def main():
    main_window = qtmax.GetQMaxMainWindow()
    w = ModelRefTool(parent=main_window)
    w.setFloating(True)

    parent_window = ParentWindow(w)
    w.setWidget(parent_window)
    w.show()


if __name__ == '__main__':
    main()
