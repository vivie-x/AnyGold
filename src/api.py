"""
API 模块 - 负责获取黄金价格数据
"""

import requests
import json
import time
import threading
import re
from datetime import datetime
from typing import Tuple, Optional, Any
from concurrent.futures import ThreadPoolExecutor, as_completed
from websocket import WebSocketApp
from bs4 import BeautifulSoup

from .config import Config


class GoldPriceAPI:
    """黄金价格 API 客户端"""

    def __init__(self):
        self.config = Config()
        self.current_api_index = self.config.CURRENT_API_INDEX

    def switch_api(self):
        """切换到下一个API"""
        self.current_api_index = (self.current_api_index + 1) % len(self.config.API_NAMES)
        return self.get_current_api_name()

    def get_current_api_name(self) -> str:
        """获取当前API的名称"""
        return self.config.API_NAMES[self.current_api_index]

    def get_current_api_url(self) -> str:
        """获取当前API的URL"""
        return self.config.API_URLS[self.current_api_index]

    def fetch_price(self) -> Tuple[Optional[float], str, str]:
        """
        从当前选中的API获取实时金价

        Returns:
            Tuple[Optional[float], str, str]: (价格浮点数, 显示文本, 更新时间)
            如果获取失败，价格为 None
        """
        return self._fetch_price_from_api(self.current_api_index)

    def fetch_all_prices(self) -> dict:
        """
        从所有API并行获取实时金价（使用线程池）

        Returns:
            dict: {api_index: (价格浮点数, 显示文本, 更新时间, API名称)}
        """
        results = {}

        # 使用线程池并行请求所有API
        with ThreadPoolExecutor(max_workers=len(self.config.API_URLS)) as executor:
            # 提交所有任务
            future_to_index = {
                executor.submit(self._fetch_price_from_api, i): i
                for i in range(len(self.config.API_URLS))
            }

            # 收集结果
            for future in as_completed(future_to_index):
                api_index = future_to_index[future]
                try:
                    price, display, update_time = future.result()
                    results[api_index] = (price, display, update_time, self.config.API_NAMES[api_index])
                except Exception as e:
                    # 如果某个API失败，返回错误信息
                    results[api_index] = (None, f"请求失败: {str(e)}", "", self.config.API_NAMES[api_index])

        return results

    def _fetch_price_from_api(self, api_index: int) -> Tuple[Optional[float], str, str]:
        """
        从指定的API获取实时金价

        Args:
            api_index: API索引

        Returns:
            Tuple[Optional[float], str, str]: (价格浮点数, 显示文本, 更新时间)
        """
        try:
            response = requests.get(
                self.config.API_URLS[api_index],
                headers=self.config.HEADERS,
                timeout=self.config.API_TIMEOUT
            )

            if response.status_code == 200:
                data = response.json()
                price = self._extract_price(data)

                if price is not None:
                    current_time = datetime.now().strftime("%H:%M:%S")
                    price_float = float(price)
                    return price_float, f"{price} 元/克", current_time
                else:
                    return None, "价格字段未找到", ""
            else:
                return None, f"API错误: {response.status_code}", ""

        except requests.exceptions.RequestException as e:
            return None, f"网络错误: {str(e)}", ""
        except json.JSONDecodeError as e:
            return None, f"JSON解析错误: {str(e)}", ""
        except Exception as e:
            return None, f"未知错误: {str(e)}", ""

    def _extract_price(self, data: dict) -> Optional[Any]:
        """
        从 API 响应数据中提取价格

        Args:
            data: API 响应的 JSON 数据

        Returns:
            价格值，如果未找到则返回 None
        """
        # 尝试第一种可能的路径
        try:
            return data['data']['resultData']['datas']['price']
        except (KeyError, TypeError):
            pass

        # 尝试第二种可能的路径
        try:
            return data['data']['price']
        except (KeyError, TypeError):
            pass

        # 遍历数据结构查找价格
        return self._find_price_recursive(data)

    def _find_price_recursive(self, obj: Any, path: str = "") -> Optional[Any]:
        """
        递归查找价格字段

        Args:
            obj: 要搜索的对象
            path: 当前路径（用于调试）

        Returns:
            找到的价格值，否则返回 None
        """
        if isinstance(obj, dict):
            for key, value in obj.items():
                if key == "price" and isinstance(value, (int, float, str)):
                    return value
                elif isinstance(value, (dict, list)):
                    result = self._find_price_recursive(value, f"{path}.{key}")
                    if result is not None:
                        return result
        elif isinstance(obj, list):
            for i, item in enumerate(obj):
                result = self._find_price_recursive(item, f"{path}[{i}]")
                if result is not None:
                    return result
        return None


