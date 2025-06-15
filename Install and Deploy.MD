# AI-Powered-Fund



## INSTALL AND DEPLOY



## poetry 

`poetry` 是 Python 的一个依赖管理和打包工具，旨在简化项目环境配置、依赖安装及代码分发流程。下面详细介绍其功能和使用场景：

### 主要功能

1. **依赖管理**
   - 自动生成和更新 `poetry.lock` 文件，确保依赖版本的一致性。
   - 通过 `pyproject.toml` 文件声明项目依赖，替代传统的 `requirements.txt`。
   - 支持语义化版本约束（如 `^1.0.0`、`~2.0.0`）和直接引用 Git 仓库。
2. **虚拟环境管理**
   - 自动创建和管理项目专属的虚拟环境，无需手动执行 `venv` 或 `virtualenv`。
   - 通过 `poetry shell` 或 `poetry run` 直接在虚拟环境中执行命令。
3. **项目打包与发布**
   - 自动生成符合 PEP 517/518 标准的包，支持 `sdist` 和 `wheel` 格式。
   - 简化发布流程，通过 `poetry publish` 直接上传到 PyPI。
4. **项目脚手架**
   - 使用 `poetry new <project-name>` 快速创建标准化的项目结构。

```bash
# 添加依赖（自动更新 pyproject.toml 和 poetry.lock）
poetry add requests
```



## env 环境配置

```
环境配置文件
.env.example
.env
```

項目運行

```
# 在项目根目录运行（ai-hedge-fund/）
poetry run python -m src.main --ticker AAPL,MSFT,NVDA
# 分析单只股票
 poetry run python -m src.main --ticker AAPL 
```

#### **模型服务互补关系**

| **场景**         | **推荐模型服务**    | **原因**                          |
| :--------------- | :------------------ | :-------------------------------- |
| 中文金融报告分析 | `DEEPSEEK_API_KEY`  | 深度求索对中文金融语义理解更强    |
| 高频策略生成     | `GROQ_API_KEY`      | Groq LPU芯片提供毫秒级响应        |
| 多模态财报分析   | `GOOGLE_API_KEY`    | Gemini擅长图文混合推理            |
| 复杂金融推理     | `ANTHROPIC_API_KEY` | Claude 3.5 Sonnet金融基准测试最优 |
| 低成本通用任务   | `OPENAI_API_KEY`    | GPT-4o性价比高                    |

**原本版本的数据来源集： https://api.financialdatasets.ai**

增加 金融数据源 Add financial data sources

```bash
poetry add akshare yfinance
```

akshare接口教程  https://akshare.akfamily.xyz/data/stock/stock.html

测试美股 蔚来NIO  阿里吧吧BABA

yfinance 港股接口



## 安装 FUTU API

```
poetry add futu
poetry add futu-api 
```

必须安装这两个组件才能使用FUTU API

#### 安装 TA-Lib（可选）

`TA-Lib`（Technical Analysis Library）是一个用于金融市场技术分析的开源库。它提供了一系列强大的工具和指标，帮助分析和预测市场趋势。

### 主要功能

1. **技术指标**：
   - 提供超过 150 种常用的技术指标，如移动平均线（MA）、相对强弱指数（RSI）、布林带（Bollinger Bands）、MACD 等。
2. **价格数据处理**：
   - 能够处理和分析历史价格数据，包括开盘价、收盘价、最高价、最低价和成交量。
3. **信号生成**：
   - 可以根据技术指标生成买入或卖出信号，帮助交易者做出决策。
4. **多种编程语言支持**：
   - 除了 Python，`TA-Lib` 还支持 C、C++、Java、Perl 等多种编程语言。

### 应用场景

- **量化交易**：用于开发交易策略和自动化交易系统。
- **市场分析**：帮助分析师和交易员识别市场趋势和潜在的交易机会。
- **投资决策**：为投资者提供基于技术分析的决策支持。

```
pip install TA-Lib  或：
poetry add TA-Lib
```

**对于 Ubuntu/Debian**:

```
sudo apt-get install build-essential
sudo apt-get install libta-lib0-dev
```



## 改造的相关函数：

#### **1. 重写数据获取函数（共8个关键函数）**

需修改 `src/tools/api.py` 中的以下函数，替换为港股接口3：

| **原函数**                | **港股适配方案**                                             |
| :------------------------ | :----------------------------------------------------------- |
| `get_prices()`            | 调用AKShare的 `stock_hk_daily()`，注意处理日期格式（YYYYMMDD） |
| `get_financial_metrics()` | 使用AKShare的 `stock_hk_financial_report()` 提取财报指标     |
| `get_market_cap()`        | 从AKShare的 `stock_hk_spot()` 实时数据中提取市值             |
| `get_company_news()`      | 替换为eFin或富途的新闻API（AKShare无港股新闻）               |
| `get_insider_trades()`    | 港股无公开内幕交易数据，可注释此功能或改用大股东持股变动数据 |
| 其他函数                  | 保持逻辑，仅替换数据源调用                                   |

**魔改后必须注意股票代码格式:  a03690.HK  002236.SZ**

安装最新版本 pip install akshare --upgrade  
[notice] A new release of pip is available: 24.3.1 -> 25.1.1

## 前端

**http://127.0.0.1:5173/**