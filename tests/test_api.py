"""
API 模块测试
"""

import unittest
from unittest.mock import patch, MagicMock
from src.api import GoldPriceAPI


class TestGoldPriceAPI(unittest.TestCase):
    """测试 GoldPriceAPI 类"""

    def setUp(self):
        """测试前的准备工作"""
        self.api = GoldPriceAPI()

    def test_switch_api(self):
        """测试 API 切换功能"""
        initial_index = self.api.current_api_index
        api_name = self.api.switch_api()

        # 验证索引已切换
        self.assertNotEqual(initial_index, self.api.current_api_index)
        # 验证返回了 API 名称
        self.assertIsInstance(api_name, str)

    def test_get_current_api_name(self):
        """测试获取当前 API 名称"""
        name = self.api.get_current_api_name()
        self.assertIn(name, self.api.config.API_NAMES)

    @patch('requests.get')
    def test_fetch_price_success(self, mock_get):
        """测试成功获取价格"""
        # 模拟成功的 API 响应
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'code': 0,
            'data': {
                'price': '500.00'
            }
        }
        mock_get.return_value = mock_response

        price, text, time = self.api.fetch_price()

        # 验证返回值
        self.assertIsNotNone(price)
        self.assertIsInstance(price, float)
        self.assertIsInstance(text, str)
        self.assertIsInstance(time, str)

    @patch('requests.get')
    def test_fetch_price_failure(self, mock_get):
        """测试获取价格失败的情况"""
        # 模拟请求失败
        mock_get.side_effect = Exception("网络错误")

        price, text, time = self.api.fetch_price()

        # 验证失败情况下的返回值
        self.assertIsNone(price)
        self.assertIn("获取失败", text)


if __name__ == '__main__':
    unittest.main()

