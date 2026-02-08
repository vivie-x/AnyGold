"""
配置模块测试
"""

import unittest
from src.config import Config, ThemeConfig


class TestConfig(unittest.TestCase):
    """测试配置类"""

    def test_api_config(self):
        """测试 API 配置"""
        config = Config()

        # 验证 API URLs 配置
        self.assertIsInstance(config.API_URLS, list)
        self.assertGreater(len(config.API_URLS), 0)

        # 验证 API 名称配置
        self.assertIsInstance(config.API_NAMES, list)
        self.assertEqual(len(config.API_NAMES), 3)

    def test_window_config(self):
        """测试窗口配置"""
        config = Config()

        # 验证窗口尺寸配置
        self.assertGreater(config.WINDOW_WIDTH, 0)
        self.assertGreater(config.WINDOW_HEIGHT, 0)
        self.assertLess(config.WINDOW_MIN_WIDTH, config.WINDOW_WIDTH)
        self.assertLess(config.WINDOW_MIN_HEIGHT, config.WINDOW_HEIGHT)

    def test_ai_config_from_env(self):
        """测试从环境变量读取 AI 配置"""
        config = Config()

        # AI 配置应该从环境变量读取
        self.assertIsInstance(config.AI_ENABLED, bool)
        self.assertIsInstance(config.AI_PROVIDER, str)
        self.assertIsInstance(config.AI_MODEL, str)


class TestThemeConfig(unittest.TestCase):
    """测试主题配置类"""

    def test_theme_structure(self):
        """测试主题配置结构"""
        themes = [
            ThemeConfig.DARK_THEME,
            ThemeConfig.LIGHT_THEME,
            ThemeConfig.TRANSPARENT_THEME
        ]

        required_keys = ['bg', 'fg', 'info_fg', 'up_color', 'down_color', 'neutral_color']

        for theme in themes:
            for key in required_keys:
                self.assertIn(key, theme)
                self.assertIsInstance(theme[key], str)


if __name__ == '__main__':
    unittest.main()

