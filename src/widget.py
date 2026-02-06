"""
Widget 模块 - 黄金价格小工具核心逻辑 (PySide6 版本)
"""

from datetime import date
from typing import Optional

import shiboken6
from PySide6.QtCore import QTimer

from .config import Config
from .api import GoldPriceAPI, LondonGoldWebSocket
from .ui import MainWindow, AlertWindow


class GoldPriceWidget:
    """黄金价格监控小工具"""

    def __init__(self):
        self.config = Config()
        self.api = GoldPriceAPI()

        # 初始化伦敦金 WebSocket 客户端
        self.london_gold_ws = LondonGoldWebSocket()
        self.london_gold_ws.start()

        # 状态变量
        self.is_running = True
        self.last_update_time = ""

        # 为每个API维护独立的状态
        # 结构：{api_index: {'base_price': float, 'base_price_date': date, 'last_alert_price': float}}
        self.api_states = {}
        # 为前两个 HTTP API 和伦敦金（索引2）初始化状态
        for i in range(len(self.config.API_URLS) + 1):  # +1 包含伦敦金
            self.api_states[i] = {
                'base_price': None,
                'base_price_date': None,
                'last_alert_price': None
            }

        # 缓存所有API的最新价格数据
        self.cached_prices = {}

        self.current_alert_window: Optional[AlertWindow] = None

        # 创建 UI
        self.main_window = MainWindow(on_close=self._on_close, on_api_switch=self._on_api_switch)

        # 使用 QTimer 代替线程进行定时更新
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self._update_price_display)
        self.update_timer.start(self.config.UPDATE_INTERVAL * 1000)  # 转换为毫秒

        # 立即执行一次更新
        self._update_price_display()

    def _on_close(self):
        """关闭回调"""
        self.is_running = False
        self.update_timer.stop()
        # 停止 WebSocket 连接
        if hasattr(self, 'london_gold_ws'):
            self.london_gold_ws.stop()
        if self.current_alert_window:
            try:
                if shiboken6.isValid(self.current_alert_window):
                    self.current_alert_window.close_window()
            except (RuntimeError, AttributeError):
                pass
        self.main_window.quit()

    def _on_api_switch(self):
        """API切换回调"""
        api_name = self.api.switch_api()
        # 立即使用缓存数据更新显示，不等待网络请求
        self._update_display_from_cache()
        # 异步触发后台更新
        # (下次定时器触发时会自动更新)

    def _show_alert(self, change_percent: float, api_name: str):
        """显示价格变动提醒"""
        # 关闭已有的提醒窗口
        if self.current_alert_window:
            try:
                # 检查 C++ 对象是否还有效
                if shiboken6.isValid(self.current_alert_window):
                    self.current_alert_window.close_window()
            except (RuntimeError, AttributeError):
                pass  # 对象已被删除，忽略错误
            finally:
                self.current_alert_window = None

        # 创建新的提醒窗口
        self.current_alert_window = AlertWindow(
            self.main_window,
            change_percent,
            self.main_window.theme_index,  # 传递主题索引
            api_name  # 传递 API 名称
        )

    def _update_display_from_cache(self):
        """从缓存数据更新显示（用于快速切换API）"""
        if not self.cached_prices:
            # 如果没有缓存，显示加载中
            self.main_window.show_error("正在加载数据...")
            return

        current_api_index = self.api.current_api_index
        if current_api_index not in self.cached_prices:
            self.main_window.show_error("数据未就绪...")
            return

        price_data, display_text, update_time, api_name = self.cached_prices[current_api_index]

        if price_data is not None:
            self.last_update_time = update_time
            state = self.api_states[current_api_index]

            # 如果该API还没有基准价格，先设置
            if state['base_price'] is None:
                state['base_price'] = price_data
                state['base_price_date'] = date.today()

            # 计算当前API的变化（用于显示）
            change_vs_base = price_data - state['base_price']
            change_percent_vs_base = (change_vs_base / state['base_price']) * 100

            # 确定颜色和符号
            if change_vs_base > 0:
                price_color = 'up'
                change_symbol = "↑"
            elif change_vs_base < 0:
                price_color = 'down'
                change_symbol = "↓"
            else:
                price_color = 'neutral'
                change_symbol = "→"

            # 生成显示文本
            change_text = f"基准: {state['base_price']:.2f}  {change_symbol} {change_vs_base:+.2f} ({change_percent_vs_base:+.2f}%)"

            # 如果是伦敦金（索引2），使用4行显示详细信息
            if current_api_index == 2:
                line1, line2, line3, line4 = self.london_gold_ws.get_detailed_info(
                    state['base_price'], state['last_alert_price'],
                    self.last_update_time, change_vs_base,
                    change_percent_vs_base, change_symbol
                )
                # 使用所有4个标签显示伦敦金信息
                self.main_window.update_display(
                    line1, line2, line3, line4, price_color
                )
            else:
                info_text1 = f"更新: {self.last_update_time} | API: {api_name}"
                alert_info = f"上次提醒: {state['last_alert_price']:.2f}" if state['last_alert_price'] else "上次提醒: 无"
                info_text2 = f"{alert_info} | 滚轮切换API | 右键关闭"
                # 更新显示
                self.main_window.update_display(
                    display_text, change_text, info_text1, info_text2, price_color
                )
        else:
            self.main_window.show_error(display_text)

    def _update_price_display(self):
        """更新价格显示，仅监控当前选中的API"""
        # 获取所有API的价格数据（并行请求，速度快）
        all_prices = self.api.fetch_all_prices()

        # 获取伦敦金价格（索引2）
        london_price_data, london_display_text, london_update_time = self.london_gold_ws.get_latest_price()
        all_prices[2] = (london_price_data, london_display_text, london_update_time, "伦敦金")

        # 更新缓存
        self.cached_prices = all_prices

        today = date.today()

        # 遍历所有API，更新基准价格（但不检查提醒）
        for api_index, (price_data, display_text, update_time, api_name) in all_prices.items():
            if price_data is None:
                continue

            state = self.api_states[api_index]

            # 检查是否需要更新基准价格
            if state['base_price'] is None or state['base_price_date'] != today:
                state['base_price'] = price_data
                state['base_price_date'] = today
                state['last_alert_price'] = None

        # 只对当前选中的API检查提醒和显示数据
        current_api_index = self.api.current_api_index
        if current_api_index in all_prices:
            price_data, display_text, update_time, api_name = all_prices[current_api_index]

            if price_data is not None:
                self.last_update_time = update_time
                state = self.api_states[current_api_index]

                # 计算当前API的变化
                change_vs_base = price_data - state['base_price']
                change_percent_vs_base = (change_vs_base / state['base_price']) * 100

                # 检查是否需要触发提醒（仅针对当前选中的API）
                if state['last_alert_price'] is not None:
                    change_vs_last_alert = price_data - state['last_alert_price']
                    change_percent_vs_last_alert = (change_vs_last_alert / state['last_alert_price']) * 100
                else:
                    change_percent_vs_last_alert = change_percent_vs_base

                if abs(change_percent_vs_last_alert) >= self.config.ALERT_THRESHOLD:
                    self._show_alert(change_percent_vs_last_alert, api_name)
                    state['last_alert_price'] = price_data


                # 确定颜色和符号
                if change_vs_base > 0:
                    price_color = 'up'
                    change_symbol = "↑"
                elif change_vs_base < 0:
                    price_color = 'down'
                    change_symbol = "↓"
                else:
                    price_color = 'neutral'
                    change_symbol = "→"

                # 生成显示文本
                change_text = f"基准: {state['base_price']:.2f}  {change_symbol} {change_vs_base:+.2f} ({change_percent_vs_base:+.2f}%)"

                # 如果是伦敦金（索引2），使用4行显示详细信息
                if current_api_index == 2:
                    line1, line2, line3, line4 = self.london_gold_ws.get_detailed_info(
                        state['base_price'], state['last_alert_price'],
                        self.last_update_time, change_vs_base,
                        change_percent_vs_base, change_symbol
                    )
                    # 使用所有4个标签显示伦敦金信息
                    self.main_window.update_display(
                        line1, line2, line3, line4, price_color
                    )
                else:
                    info_text1 = f"更新: {self.last_update_time} | API: {api_name}"
                    alert_info = f"上次提醒: {state['last_alert_price']:.2f}" if state['last_alert_price'] else "上次提醒: 无"
                    info_text2 = f"{alert_info} | 滚轮切换API | 右键关闭"
                    # 更新显示
                    self.main_window.update_display(
                        display_text, change_text, info_text1, info_text2, price_color
                    )
            else:
                self.main_window.show_error(display_text)

    def run(self):
        """运行应用"""
        try:
            self.main_window.run()
        except KeyboardInterrupt:
            self.is_running = False
            self.main_window.quit()

