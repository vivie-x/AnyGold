"""
UI 模块 - 负责界面显示和交互 (PySide6 版本)
"""

import sys
import ctypes
from typing import Callable, Optional

from PySide6.QtCore import Qt, QPoint, QPropertyAnimation, QEasingCurve, QTimer
from PySide6.QtGui import QFont, QColor, QPainter, QBrush
from PySide6.QtWidgets import (
    QApplication, QWidget, QLabel, QVBoxLayout, QGraphicsOpacityEffect
)

from .config import Config, ThemeConfig


class MainWindow(QWidget):
    """主窗口类"""

    def __init__(self, on_close: Callable, on_api_switch: Callable = None):
        """
        初始化主窗口

        Args:
            on_close: 关闭窗口时的回调函数
            on_api_switch: 切换API时的回调函数
        """
        # 确保 QApplication 存在
        self.app = QApplication.instance()
        if self.app is None:
            self.app = QApplication(sys.argv)

        # 防止关闭子窗口时退出应用
        self.app.setQuitOnLastWindowClosed(False)

        super().__init__()

        self.config = Config()
        self.on_close = on_close
        self.on_api_switch = on_api_switch
        self.theme_index = 0  # 0: dark, 1: light, 2: transparent
        self.themes = [ThemeConfig.DARK_THEME, ThemeConfig.LIGHT_THEME, ThemeConfig.TRANSPARENT_THEME]

        # 缩放比例
        self.scale_factor = 1.0
        self.scale_min = 0.3
        self.scale_max = 5.0

        # 基础字体大小
        self.base_font_price = 14
        self.base_font_change = 10
        self.base_font_info = 9

        # 伦敦金显示模式标记
        self.is_london_gold_mode = False

        # 拖拽相关
        self.drag_position: Optional[QPoint] = None

        # 背景透明度 (0-255)
        self.bg_alpha = 255

        # 置顶刷新定时器
        self.topmost_timer = QTimer()
        self.topmost_timer.timeout.connect(self._refresh_topmost)

        self._setup_window()
        self._setup_labels()
        self._apply_theme()

    def _setup_window(self):
        """设置主窗口属性"""
        # 无边框 + 置顶 + 工具窗口（不在任务栏显示）
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        # 启用透明背景
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self.setWindowTitle("金价监控")
        self.setGeometry(
            self.config.WINDOW_INITIAL_X,
            self.config.WINDOW_INITIAL_Y,
            self.config.WINDOW_WIDTH,
            self.config.WINDOW_HEIGHT
        )
        self.setMinimumSize(self.config.WINDOW_MIN_WIDTH, self.config.WINDOW_MIN_HEIGHT)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

    def _refresh_topmost(self):
        """刷新窗口置顶状态（使用 Windows API 强制置顶）"""
        try:
            if sys.platform == 'win32':
                # Windows API 常量
                HWND_TOPMOST = -1
                HWND_NOTOPMOST = -2
                SWP_NOMOVE = 0x0002
                SWP_NOSIZE = 0x0001
                SWP_NOACTIVATE = 0x0010
                SWP_SHOWWINDOW = 0x0040

                GWL_EXSTYLE = -20
                WS_EX_TOPMOST = 0x00000008
                WS_EX_TOOLWINDOW = 0x00000080

                # 获取窗口句柄
                hwnd = int(self.winId())

                # 方法1：先取消置顶，再重新设置（刷新 Z-Order）
                ctypes.windll.user32.SetWindowPos(
                    hwnd,
                    HWND_NOTOPMOST,
                    0, 0, 0, 0,
                    SWP_NOMOVE | SWP_NOSIZE | SWP_NOACTIVATE
                )

                # 方法2：设置扩展窗口样式
                ex_style = ctypes.windll.user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
                ex_style |= WS_EX_TOPMOST | WS_EX_TOOLWINDOW
                ctypes.windll.user32.SetWindowLongW(hwnd, GWL_EXSTYLE, ex_style)

                # 方法3：重新设置为置顶
                ctypes.windll.user32.SetWindowPos(
                    hwnd,
                    HWND_TOPMOST,
                    0, 0, 0, 0,
                    SWP_NOMOVE | SWP_NOSIZE | SWP_NOACTIVATE | SWP_SHOWWINDOW
                )

                # 方法4：强制提升到最前（不改变焦点）
                ctypes.windll.user32.BringWindowToTop(hwnd)

        except Exception as e:
            pass  # 静默失败

    def _setup_labels(self):
        """设置显示标签"""
        layout = QVBoxLayout()
        layout.setContentsMargins(8, 5, 8, 5)
        layout.setSpacing(2)

        # 价格标签
        self.price_label = QLabel("加载中...")
        self.price_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.price_label)

        # 变化标签
        self.change_label = QLabel("")
        self.change_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.change_label)

        # 信息标签1
        self.info_label1 = QLabel("")
        self.info_label1.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.info_label1)

        # 信息标签2
        self.info_label2 = QLabel("")
        self.info_label2.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.info_label2)

        self.setLayout(layout)
        self._update_fonts()

    def _get_all_labels(self):
        """获取所有标签"""
        return [self.price_label, self.change_label, self.info_label1, self.info_label2]

    def paintEvent(self, event):
        """绘制背景（支持透明度）"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # 获取当前背景色
        theme = self.themes[self.theme_index]
        if theme['bg'] == 'black':
            bg_color = QColor(0, 0, 0, self.bg_alpha)
        elif theme['bg'] == 'white':
            bg_color = QColor(255, 255, 255, self.bg_alpha)
        else:
            bg_color = QColor(0, 0, 0, self.bg_alpha)

        painter.setBrush(QBrush(bg_color))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(self.rect(), 5, 5)

    def _apply_theme(self):
        """应用主题"""
        theme = self.themes[self.theme_index]

        # 设置背景透明度
        if self.theme_index == 2:  # 透明主题
            self.bg_alpha = 1  # 约 15% 不透明，更透明
        else:
            self.bg_alpha = 255  # 完全不透明

        # 设置文字颜色
        self.price_label.setStyleSheet(f"color: {theme['fg']}; background: transparent;")
        self.change_label.setStyleSheet(f"color: {theme['fg']}; background: transparent;")
        self.info_label1.setStyleSheet(f"color: {theme['info_fg']}; background: transparent;")
        self.info_label2.setStyleSheet(f"color: {theme['info_fg']}; background: transparent;")

        self.update()  # 触发重绘

    def _update_fonts(self):
        """更新字体大小"""
        # 如果是伦敦金模式，使用统一的小字体
        if self.is_london_gold_mode:
            font_size = max(int(self.base_font_info * self.scale_factor), 8)
            font = QFont("微软雅黑", font_size)
            self.price_label.setFont(font)
            self.change_label.setFont(font)
            self.info_label1.setFont(font)
            self.info_label2.setFont(font)
        else:
            # 正常模式：使用不同大小的字体
            font_size_price = max(int(self.base_font_price * self.scale_factor), 6)
            font_size_change = max(int(self.base_font_change * self.scale_factor), 4)
            font_size_info = max(int(self.base_font_info * self.scale_factor), 3)

            font_price = QFont("微软雅黑", font_size_price)
            font_price.setBold(True)
            self.price_label.setFont(font_price)

            self.change_label.setFont(QFont("微软雅黑", font_size_change))
            self.info_label1.setFont(QFont("微软雅黑", font_size_info))
            self.info_label2.setFont(QFont("微软雅黑", font_size_info))

    def set_uniform_small_font(self):
        """设置所有标签为统一的小字体（用于伦敦金详细信息显示）"""
        self.is_london_gold_mode = True
        font_size = max(int(self.base_font_info * self.scale_factor), 8)
        small_font = QFont("微软雅黑", font_size)

        self.price_label.setFont(small_font)
        self.change_label.setFont(small_font)
        self.info_label1.setFont(small_font)
        self.info_label2.setFont(small_font)

    def restore_normal_fonts(self):
        """恢复正常的字体大小（切换回其他数据源时使用）"""
        self.is_london_gold_mode = False
        self._update_fonts()

    def mousePressEvent(self, event):
        """鼠标按下事件"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()
        elif event.button() == Qt.MouseButton.RightButton:
            self.on_close()
            event.accept()
        elif event.button() == Qt.MouseButton.MiddleButton:
            # 鼠标中键点击切换API
            if self.on_api_switch:
                self.on_api_switch()
            event.accept()

    def mouseMoveEvent(self, event):
        """鼠标移动事件（拖拽）"""
        if event.buttons() == Qt.MouseButton.LeftButton and self.drag_position:
            self.move(event.globalPosition().toPoint() - self.drag_position)
            event.accept()

    def mouseDoubleClickEvent(self, event):
        """双击切换主题"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.theme_index = (self.theme_index + 1) % len(self.themes)
            self._apply_theme()
            event.accept()

    def wheelEvent(self, event):
        """滚轮事件处理"""
        modifiers = event.modifiers()
        delta = event.angleDelta().y()

        if modifiers & Qt.KeyboardModifier.ControlModifier:
            # Ctrl + 滚轮：切换API
            if self.on_api_switch:
                self.on_api_switch()
        else:
            # 普通滚轮：调整窗口大小（保持原有功能）
            scale_step = 0.05

            if delta > 0:
                self.scale_factor = min(self.scale_factor + scale_step, self.scale_max)
            else:
                self.scale_factor = max(self.scale_factor - scale_step, self.scale_min)

            # 计算新尺寸
            new_width = int(self.config.WINDOW_WIDTH * self.scale_factor)
            new_height = int(self.config.WINDOW_HEIGHT * self.scale_factor)
            new_width = max(new_width, self.config.WINDOW_MIN_WIDTH)
            new_height = max(new_height, self.config.WINDOW_MIN_HEIGHT)

            self.resize(new_width, new_height)
            self._update_fonts()
            self._update_label_visibility()

        event.accept()

    def focusOutEvent(self, event):
        """窗口失去焦点时立即刷新置顶（关键优化）"""
        super().focusOutEvent(event)
        # 当用户点击其他窗口或任务栏时，立即刷新置顶
        self._refresh_topmost()

    def changeEvent(self, event):
        """窗口状态改变时刷新置顶"""
        super().changeEvent(event)
        # 窗口状态改变时也刷新置顶
        if event.type() == event.Type.ActivationChange:
            self._refresh_topmost()

    def _update_label_visibility(self):
        """根据缩放比例更新标签可见性"""
        if self.scale_factor < 0.45:
            # 非常小：只显示价格
            self.change_label.hide()
            self.info_label1.hide()
            self.info_label2.hide()
        elif self.scale_factor < 0.6:
            # 较小：显示价格和变化
            self.change_label.show()
            self.info_label1.hide()
            self.info_label2.hide()
        else:
            # 正常：显示全部
            self.change_label.show()
            self.info_label1.show()
            self.info_label2.show()

    def update_display(self, price_text: str, change_text: str,
                       info_text1: str, info_text2: str,
                       price_color: str):
        """更新显示内容"""
        self.price_label.setText(price_text)
        self.change_label.setText(change_text)
        self.info_label1.setText(info_text1)
        self.info_label2.setText(info_text2)

        # 设置价格颜色
        theme = self.themes[self.theme_index]
        if price_color == 'up':
            color = theme['up_color']
        elif price_color == 'down':
            color = theme['down_color']
        else:
            color = theme['neutral_color']

        self.price_label.setStyleSheet(f"color: {color}; background: transparent;")
        self.change_label.setStyleSheet(f"color: {color}; background: transparent;")

    def show_error(self, error_text: str):
        """显示错误信息"""
        self.price_label.setText(error_text)
        self.change_label.setText("")
        self.info_label1.setText("")
        self.info_label2.setText("")

    def run(self):
        """运行主循环"""
        self.show()
        # 立即刷新一次置顶
        self._refresh_topmost()
        # 启动定时器，定期刷新置顶状态
        self.topmost_timer.start(self.config.TOPMOST_REFRESH_INTERVAL)
        self.app.exec()

    def quit(self):
        """退出应用"""
        self.topmost_timer.stop()
        self.close()
        self.app.quit()


class AlertWindow(QWidget):
    """提醒弹窗类"""

    def __init__(self, parent: QWidget, change_percent: float, theme_index: int, api_name: str = ""):
        """
        初始化提醒弹窗

        Args:
            parent: 父窗口
            change_percent: 变化百分比
            theme_index: 主题索引 (0=深色, 1=浅色, 2=透明)
            api_name: API名称
        """
        super().__init__()
        self.config = Config()
        self.theme_index = theme_index
        self.change_percent = change_percent
        self.api_name = api_name

        self._setup_window()
        self._setup_content()
        self._fade_in()

    def _setup_window(self):
        """设置窗口属性"""
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool |
            Qt.WindowType.WindowDoesNotAcceptFocus  # 不夺取焦点，避免影响主窗口
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)  # 显示时不激活
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)  # 关闭时删除窗口对象

        # 居中显示
        screen = QApplication.primaryScreen().geometry()
        x = (screen.width() - self.config.ALERT_WINDOW_WIDTH) // 2
        y = (screen.height() - self.config.ALERT_WINDOW_HEIGHT) // 2
        self.setGeometry(x, y, self.config.ALERT_WINDOW_WIDTH, self.config.ALERT_WINDOW_HEIGHT)

        self.setCursor(Qt.CursorShape.PointingHandCursor)

        # 透明度效果
        self.opacity_effect = QGraphicsOpacityEffect()
        self.opacity_effect.setOpacity(0.0)
        self.setGraphicsEffect(self.opacity_effect)

    def _setup_content(self):
        """设置内容"""
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 8, 10, 8)
        layout.setSpacing(2)

        # 根据主题配置颜色
        if self.theme_index == 0:  # 深色主题
            text_color = 'white'
        elif self.theme_index == 1:  # 浅色主题
            text_color = 'black'
        else:  # 透明主题
            text_color = 'white'

        if self.change_percent > 0:
            direction = "金价上涨提醒"
            percent_color = "red"
        else:
            direction = "金价下跌提醒"
            percent_color = "green"

        # 如果有API名称，添加到标题中
        if self.api_name:
            direction = f"{direction} - {self.api_name}"

        # 标题
        title_label = QLabel(direction)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet(f"color: {text_color}; background: transparent;")
        title_font = QFont("微软雅黑", 9)
        title_font.setBold(True)
        title_label.setFont(title_font)
        layout.addWidget(title_label)

        # 百分比
        percent_label = QLabel(f"{self.change_percent:+.2f}%")
        percent_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        percent_label.setStyleSheet(f"color: {percent_color}; background: transparent;")
        percent_font = QFont("微软雅黑", 14)
        percent_font.setBold(True)
        percent_label.setFont(percent_font)
        layout.addWidget(percent_label)

        # 提示
        hint_label = QLabel("点击关闭")
        hint_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        hint_label.setStyleSheet("color: gray; background: transparent;")
        hint_label.setFont(QFont("微软雅黑", 8))
        layout.addWidget(hint_label)

        self.setLayout(layout)

    def paintEvent(self, event):
        """绘制背景"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # 根据主题设置背景颜色
        if self.theme_index == 0:  # 深色主题
            bg_color = QColor(30, 30, 30, 240)
            border_color = QColor(100, 100, 100)
        elif self.theme_index == 1:  # 浅色主题
            bg_color = QColor(250, 250, 250, 240)
            border_color = QColor(100, 100, 100)
        else:  # 透明主题
            bg_color = QColor(0, 0, 0, 1)  # 几乎完全透明的黑色
            border_color = QColor(255, 255, 255, 100)  # 半透明白色边框

        painter.setBrush(QBrush(bg_color))
        painter.setPen(border_color)
        painter.drawRoundedRect(self.rect(), 8, 8)

    def _fade_in(self):
        """淡入效果"""
        self.show()
        self.animation = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.animation.setDuration(300)
        self.animation.setStartValue(0.0)
        self.animation.setEndValue(1.0)
        self.animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        self.animation.start()

    def _fade_out(self):
        """淡出效果"""
        self.animation = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.animation.setDuration(200)
        self.animation.setStartValue(1.0)
        self.animation.setEndValue(0.0)
        self.animation.setEasingCurve(QEasingCurve.Type.InCubic)
        self.animation.finished.connect(self.close)
        self.animation.start()

    def mousePressEvent(self, event):
        """点击关闭"""
        self._fade_out()
        event.accept()

    def close_window(self):
        """关闭窗口"""
        self.close()

