import tkinter as tk
import requests
import json
import threading
import time
from datetime import datetime, date


class GoldPriceWidget:
    def __init__(self):
        self.root = tk.Tk()
        self.setup_ui()
        self.is_running = True
        self.last_update_time = ""
        self.base_price = None  # 存储当日00:00:00的价格
        self.base_price_date = None  # 存储基准价格的日期
        self.last_alert_price = None  # 记录上一次提醒时的价格
        self.alert_threshold = 1.0  # 提醒阈值：1%
        self.current_alert_window = None  # 当前显示的提醒窗口

        # 启动价格更新线程
        self.update_thread = threading.Thread(target=self.periodic_price_update)
        self.update_thread.daemon = True
        self.update_thread.start()

    def setup_ui(self):
        # 设置主窗口无标题栏、置顶、透明背景
        self.root.overrideredirect(True)
        self.root.attributes('-topmost', True)
        self.root.configure(bg='black')
        # 增加窗口宽度以适应更多信息，高度也稍微增加
        self.root.geometry('220x110+100+100')

        # 显示金价的标签
        self.price_label = tk.Label(
            self.root,
            text="加载中...",
            fg='white',
            bg='black',
            font=('微软雅黑', 12, 'bold')
        )
        self.price_label.pack(expand=True, fill='both')

        # 显示价格变化的标签
        self.change_label = tk.Label(
            self.root,
            text="",
            fg='white',
            bg='black',
            font=('微软雅黑', 9)
        )
        self.change_label.pack(expand=True, fill='both')

        # 第一行信息标签 - 显示更新时间和基准价格
        self.info_label1 = tk.Label(
            self.root,
            text="",
            fg='lightgray',
            bg='black',
            font=('微软雅黑', 8)
        )
        self.info_label1.pack(expand=True, fill='both')

        # 第二行信息标签 - 显示上次提醒价格和操作提示
        self.info_label2 = tk.Label(
            self.root,
            text="",
            fg='lightgray',
            bg='black',
            font=('微软雅黑', 8)
        )
        self.info_label2.pack(expand=True, fill='both')

        # 绑定鼠标事件实现拖拽
        self.price_label.bind('<ButtonPress-1>', self.start_drag)
        self.price_label.bind('<B1-Motion>', self.on_drag)
        self.change_label.bind('<ButtonPress-1>', self.start_drag)
        self.change_label.bind('<B1-Motion>', self.on_drag)
        self.info_label1.bind('<ButtonPress-1>', self.start_drag)
        self.info_label1.bind('<B1-Motion>', self.on_drag)
        self.info_label2.bind('<ButtonPress-1>', self.start_drag)
        self.info_label2.bind('<B1-Motion>', self.on_drag)

        # 绑定双击事件切换主题
        self.price_label.bind('<Double-Button-1>', self.toggle_theme)
        self.change_label.bind('<Double-Button-1>', self.toggle_theme)
        self.info_label1.bind('<Double-Button-1>', self.toggle_theme)
        self.info_label2.bind('<Double-Button-1>', self.toggle_theme)

        # 绑定右键点击关闭程序
        self.price_label.bind('<Button-3>', self.close_app)
        self.change_label.bind('<Button-3>', self.close_app)
        self.info_label1.bind('<Button-3>', self.close_app)
        self.info_label2.bind('<Button-3>', self.close_app)

        # 添加右键菜单提示
        self.price_label.config(cursor="hand2")
        self.change_label.config(cursor="hand2")
        self.info_label1.config(cursor="hand2")
        self.info_label2.config(cursor="hand2")

        # 初始为深色主题
        self.is_dark = True

    def start_drag(self, event):
        self.start_x = event.x
        self.start_y = event.y

    def on_drag(self, event):
        x = self.root.winfo_x() + (event.x - self.start_x)
        y = self.root.winfo_y() + (event.y - self.start_y)
        self.root.geometry(f'+{x}+{y}')

    def toggle_theme(self, event):
        """双击切换浅色/深色主题"""
        if self.is_dark:
            self.root.configure(bg='white')
            self.price_label.configure(fg='black', bg='white')
            self.change_label.configure(fg='black', bg='white')
            self.info_label1.configure(fg='darkgray', bg='white')
            self.info_label2.configure(fg='darkgray', bg='white')
        else:
            self.root.configure(bg='black')
            self.price_label.configure(fg='white', bg='black')
            self.change_label.configure(fg='white', bg='black')
            self.info_label1.configure(fg='lightgray', bg='black')
            self.info_label2.configure(fg='lightgray', bg='black')
        self.is_dark = not self.is_dark

    def close_app(self, event):
        """右键点击关闭程序"""
        self.is_running = False
        # 关闭提醒窗口（如果存在）
        if self.current_alert_window:
            self.current_alert_window.destroy()
        self.root.quit()
        self.root.destroy()

    def fade_in(self, window, step=0.05):
        """淡入效果"""
        current_alpha = window.attributes('-alpha')
        new_alpha = min(current_alpha + step, 1.0)
        window.attributes('-alpha', new_alpha)

        if new_alpha < 1.0:
            window.after(30, lambda: self.fade_in(window, step))

    def fade_out(self, window, step=0.05):
        """淡出效果"""
        current_alpha = window.attributes('-alpha')
        new_alpha = max(current_alpha - step, 0.0)
        window.attributes('-alpha', new_alpha)

        if new_alpha > 0.0:
            window.after(30, lambda: self.fade_out(window, step))
        else:
            window.destroy()
            # 当窗口完全关闭后，重置当前提醒窗口引用
            if self.current_alert_window == window:
                self.current_alert_window = None

    def show_alert(self, change_percent):
        """显示价格变动提醒弹窗 - 点击关闭+自动更新"""
        # 如果已有提醒窗口，先关闭它
        if self.current_alert_window:
            self.current_alert_window.destroy()
            self.current_alert_window = None

        # 创建弹窗窗口
        alert_window = tk.Toplevel(self.root)
        alert_window.overrideredirect(True)  # 无边框
        alert_window.attributes('-topmost', True)  # 置顶

        # 初始设置为完全透明
        alert_window.attributes('-alpha', 0.0)

        # 使用主窗口的底色
        if self.is_dark:
            bg_color = 'black'
            text_color = 'white'  # 与底色相反
        else:
            bg_color = 'white'
            text_color = 'black'  # 与底色相反

        alert_window.configure(bg=bg_color, relief='solid', bd=1)

        # 设置窗口大小
        alert_window.geometry('180x80')  # 稍微增大以容纳更多信息

        # 计算屏幕中央位置
        screen_width = alert_window.winfo_screenwidth()
        screen_height = alert_window.winfo_screenheight()
        x = (screen_width - 180) // 2  # 窗口宽度180
        y = (screen_height - 80) // 2  # 窗口高度80
        alert_window.geometry(f'180x80+{x}+{y}')

        # 确定涨跌方向和颜色
        if change_percent > 0:
            direction = "金价上涨提醒"
            percent_color = "red"
        else:
            direction = "金价下跌提醒"
            percent_color = "green"

        # 创建第一行文本 - 提醒文字
        alert_label1 = tk.Label(
            alert_window,
            text=direction,
            fg=text_color,
            bg=bg_color,
            font=('微软雅黑', 10, 'bold'),
            justify='center'
        )
        alert_label1.pack(pady=(8, 0))

        # 创建第二行文本 - 百分比（更大字体）
        alert_label2 = tk.Label(
            alert_window,
            text=f"{change_percent:+.2f}%",
            fg=percent_color,
            bg=bg_color,
            font=('微软雅黑', 14, 'bold'),
            justify='center'
        )
        alert_label2.pack(pady=(2, 0))

        # 创建第三行文本 - 点击关闭提示
        alert_label3 = tk.Label(
            alert_window,
            text="点击此处关闭",
            fg='gray',
            bg=bg_color,
            font=('微软雅黑', 8),
            justify='center'
        )
        alert_label3.pack(pady=(5, 8))

        # 绑定点击事件关闭弹窗
        alert_label1.bind('<Button-1>', lambda e: self.fade_out(alert_window))
        alert_label2.bind('<Button-1>', lambda e: self.fade_out(alert_window))
        alert_label3.bind('<Button-1>', lambda e: self.fade_out(alert_window))
        alert_window.bind('<Button-1>', lambda e: self.fade_out(alert_window))

        # 设置鼠标指针为手型，提示可点击
        alert_label1.config(cursor="hand2")
        alert_label2.config(cursor="hand2")
        alert_label3.config(cursor="hand2")

        # 开始淡入效果
        self.fade_in(alert_window)

        # 保存当前提醒窗口引用
        self.current_alert_window = alert_window

    def fetch_gold_price(self):
        """
        从京东黄金API获取实时金价
        API: https://api.jdjygold.com/gw/generic/hj/h5/m/latestPrice
        返回JSON格式: data.resultData.datas.price
        """
        try:
            # 设置请求头，模拟浏览器请求
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Referer': 'https://jiage.jd.com/',
                'Accept': 'application/json, text/plain, */*'
            }

            # 发送GET请求获取金价数据
            response = requests.get(
                "https://api.jdjygold.com/gw/generic/hj/h5/m/latestPrice",
                headers=headers,
                timeout=5  # 设置超时时间为5秒
            )

            # 检查请求是否成功
            if response.status_code == 200:
                data = response.json()

                # 尝试多种可能的路径来解析金价数据
                price = None

                # 尝试第一种可能的路径
                try:
                    price = data['data']['resultData']['datas']['price']
                except KeyError:
                    pass

                # 如果第一种路径失败，尝试其他可能的路径
                if price is None:
                    try:
                        # 尝试直接访问data中的price字段
                        price = data['data']['price']
                    except KeyError:
                        pass

                # 如果仍然找不到价格，尝试遍历数据结构
                if price is None:
                    def find_price(obj, path=""):
                        if isinstance(obj, dict):
                            for key, value in obj.items():
                                if key == "price" and isinstance(value, (int, float, str)):
                                    return value
                                elif isinstance(value, (dict, list)):
                                    result = find_price(value, f"{path}.{key}")
                                    if result is not None:
                                        return result
                        elif isinstance(obj, list):
                            for i, item in enumerate(obj):
                                result = find_price(item, f"{path}[{i}]")
                                if result is not None:
                                    return result
                        return None

                    price = find_price(data)

                # 如果找到了价格，格式化并返回
                if price is not None:
                    # 获取当前时间
                    current_time = datetime.now().strftime("%H:%M:%S")
                    self.last_update_time = current_time

                    # 转换为浮点数
                    price_float = float(price)

                    # 检查是否需要更新基准价格（如果是新的一天或者还没有基准价格）
                    today = date.today()
                    if self.base_price is None or self.base_price_date != today:
                        self.base_price = price_float
                        self.base_price_date = today
                        self.last_alert_price = None  # 重置提醒价格

                    return price_float, f"{price} 元/克"
                else:
                    return None, "价格字段未找到"
            else:
                return None, f"API错误: {response.status_code}"

        except requests.exceptions.RequestException as e:
            return None, f"网络错误: {str(e)}"
        except json.JSONDecodeError as e:
            return None, f"JSON解析错误: {str(e)}"
        except Exception as e:
            return None, f"未知错误: {str(e)}"

    def update_price_display(self):
        """更新界面显示的价格和更新时间"""
        price_data, display_text = self.fetch_gold_price()

        if price_data is not None:
            # 更新价格显示
            self.price_label.config(text=display_text)

            # 计算相对于基准价格的变化（用于显示）
            change_vs_base = price_data - self.base_price
            change_percent_vs_base = (change_vs_base / self.base_price) * 100

            # 计算相对于上一次提醒价格的变化（用于触发提醒）
            if self.last_alert_price is not None:
                change_vs_last_alert = price_data - self.last_alert_price
                change_percent_vs_last_alert = (change_vs_last_alert / self.last_alert_price) * 100
            else:
                # 如果没有上一次提醒价格，使用基准价格作为参考
                change_vs_last_alert = change_vs_base
                change_percent_vs_last_alert = change_percent_vs_base

            # 检查是否需要触发提醒（基于上一次提醒价格的1%变动）
            if abs(change_percent_vs_last_alert) >= self.alert_threshold:
                # 触发弹窗提醒
                self.show_alert(change_percent_vs_last_alert)
                # 更新上一次提醒价格
                self.last_alert_price = price_data

            # 设置颜色和变化文本（仍然基于基准价格）
            if change_vs_base > 0:
                # 价格上涨，显示红色
                color = 'red'
                change_symbol = "↑"
            elif change_vs_base < 0:
                # 价格下跌，显示绿色
                color = 'green'
                change_symbol = "↓"
            else:
                # 价格不变，显示白色
                color = 'white'
                change_symbol = "→"

            # 更新颜色
            if self.is_dark:
                self.price_label.config(fg=color)
                self.change_label.config(fg=color)
            else:
                # 浅色主题下使用深色版本的颜色
                if color == 'red':
                    self.price_label.config(fg='darkred')
                    self.change_label.config(fg='darkred')
                elif color == 'green':
                    self.price_label.config(fg='darkgreen')
                    self.change_label.config(fg='darkgreen')
                else:
                    self.price_label.config(fg='black')
                    self.change_label.config(fg='black')

            # 更新变化标签（显示相对于基准价格的变化）
            change_text = f"基准: {self.base_price:.2f}  {change_symbol} {change_vs_base:+.2f} ({change_percent_vs_base:+.2f}%)"
            self.change_label.config(text=change_text)

            # 更新第一行信息标签 - 显示更新时间和基准价格
            info_text1 = f"更新: {self.last_update_time} | 基准: {self.base_price:.2f}"
            self.info_label1.config(text=info_text1)

            # 更新第二行信息标签 - 显示上次提醒价格和操作提示
            alert_info = f"上次提醒: {self.last_alert_price:.2f}" if self.last_alert_price is not None else "上次提醒: 无"
            info_text2 = f"{alert_info} | 右键关闭"
            self.info_label2.config(text=info_text2)
        else:
            # 显示错误信息
            self.price_label.config(text=display_text)
            self.change_label.config(text="")
            self.info_label1.config(text="")
            self.info_label2.config(text="")

    def periodic_price_update(self):
        """在后台线程中定期更新价格"""
        while self.is_running:
            self.update_price_display()
            # 更新频率：设置为5秒一次，避免过于频繁请求
            time.sleep(5)

    def run(self):
        """运行主程序"""
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            self.is_running = False
            self.root.quit()


if __name__ == "__main__":
    widget = GoldPriceWidget()
    widget.run()