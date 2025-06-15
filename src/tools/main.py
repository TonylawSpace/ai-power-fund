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



if __name__ == "__main__":

    # get_financial_metrics
    tencent_metrics = get_financial_metrics("00700.HK")
    for metric in tencent_metrics:
        print(f"{metric.report_period}: 市盈率={metric.price_to_earnings_ratio}, ROE={metric.return_on_equity}")

    # 测试美团
    meituan_metrics = get_financial_metrics("03690.HK")
    for metric in meituan_metrics:
        print(f"{metric.report_period}: 营收增长={metric.revenue_growth}%")

