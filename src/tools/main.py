import sys

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage

from colorama import Fore, Style, init
import questionary
from src.agents.portfolio_manager import portfolio_management_agent
from src.agents.risk_manager import risk_management_agent
from src.graph.state import AgentState
from src.utils.display import print_trading_output
from src.utils.analysts import ANALYST_ORDER, get_analyst_nodes
from src.utils.progress import progress
from src.llm.models import LLM_ORDER, OLLAMA_LLM_ORDER, get_model_info, ModelProvider
from src.utils.ollama import ensure_ollama_and_model

import argparse
from datetime import datetime
from dateutil.relativedelta import relativedelta
from src.utils.visualize import save_graph_as_png
import json

from  src.tools.api import get_financial_metrics


# Load environment variables from .env file
load_dotenv()

init(autoreset=True)


# 测试富途财务数据获取
def test_futu_financials():
    print("测试富途财务数据接口...")

    # 测试腾讯控股
    print("\n获取腾讯控股(00700.HK)财务数据:")
    tencent_metrics = get_financial_metrics("00700.HK")

    if tencent_metrics:
        latest = tencent_metrics[0]
        print(f"最新报告期: {latest.report_period}")
        print(f"市盈率: {latest.price_to_earnings_ratio}")
        print(f"市净率: {latest.price_to_book_ratio}")
        print(f"ROE: {latest.return_on_equity}%")
        print(f"股息率: {latest.dividend_yield}%")
        print(f"每股收益: {latest.earnings_per_share}")

        # 打印所有可用指标
        print("\n所有可用指标:")
        for field, value in latest.dict().items():
            if value is not None:
                print(f"{field}: {value}")
    else:
        print("获取腾讯财务数据失败")

    # 测试美团
    print("\n获取美团(03690.HK)财务数据:")
    meituan_metrics = get_financial_metrics("03690.HK")

    if meituan_metrics:
        latest = meituan_metrics[0]
        print(f"最新报告期: {latest.report_period}")
        print(f"营收增长率: {latest.revenue_growth}%")
        print(f"毛利率: {latest.gross_margin}%")
        print(f"自由现金流: {latest.free_cash_flow_per_share}")
    else:
        print("获取美团财务数据失败")


if __name__ == "__main__":
    test_futu_financials()



