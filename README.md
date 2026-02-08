# AnyGold - 实时黄金价格监控桌面小工具

[![Version](https://img.shields.io/badge/version-2.6.0-blue.svg)](https://github.com/vivie-x/AnyGold)
[![Python](https://img.shields.io/badge/python-3.8+-brightgreen.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

一个简洁的 Windows 桌面小工具，实时监控黄金价格。

## ✨ 核心特性

- 🔄 **实时更新** - 每 5 秒自动获取最新价格
- 🔀 **多数据源** - 浙商银行、民生银行、伦敦金实时行情（WebSocket）
- 📊 **智能提醒** - 价格变动超过 1% 自动弹窗
- 🎨 **多主题** - 深色/浅色/透明主题切换
- 🤖 **AI 分析**（可选）- 支持 OpenAI/通义千问/Deepseek，智能分析价格走势

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
│   ├── ai_analyzer.py      # AI 分析模块
│   └── version.py          # 版本信息
├── tests/                  # 单元测试目录
│   ├── __init__.py
│   ├── test_api.py
│   └── test_config.py
├── assets/                 # 资源文件目录
│   └── icon.ico
├── requirements.txt        # Python 依赖
├── .env.example            # 环境变量配置示例
├── setup.py                # 安装配置
├── build.py                # 打包脚本
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

## 🤖 AI 智能分析（可选）

<details>
<summary>点击展开配置说明</summary>

### 快速配置

```bash
# 1. 复制配置文件
cp .env.example .env

# 2. 编辑 .env，填入以下内容
AI_ENABLED=true
AI_PROVIDER=qwen  # 可选: openai/qwen/deepseek
AI_API_KEY=sk-xxxxxxxxxxxxx
AI_MODEL=qwen-plus
```

### 获取 API Key

- **通义千问**（推荐）: https://dashscope.console.aliyun.com/apiKey
- **OpenAI**: https://platform.openai.com/api-keys
- **Deepseek**: https://platform.deepseek.com/api_keys

### 成本参考

| 提供商 | 月成本估算 | 说明 |
|--------|-----------|------|
| 通义千问 | ~¥0.60 | 推荐，性价比高 |
| Deepseek | ~¥0.30 | 最便宜 |
| OpenAI | ~¥4.50 | 质量最高 |

⚠️ **免责声明**：AI 分析仅供参考，不构成投资建议，投资有风险。

</details>

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

<details>
<summary>点击查看可调整参数</summary>

编辑 `src/config.py` 中的以下参数：

| 配置项 | 默认值 | 说明 |
|--------|--------|------|
| `UPDATE_INTERVAL` | 5 | 价格更新间隔（秒） |
| `ALERT_THRESHOLD` | 1.0 | 提醒阈值（%） |
| `WINDOW_WIDTH/HEIGHT` | 230/110 | 窗口尺寸 |
| `CURRENT_API_INDEX` | 0 | 默认数据源（0=浙商，1=民生，2=伦敦金） |

</details>

## 📦 打包为 EXE

<details>
<summary>点击查看打包方法</summary>

### 推荐方法
```bash
python build.py
```

### 手动打包
```bash
# 使用 spec 文件
pyinstaller AnyGold_slim.spec

# 或者命令行
pyinstaller --onefile --windowed --icon=assets\icon.ico --name=AnyGold run.py
```

打包后的文件位于 `dist/AnyGold.exe`

</details>

## 🔧 开发说明

<details>
<summary>点击查看模块说明</summary>

### 模块职责

| 模块 | 职责 |
|------|------|
| **config.py** | 配置参数管理 |
| **api.py** | API 调用、WebSocket、汇率转换 |
| **ai_analyzer.py** | AI 智能分析 |
| **ui.py** | 界面组件（主窗口、提醒窗口） |
| **widget.py** | 核心业务逻辑协调 |
| **main.py** | 程序入口 |

### 技术栈
- GUI: PySide6 (Qt6)
- 网络: requests + websocket-client
- 解析: beautifulsoup4
- AI: openai

</details>

## 📝 数据来源

| 数据源 | 更新方式 | 特点 |
|--------|---------|------|
| 浙商银行 | HTTP 轮询（5秒） | 默认数据源 |
| 民生银行 | HTTP 轮询（5秒） | 备用数据源 |
| 伦敦金 | WebSocket 实时推送 | 美元/盎司自动转换为人民币/克 |

💡 使用 **Ctrl+滚轮** 或 **中键点击** 可在数据源间切换

## ❓ 常见问题

<details>
<summary>点击查看常见问题解答</summary>

**Q: 数据无法更新/显示"获取失败"？**  
A: 检查网络连接，或尝试切换到其他数据源（Ctrl+滚轮）

**Q: 伦敦金价格显示不正常？**  
A: WebSocket 连接需要时间，等待 5-10 秒；如长时间无数据，切换到其他数据源后再切回

**Q: 如何修改更新频率或提醒阈值？**  
A: 编辑 `src/config.py` 文件，修改 `UPDATE_INTERVAL` 和 `ALERT_THRESHOLD` 参数

**Q: 如何设置开机自启动？**  
A: 按 `Win+R` 输入 `shell:startup` 打开启动文件夹，将 exe 快捷方式放进去

**Q: AI 功能如何启用？**  
A: 复制 `.env.example` 为 `.env`，填入 API Key，设置 `AI_ENABLED=true`

**Q: 如何关闭 AI 功能？**  
A: 在 `.env` 中设置 `AI_ENABLED=false`，或直接删除 `.env` 文件

</details>

## 📄 开源协议

本项目采用 [MIT License](LICENSE) 开源协议

## 📧 联系方式

- **作者**：vivie、小程你好会😯
- **邮箱**：1632631306@qq.com、1098670977@qq.com




**如果这个项目对你有帮助，欢迎 Star ⭐ 支持一下！**

Made with ❤️ by vivie、小程你好会😯
