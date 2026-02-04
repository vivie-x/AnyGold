"""
配置文件 - 存放应用程序的各种配置参数
"""


class Config:
    """应用程序配置类"""

    # API 配置
    # 可切换的API列表
    API_URLS = [
        "https://api.jdjygold.com/gw2/generic/jrm/h5/m/stdLatestPrice?productSku=1961543816",  # 浙商的API
        "https://api.jdjygold.com/gw/generic/hj/h5/m/latestPrice"  # 民生的API
    ]
    API_NAMES = ["浙商银行", "民生银行", "伦敦金"]  # API名称，用于显示
    API_TIMEOUT = 5  # API 请求超时时间（秒）

    # 当前使用的API索引
    CURRENT_API_INDEX = 0  # 默认使用浙商的API（索引0）

    # 请求头配置
    HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Referer': 'https://jiage.jd.com/',
        'Accept': 'application/json, text/plain, */*'
    }

    # 更新频率配置
    UPDATE_INTERVAL = 5  # 价格更新间隔（秒）

    # 提醒配置
    ALERT_THRESHOLD = 1.0  # 价格变动提醒阈值（百分比）

    # WebSocket 配置（伦敦金实时价格）
    WS_DOMAIN_API = "https://www.jrjr.com/api/getDomainInfo"  # 动态获取WebSocket地址
    WS_BACKUP_URL = "wss://alb-1ko0lowmvacsqia0ij.cn-shenzhen.alb.aliyuncs.com:26203"  # 备用WebSocket地址
    WS_RECONNECT_INTERVAL = 5  # WebSocket重连间隔（秒）
    MAX_WS_RECONNECT_ATTEMPTS = 5  # 最大重连次数

    # 汇率配置
    EXCHANGE_RATE_APIS = [
        "https://api.exchangerate-api.com/v4/latest/USD",  # 主汇率API
        "https://www.boc.cn/sourcedb/whpj/"  # 备用：中国银行官网汇率
    ]
    EXCHANGE_RATE_CACHE_TIME = 3600  # 汇率缓存时间（秒）
    DEFAULT_EXCHANGE_RATE = 7.2  # 默认汇率（所有API都失败时使用）

    # 单位转换常量
    OUNCE_TO_GRAM = 31.1035  # 1盎司 = 31.1035克
    PRICE_DECIMAL_PLACES = 2  # 价格保留小数位数

    # 窗口配置
    WINDOW_WIDTH = 220
    WINDOW_HEIGHT = 110
    WINDOW_MIN_WIDTH = 50  # 最小窗口宽度
    WINDOW_MIN_HEIGHT = 25  # 最小窗口高度
    WINDOW_RESIZE_STEP = 10  # 滚轮调整步长
    WINDOW_INITIAL_X = 100
    WINDOW_INITIAL_Y = 100
    TOPMOST_REFRESH_INTERVAL = 200  # 置顶刷新间隔（毫秒），用于保持窗口在任务栏上方

    # 弹窗配置
    ALERT_WINDOW_WIDTH = 180
    ALERT_WINDOW_HEIGHT = 80
    FADE_STEP = 0.05  # 淡入淡出步长
    FADE_INTERVAL = 30  # 淡入淡出间隔（毫秒）


class ThemeConfig:
    """主题配置类"""

    # 深色主题
    DARK_THEME = {
        'bg': 'black',
        'fg': 'white',
        'info_fg': 'lightgray',
        'up_color': 'red',
        'down_color': 'green',
        'neutral_color': 'white'
    }

    # 浅色主题
    LIGHT_THEME = {
        'bg': 'white',
        'fg': 'black',
        'info_fg': 'darkgray',
        'up_color': 'darkred',
        'down_color': 'darkgreen',
        'neutral_color': 'black'
    }

    # 透明主题（背景透明，字体颜色同深色主题）
    TRANSPARENT_THEME = {
        'bg': 'black',  # 实际会被透明化
        'fg': 'white',
        'info_fg': 'lightgray',
        'up_color': 'red',
        'down_color': 'green',
        'neutral_color': 'white'
    }