class ExchangeRateAPI:
    """汇率 API 客户端 - 获取美元兑人民币汇率"""

    def __init__(self):
        self.config = Config()
        self.cached_rate = None
        self.cache_time = 0

    def get_usd_to_cny(self) -> float:
        """
        获取美元兑人民币汇率，优先使用缓存

        Returns:
            float: 美元兑人民币汇率
        """
        # 检查缓存是否有效
        if self._is_cache_valid():
            return self.cached_rate

        # 尝试从主 API 获取
        rate = self._fetch_from_primary_api()
        if rate is not None:
            self.cached_rate = rate
            self.cache_time = time.time()
            return rate

        # 主 API 失败，尝试中国银行
        rate = self._fetch_from_boc()
        if rate is not None:
            self.cached_rate = rate
            self.cache_time = time.time()
            return rate

        # 都失败，返回默认汇率
        return self.config.DEFAULT_EXCHANGE_RATE

    def _is_cache_valid(self) -> bool:
        """检查缓存是否有效"""
        if self.cached_rate is None:
            return False
        return (time.time() - self.cache_time) < self.config.EXCHANGE_RATE_CACHE_TIME

    def _fetch_from_primary_api(self) -> Optional[float]:
        """从主汇率 API 获取汇率"""
        try:
            response = requests.get(
                self.config.EXCHANGE_RATE_APIS[0],
                timeout=5
            )
            if response.status_code == 200:
                data = response.json()
                # exchangerate-api.com 的响应格式
                if 'rates' in data and 'CNY' in data['rates']:
                    return float(data['rates']['CNY'])
        except Exception as e:
            print(f"主汇率API获取失败: {e}")
        return None

    def _fetch_from_boc(self) -> Optional[float]:
        """从中国银行官网获取汇率"""
        try:
            response = requests.get(
                self.config.EXCHANGE_RATE_APIS[1],
                headers=self.config.HEADERS,
                timeout=10
            )
            if response.status_code == 200:
                response.encoding = 'utf-8'
                soup = BeautifulSoup(response.text, 'html.parser')

                # 查找包含美元汇率的表格行
                # 中国银行的页面结构：找到包含"美元"的行
                rows = soup.find_all('tr')
                for row in rows:
                    cells = row.find_all('td')
                    if len(cells) > 0:
                        # 第一列通常是货币名称
                        if '美元' in cells[0].get_text():
                            # 现汇买入价通常在第3或第4列
                            # 我们使用现汇买入价（适合价格转换）
                            if len(cells) >= 4:
                                rate_text = cells[3].get_text().strip()
                                # 移除可能的空格和换行
                                rate_text = re.sub(r'\s+', '', rate_text)
                                try:
                                    rate = float(rate_text)
                                    if rate > 0:
                                        return rate
                                except ValueError:
                                    pass
        except Exception as e:
            print(f"中国银行汇率获取失败: {e}")
        return None


