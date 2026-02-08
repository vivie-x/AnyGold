

# AnyGold - 实时黄金价格监控桌面小工具

[![Version](https://img.shields.io/badge/version-2.5.0-blue.svg)](https://github.com/vivie-x/AnyGold)
[![Python](https://img.shields.io/badge/python-3.8+-brightgreen.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

一个简洁的 Windows 桌面小工具，用于实时监控黄金价格。

## 📋 版本信息

**当前版本**：v2.5.0

### 主要特性
- 🔄 实时价格更新，每 5 秒自动获取最新数据
- 🔀 支持多数据源切换（浙商银行、民生银行、伦敦金）
- 🌍 伦敦金 WebSocket 实时行情推送
- 📊 价格变动追踪与智能提醒
- 🎨 多主题支持（深色/浅色/透明）
- 🤖 **AI 智能分析**：基于大模型提供价格变动分析和投资建议

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
- 🤖 **AI 智能分析**（可选）：价格变动时自动提供 AI 分析建议
  - 支持多个大模型（OpenAI、通义千问、Deepseek）
  - 智能分析价格驱动因素和短期走势
  - 提供买入/持有/卖出操作建议
  - 成本控制（每日调用限额、结果缓存）

## 📁 项目结构

```
AnyGold/
├── src/                    # 源代码目录
│   ├── __init__.py         # 包初始化文件
│   ├── main.py             # 程序入口
│   ├── config.py           # 配置文件
│   ├── api.py              # API 接口模块
│   ├── ui.py               # UI 界面模块
│   ├── widget.py           # 核心业务逻辑
│   └── ai_analyzer.py      # AI 分析模块（新增）
├── assets/                 # 资源文件目录
├── AnyGold.py              # 原始单文件版本（保留兼容）
├── requirements.txt        # Python 依赖
├── .env.example            # 环境变量配置示例
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
- `openai>=1.12.0` - OpenAI SDK（AI 功能，可选）
- `python-dotenv>=1.0.0` - 环境变量管理（AI 功能，可选）

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

## 🤖 AI 智能分析功能（可选）

### 功能概述

当黄金价格出现显著变动（超过 1%）时，AI 智能分析功能将自动：
1. 分析价格变动的可能驱动因素（经济指标、地缘政治等）
2. 预判短期走势（1-3天）
3. 提供操作建议（买入/持有/卖出）及核心理由

### 支持的模型

| 提供商 | 模型选项 | 特点 |
|--------|----------|------|
| **通义千问** | qwen-plus, qwen-turbo, qwen-max | 推荐，性价比高，速度快 |
| **OpenAI** | gpt-3.5-turbo, gpt-4, gpt-4-turbo | 经典模型，分析质量高 |
| **Deepseek** | deepseek-chat, deepseek-coder | 新兴模型，成本较低 |

### 配置方法

1. **复制配置模板**
   ```bash
   cp .env.example .env
   ```

2. **编辑 `.env` 文件，填入配置**
   ```bash
   # 启用AI功能
   AI_ENABLED=true
   
   # 选择提供商（qwen/openai/deepseek）
   AI_PROVIDER=qwen
   
   # 填入您的 API Key
   AI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxx
   
   # 选择模型
   AI_MODEL=qwen-plus
   
   # 控制成本
   AI_MAX_TOKENS=300
   AI_CALL_LIMIT_PER_DAY=20
   ```

3. **获取 API Key**
   - **通义千问**：访问 [DashScope控制台](https://dashscope.console.aliyun.com/apiKey)
   - **OpenAI**：访问 [OpenAI API Keys](https://platform.openai.com/api-keys)
   - **Deepseek**：访问 [Deepseek API Keys](https://platform.deepseek.com/api_keys)

### 成本估算

基于默认配置（每日最多 20 次调用，每次 300 tokens）：

| 提供商 | 模型 | 预计日成本 | 预计月成本 |
|--------|------|-----------|-----------|
| 通义千问 | qwen-plus | ¥0.02 | ¥0.60 |
| OpenAI | gpt-3.5-turbo | ¥0.15 | ¥4.50 |
| Deepseek | deepseek-chat | ¥0.01 | ¥0.30 |

*注：实际成本可能因价格波动和使用情况有所不同*

### 成本控制机制

1. **每日调用限额**：默认 20 次/天（可配置）
2. **智能缓存**：相同价格变动（±0.1%）的分析结果缓存 5 分钟
3. **按需触发**：仅在价格变动超过阈值（1%）时触发
4. **可选功能**：可通过配置完全关闭，不影响核心功能

### 免责声明

⚠️ **重要提示**：
- AI 生成的分析建议仅供参考，不构成投资建议
- 投资有风险，决策需谨慎，盈亏自负
- 建议结合多方信息和个人风险承受能力做出投资决策
- 本工具开发者不对任何投资损失承担责任

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
| `WINDOW_WIDTH` | 230                     | 窗口宽度（像素） |
| `WINDOW_HEIGHT` | 110                     | 窗口高度（像素） |
| `WINDOW_MIN_WIDTH` | 80                      | 最小窗口宽度 |
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

- **config.py**：配置参数管理（API、窗口、WebSocket、汇率、AI 等配置）
- **api.py**：黄金价格 API 调用（HTTP API、WebSocket、汇率转换）
  - `GoldPriceAPI` 类：负责获取浙商银行和民生银行黄金价格
  - `ExchangeRateAPI` 类：负责获取美元兑人民币汇率
  - `LondonGoldWebSocket` 类：负责伦敦金 WebSocket 连接和实时价格获取
- **ai_analyzer.py**：AI 智能分析（价格变动分析、投资建议生成）
  - `AIAnalyzer` 类：负责调用大模型 API，提供智能分析建议
- **ui.py**：界面组件
  - `MainWindow` 类：主窗口界面
  - `AlertWindow` 类：价格变动提醒弹窗（含 AI 分析标签页）
- **widget.py**：核心业务逻辑协调（价格更新、数据源切换、提醒触发、AI 分析集成）
- **main.py**：程序入口点

### 技术栈

- **GUI 框架**：PySide6 (Qt6)
- **网络请求**：requests
- **WebSocket**：websocket-client
- **数据解析**：beautifulsoup4
- **AI 集成**：openai（支持多个提供商）

## 📝 数据来源

### 1. 浙商银行黄金（默认）
- API 地址：`https://api.jdjygold.com/gw2/generic/jrm/h5/m/stdLatestPrice?productSku=1961543816`
- 数据特点：浙商银行提供的黄金价格数据
- 更新方式：HTTP 轮询，每 5 秒更新

### 2. 民生银行黄金
- API 地址：`https://api.jdjygold.com/gw/generic/hj/h5/m/latestPrice`
- 数据特点：民生银行提供的黄金价格数据
- 更新方式：HTTP 轮询，每 5 秒更新

### 3. 伦敦金实时行情
- 数据来源：通过 WebSocket 实时推送
- WebSocket 地址：动态获取（`https://www.jrjr.com/api/getDomainInfo`）
- 数据特点：
  - 实时买入价（美元/盎司）
  - 自动汇率转换为人民币/克显示
  - 支持多级汇率源（主：ExchangeRate API，备：中国银行）
- 更新方式：WebSocket 推送，实时更新

**使用说明**：程序支持在三个数据源之间实时切换，通过 Ctrl+滚轮或中键点击即可切换。不同来源的价格可能存在差异，伦敦金价格已自动转换为人民币/克单位。

## ❓ 常见问题

**Q: 数据无法更新/显示"获取失败"？**  
A: 检查网络连接，或尝试切换到其他数据源（Ctrl+滚轮）

**Q: 伦敦金价格显示不正常？**  
A: WebSocket 连接需要时间，等待 5-10 秒；如长时间无数据，切换到其他数据源后再切回

**Q: 如何修改更新频率或提醒阈值？**  
A: 编辑 `src/config.py` 文件，修改 `UPDATE_INTERVAL` 和 `ALERT_THRESHOLD` 参数

**Q: 如何设置开机自启动？**  
A: 按 `Win+R` 输入 `shell:startup` 打开启动文件夹，将 exe 快捷方式放进去

**Q: 程序占用资源情况？**  
A: 内存约 50-80MB，CPU 空闲时几乎为 0，网络流量每小时约 1-2MB

**Q: AI 功能如何启用？**  
A: 复制 `.env.example` 为 `.env`，填入 API Key，设置 `AI_ENABLED=true`

**Q: AI 分析没有显示？**  
A: 检查 `.env` 配置是否正确，API Key 是否有效；查看是否超过每日调用限额

**Q: AI 功能会影响核心功能吗？**  
A: 不会，AI 功能完全独立，即使配置错误或 API 失败也不影响价格监控

**Q: 如何关闭 AI 功能？**  
A: 在 `.env` 中设置 `AI_ENABLED=false`，或直接删除 `.env` 文件

**Q: AI 分析的成本如何？**  
A: 使用默认配置（通义千问 qwen-plus），每月成本约 ¥0.60；可通过调整每日限额控制成本

## 📄 开源协议

本项目采用 [MIT License](LICENSE) 开源协议

## 📧 联系方式

- **作者**：vivie、小程你好会😯
- **邮箱**：1632631306@qq.com、1098670977@qq.com




**如果这个项目对你有帮助，欢迎 Star ⭐ 支持一下！**

Made with ❤️ by vivie、小程你好会😯
