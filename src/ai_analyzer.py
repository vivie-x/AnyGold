"""
AI 分析模块 - 提供智能的黄金价格分析和投资建议
"""

import os
import time
from datetime import datetime, date
from typing import Optional, Dict, Any
import threading


class AIAnalyzer:
    """AI分析器 - 基于价格变动提供智能分析建议"""

    def __init__(self, config):
        """
        初始化AI分析器

        Args:
            config: 配置对象，包含AI相关配置
        """
        self.config = config
        self.client = None
        self.enabled = config.AI_ENABLED
        self.provider = config.AI_PROVIDER
        self.api_key = config.AI_API_KEY
        self.model = config.AI_MODEL
        self.max_tokens = config.AI_MAX_TOKENS

        # 调用次数限制
        self.call_limit_per_day = config.AI_CALL_LIMIT_PER_DAY
        self.call_count = 0
        self.last_reset_date = date.today()

        # 缓存机制 - 避免短时间内重复分析相同的价格变动
        # 格式: {(price_rounded, change_percent_rounded): (suggestion, timestamp)}
        self.cache = {}
        self.cache_ttl = 300  # 缓存有效期5分钟
        self.lock = threading.Lock()

        # 初始化OpenAI客户端
        if self.enabled and self.api_key:
            self._init_client()

    def _init_client(self):
        """初始化OpenAI客户端（支持多个提供商）"""
        try:
            from openai import OpenAI

            # 根据提供商设置base_url
            base_url = None
            if self.provider == "qwen":
                base_url = "https://dashscope.aliyuncs.com/compatible-mode/v1"
            elif self.provider == "deepseek":
                base_url = "https://api.deepseek.com"
            elif self.provider == "openai":
                base_url = None  # 使用默认的OpenAI地址

            if base_url:
                self.client = OpenAI(api_key=self.api_key, base_url=base_url)
            else:
                self.client = OpenAI(api_key=self.api_key)

        except ImportError:
            print("警告: openai 库未安装，AI功能将被禁用")
            self.enabled = False
        except Exception as e:
            print(f"初始化AI客户端失败: {e}")
            self.enabled = False

    def _reset_daily_limit(self):
        """重置每日调用次数"""
        today = date.today()
        if today != self.last_reset_date:
            self.call_count = 0
            self.last_reset_date = today

    def _check_call_limit(self) -> bool:
        """
        检查是否超过每日调用限制

        Returns:
            bool: True表示可以调用，False表示超过限制
        """
        with self.lock:
            self._reset_daily_limit()
            if self.call_count >= self.call_limit_per_day:
                return False
            return True

    def _increment_call_count(self):
        """增加调用次数"""
        with self.lock:
            self._reset_daily_limit()
            self.call_count += 1

    def _get_cache_key(self, current_price: float, change_percent: float) -> tuple:
        """
        生成缓存键（对价格和变化百分比进行取整）

        Args:
            current_price: 当前价格
            change_percent: 变化百分比

        Returns:
            tuple: 缓存键
        """
        # 价格取整到1位小数，变化百分比取整到0.1%
        price_rounded = round(current_price, 1)
        change_rounded = round(change_percent, 1)
        return (price_rounded, change_rounded)

    def _get_from_cache(self, current_price: float, change_percent: float) -> Optional[str]:
        """
        从缓存中获取分析结果

        Args:
            current_price: 当前价格
            change_percent: 变化百分比

        Returns:
            Optional[str]: 缓存的分析结果，如果不存在或过期则返回None
        """
        cache_key = self._get_cache_key(current_price, change_percent)
        with self.lock:
            if cache_key in self.cache:
                suggestion, timestamp = self.cache[cache_key]
                # 检查缓存是否过期
                if time.time() - timestamp < self.cache_ttl:
                    return suggestion
                else:
                    # 缓存过期，删除
                    del self.cache[cache_key]
        return None

    def _save_to_cache(self, current_price: float, change_percent: float, suggestion: str):
        """
        保存分析结果到缓存

        Args:
            current_price: 当前价格
            change_percent: 变化百分比
            suggestion: 分析结果
        """
        cache_key = self._get_cache_key(current_price, change_percent)
        with self.lock:
            self.cache[cache_key] = (suggestion, time.time())

    def _build_prompt(self, current_price: float, change_percent: float,
                     base_price: float, current_time: str) -> str:
        """
        构建AI分析提示词

        Args:
            current_price: 当前价格
            change_percent: 变化百分比
            base_price: 基准价格
            current_time: 当前时间

        Returns:
            str: 构建的提示词
        """
        prompt = f"""当前黄金价格: {current_price:.2f} 元/克
价格变动: {change_percent:+.2f}%
基准价格: {base_price:.2f} 元/克
时间: {current_time}

请基于当前的国际形势、经济指标(美元指数、通胀率、地缘政治等)、市场情绪等因素,
简要分析这次价格变动的原因,并给出:

1. 可能的驱动因素(50字以内)
2. 短期走势预判(1-3天,50字以内)
3. 操作建议(买入/持有/卖出)及核心理由(100字以内)

要求:
- 总字数控制在200字以内
- 语言简洁专业
- 避免模棱两可的表述
- 基于客观分析,不做过度承诺
"""
        return prompt

    def get_suggestion(self, current_price: float, change_percent: float,
                      base_price: float) -> Dict[str, Any]:
        """
        获取AI分析建议

        Args:
            current_price: 当前价格
            change_percent: 变化百分比
            base_price: 基准价格

        Returns:
            Dict[str, Any]: 包含分析结果和状态的字典
                {
                    'success': bool,  # 是否成功
                    'suggestion': str,  # 分析建议（成功时）
                    'error': str,  # 错误信息（失败时）
                    'cached': bool,  # 是否来自缓存
                    'calls_remaining': int  # 剩余调用次数
                }
        """
        # 检查AI功能是否启用
        if not self.enabled:
            return {
                'success': False,
                'error': 'AI功能未启用',
                'cached': False,
                'calls_remaining': 0
            }

        # 检查是否有API Key
        if not self.api_key:
            return {
                'success': False,
                'error': 'API Key未配置',
                'cached': False,
                'calls_remaining': 0
            }

        # 先检查缓存
        cached_result = self._get_from_cache(current_price, change_percent)
        if cached_result:
            return {
                'success': True,
                'suggestion': cached_result,
                'cached': True,
                'calls_remaining': self.call_limit_per_day - self.call_count
            }

        # 检查调用限制
        if not self._check_call_limit():
            return {
                'success': False,
                'error': f'今日调用次数已达上限({self.call_limit_per_day}次)',
                'cached': False,
                'calls_remaining': 0
            }

        # 调用AI API
        try:
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            prompt = self._build_prompt(current_price, change_percent, base_price, current_time)

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "你是一位专业的黄金投资分析师，擅长基于价格变动和市场形势提供简洁准确的投资建议。"},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=self.max_tokens,
                temperature=0.7
            )

            suggestion = response.choices[0].message.content.strip()

            # 增加调用次数
            self._increment_call_count()

            # 保存到缓存
            self._save_to_cache(current_price, change_percent, suggestion)

            return {
                'success': True,
                'suggestion': suggestion,
                'cached': False,
                'calls_remaining': self.call_limit_per_day - self.call_count
            }

        except Exception as e:
            error_msg = str(e)
            # 简化错误信息
            if "authentication" in error_msg.lower() or "api key" in error_msg.lower():
                error_msg = "API Key 无效或已过期"
            elif "rate limit" in error_msg.lower():
                error_msg = "API调用频率超限，请稍后再试"
            elif "timeout" in error_msg.lower():
                error_msg = "网络请求超时"
            else:
                error_msg = f"AI分析失败: {error_msg[:50]}"

            return {
                'success': False,
                'error': error_msg,
                'cached': False,
                'calls_remaining': self.call_limit_per_day - self.call_count
            }

    def get_status(self) -> Dict[str, Any]:
        """
        获取AI分析器状态信息

        Returns:
            Dict[str, Any]: 状态信息
        """
        with self.lock:
            self._reset_daily_limit()
            return {
                'enabled': self.enabled,
                'provider': self.provider,
                'model': self.model,
                'calls_today': self.call_count,
                'calls_remaining': self.call_limit_per_day - self.call_count,
                'call_limit': self.call_limit_per_day,
                'cache_size': len(self.cache)
            }