class LondonGoldWebSocket:
    """伦敦金 WebSocket 客户端 - 获取实时金价"""

    def __init__(self):
        self.config = Config()
        self.exchange_rate_api = ExchangeRateAPI()
        self.ws = None
        self.latest_data = None  # 存储最新的价格数据: {'bid': float, 'ask': float, 'time': str}
        self.is_connected = False
        self.reconnect_count = 0
        self.lock = threading.Lock()
        self.thread = None
        self.should_stop = False

    def start(self):
        """启动 WebSocket 连接（在后台线程）"""
        if self.thread is None or not self.thread.is_alive():
            self.should_stop = False
            self.thread = threading.Thread(target=self._run, daemon=True)
            self.thread.start()

    def _run(self):
        """WebSocket 运行循环"""
        while not self.should_stop:
            try:
                ws_url = self._fetch_ws_url()
                self._connect(ws_url)
            except Exception as e:
                print(f"WebSocket 连接异常: {e}")

            # 如果需要停止或达到最大重连次数，退出
            if self.should_stop or self.reconnect_count >= self.config.MAX_WS_RECONNECT_ATTEMPTS:
                break

            # 等待后重连
            time.sleep(self.config.WS_RECONNECT_INTERVAL)
            self.reconnect_count += 1

    def _fetch_ws_url(self) -> str:
        """获取 WebSocket 地址，失败时返回备用地址"""
        try:
            response = requests.get(
                self.config.WS_DOMAIN_API,
                headers=self.config.HEADERS,
                timeout=5
            )
            if response.status_code == 200:
                data = response.json()
                if data.get('code') == 0 and 'data' in data and 'hq_ws_links' in data['data']:
                    ws_links = data['data']['hq_ws_links']
                    # 获取第一个 WebSocket 地址
                    first_key = list(ws_links.keys())[0] if ws_links else None
                    if first_key and ws_links[first_key]:
                        print(f"获取到动态 WebSocket 地址: {ws_links[first_key]}")
                        return ws_links[first_key]
        except Exception as e:
            print(f"动态获取 WebSocket 地址失败: {e}")

        # 使用备用地址
        print(f"使用备用 WebSocket 地址: {self.config.WS_BACKUP_URL}")
        return self.config.WS_BACKUP_URL

    def _connect(self, ws_url: str):
        """建立 WebSocket 连接"""
        self.ws = WebSocketApp(
            ws_url,
            on_message=self._on_message,
            on_error=self._on_error,
            on_close=self._on_close,
            on_open=self._on_open
        )
        self.ws.run_forever()

    def _on_open(self, ws):
        """连接建立回调"""
        print("WebSocket 已连接")
        self.is_connected = True
        self.reconnect_count = 0

    def _on_message(self, ws, message):
        """接收消息回调"""
        try:
            data = json.loads(message)
            # 数据格式: [{"symbol": "GOLD", "bid": 2850.5, "ask": 2851.5, ...}, ...]
            if isinstance(data, list):
                for item in data:
                    if item.get('symbol') == 'GOLD':
                        bid = float(item.get('bid', 0))
                        ask = float(item.get('ask', 0))

                        with self.lock:
                            self.latest_data = {
                                'bid': bid,
                                'ask': ask,
                                'time': datetime.now().strftime("%H:%M:%S")
                            }
                        break
        except Exception as e:
            print(f"解析 WebSocket 消息失败: {e}")

    def _on_error(self, ws, error):
        """错误回调"""
        print(f"WebSocket 错误: {error}")
        self.is_connected = False

    def _on_close(self, ws, close_status_code, close_msg):
        """连接关闭回调"""
        print(f"WebSocket 已关闭: {close_status_code} - {close_msg}")
        self.is_connected = False

    def _convert_price(self, usd_per_oz: float) -> float:
        """
        将美元/盎司转换为人民币/克

        Args:
            usd_per_oz: 美元/盎司价格

        Returns:
            float: 人民币/克价格（保留2位小数）
        """
        exchange_rate = self.exchange_rate_api.get_usd_to_cny()
        cny_per_gram = (usd_per_oz * exchange_rate) / self.config.OUNCE_TO_GRAM
        return round(cny_per_gram, self.config.PRICE_DECIMAL_PLACES)

    def get_latest_price(self) -> Tuple[Optional[float], str, str]:
        """
        获取最新价格（转换后的人民币/克）

        Returns:
            Tuple[Optional[float], str, str]: (价格浮点数, 显示文本, 更新时间)
            如果离线，价格为 None
        """
        with self.lock:
            if self.latest_data is None:
                if not self.is_connected:
                    return (None, "伦敦金: 离线", "")
                else:
                    return (None, "伦敦金: 等待数据...", "")

            try:
                # 获取当前汇率
                exchange_rate = self.exchange_rate_api.get_usd_to_cny()

                # 转换买入价（用于主显示）
                bid_cny = self._convert_price(self.latest_data['bid'])
                ask_cny = self._convert_price(self.latest_data['ask'])
                spread_usd = self.latest_data['ask'] - self.latest_data['bid']
                spread_cny = ask_cny - bid_cny

                # 生成详细的显示文本
                display_text = f"{bid_cny:.2f} 元/克"

                # 生成工具提示（在 widget 中会用到）
                # 这里只返回基本的显示文本

                # 存储详细信息供工具提示使用
                self.latest_data['bid_cny'] = bid_cny
                self.latest_data['ask_cny'] = ask_cny
                self.latest_data['spread_usd'] = spread_usd
                self.latest_data['spread_cny'] = spread_cny
                self.latest_data['exchange_rate'] = exchange_rate

                return (bid_cny, display_text, self.latest_data['time'])
            except Exception as e:
                print(f"价格转换失败: {e}")
                return (None, "伦敦金: 转换错误", "")

    def get_detailed_info(self) -> tuple:
        """
        获取详细信息文本（用于多行显示）

        Returns:
            tuple: (买入价行, 卖出价行, 差价汇率行, 更新时间行)
        """
        with self.lock:
            if self.latest_data is None or 'bid_cny' not in self.latest_data:
                return ("伦敦金: 无数据", "", "", "")

            # 第一行：买入价
            line1 = f"买入价: ¥{self.latest_data['bid_cny']:.2f}/克 (${self.latest_data['bid']:.2f}/盎司)"

            # 第二行：卖出价
            line2 = f"卖出价: ¥{self.latest_data['ask_cny']:.2f}/克 (${self.latest_data['ask']:.2f}/盎司)"

            # 第三行：差价和汇率
            line3 = f"价差: ${self.latest_data['spread_usd']:.2f} | 汇率: {self.latest_data['exchange_rate']:.4f}"

            # 第四行：更新时间
            line4 = f"更新时间: {self.latest_data['time']}"

            return (line1, line2, line3, line4)

    def stop(self):
        """停止 WebSocket 连接"""
        self.should_stop = True
        if self.ws:
            self.ws.close()
        self.is_connected = False

