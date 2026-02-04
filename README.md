# AnyGold - 实时黄金价格监控桌面小工具

一个简洁的 Windows 桌面小工具，用于实时监控黄金价格。

## ✨ 功能特点

- 🔄 **实时价格更新**：每 5 秒自动获取最新黄金价格
- 🔀 **多数据源切换**：支持浙商银行、民生银行和伦敦金实时价格，滚轮切换
- 🌍 **伦敦金实时价格**：通过 WebSocket 获取伦敦金实时行情，自动汇率转换为人民币/克
- 📊 **价格变动追踪**：显示相对于当日基准价格的涨跌变化
- 🔔 **智能提醒**：价格变动超过 1% 时自动弹窗提醒
- 🎨 **多主题支持**：深色/浅色/透明主题，双击切换
- 🖱️ **灵活交互**：左键拖拽、右键关闭、点击滚轮切换数据源
- 🔧 **窗口缩放**：滚轮调整窗口大小
- 📌 **窗口置顶**：始终显示在其他窗口之上

## 📁 项目结构

```
AnyGold/
├── src/                    # 源代码目录
│   ├── __init__.py         # 包初始化文件
│   ├── main.py             # 程序入口
│   ├── config.py           # 配置文件
│   ├── api.py              # API 接口模块
│   ├── ui.py               # UI 界面模块
│   └── widget.py           # 核心业务逻辑
├── assets/                 # 资源文件目录
├── AnyGold.py              # 原始单文件版本（保留兼容）
├── requirements.txt        # Python 依赖
├── setup.py                # 安装配置
├── run.py                  # 快速启动脚本
└── README.md               # 项目说明
```

## 🚀 快速开始

### 环境要求

- Python 3.8+
- Windows 操作系统

### 安装依赖

```bash
pip install -r requirements.txt
```

**主要依赖**：
- `PySide6>=6.4.0` - Qt6 GUI 框架
- `requests>=2.25.0` - HTTP 请求库
- `websocket-client>=1.5.0` - WebSocket 客户端
- `beautifulsoup4>=4.9.0` - HTML 解析（用于中国银行汇率获取）

### 运行程序

**方式一：使用启动脚本**
```bash
python run.py
```

**方式二：模块方式运行**
```bash
python -m src.main
```

**方式三：使用原始单文件**
```bash
python AnyGold.py
```

## 🖱️ 操作说明

| 操作 | 功能 |
|------|------|
| **左键拖拽** | 移动窗口到任意位置 |
| **双击左键** | 循环切换主题（深色→浅色→透明） |
| **右键点击** | 关闭程序 |
| **滚轮滑动** | 调整窗口大小（向上放大，向下缩小） |
| **Ctrl+滚轮** | 切换数据源（浙商银行→民生银行→伦敦金） |
| **中键点击** | 切换数据源（同 Ctrl+滚轮功能） |

## ⚙️ 配置参数

在 `src/config.py` 中可以调整以下参数：

| 配置项 | 默认值                     | 说明 |
|--------|-------------------------|------|
| `API_URLS` | 2个API地址                 | HTTP API列表（浙商、民生） |
| `API_NAMES` | ["浙商银行", "民生银行", "伦敦金"] | 数据源名称显示 |
| `CURRENT_API_INDEX` | 0                       | 默认使用的数据源索引（0=浙商） |
| `UPDATE_INTERVAL` | 5                       | 价格更新间隔（秒） |
| `ALERT_THRESHOLD` | 1.0                     | 提醒阈值（%） |
| `WINDOW_WIDTH` | 220                     | 窗口宽度（像素） |
| `WINDOW_HEIGHT` | 110                     | 窗口高度（像素） |
| `WINDOW_MIN_WIDTH` | 50                      | 最小窗口宽度 |
| `WINDOW_MIN_HEIGHT` | 25                      | 最小窗口高度 |
| `WS_DOMAIN_API` | 动态获取地址                  | WebSocket 地址获取 API |
| `EXCHANGE_RATE_CACHE_TIME` | 3600                    | 汇率缓存时间（秒） |

## 📦 打包为 EXE

### 方法一：使用配置好的打包脚本（推荐）

```bash
python build.py
```

### 方法二：使用spec文件打包

```bash
# 完整版本
pyinstaller AnyGold.spec

# 精简版本（体积更小）
pyinstaller AnyGold_slim.spec
```

### 方法三：手动打包

```bash
pyinstaller --onefile --windowed --icon=assets\icon.ico --name=AnyGold run.py
```

**图标说明**：
- 程序使用 `assets\icon.ico` 作为源图标

打包后的 exe 文件位于 `dist/AnyGold.exe`

## 🔧 开发说明

### 模块职责

- **config.py**：配置参数管理（API、窗口、WebSocket、汇率等配置）
- **api.py**：黄金价格 API 调用（HTTP API、WebSocket、汇率转换）
- **ui.py**：界面组件（主窗口、提醒弹窗、字体控制）
- **widget.py**：核心业务逻辑协调（价格更新、数据源切换、提醒触发）

## 📝 数据来源

### 1. 浙商银行黄金（默认）
- API 地址：`https://api.jdjygold.com/gw2/generic/jrm/h5/m/stdLatestPrice?productSku=1961543816`
- 数据特点：浙商银行提供的黄金价格数据
- 更新方式：HTTP 轮询，每 5 秒更新

### 2. 民生银行黄金
- API 地址：`https://api.jdjygold.com/gw/generic/hj/h5/m/latestPrice`
- 数据特点：民生银行提供的黄金价格数据
- 更新方式：HTTP 轮询，每 5 秒更新

### 3. 伦敦金实时行情（新增）
- 数据来源：通过 WebSocket 实时推送
- WebSocket 地址：动态获取（`https://www.jrjr.com/api/getDomainInfo`）
- 数据特点：
  - 实时买入价和卖出价（美元/盎司）
  - 自动汇率转换为人民币/克
  - 支持多级汇率源（主：ExchangeRate API，备：中国银行）
  - 显示价差、汇率等详细信息
- 更新方式：WebSocket 推送，实时更新

**使用说明**：程序支持在三个数据源之间实时切换，通过 Ctrl+滚轮或中键点击即可切换。不同来源的价格可能存在差异，伦敦金价格已自动转换为人民币/克单位。

## 📄 许可证

MIT License

## 🤝 贡献

欢迎提出问题和建议！

