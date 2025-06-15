from dotenv import load_dotenv
from futu import *

import datetime
import os
import pandas as pd
import requests
from typing import Optional
import yfinance as yf
import akshare as ak


from src.data.cache import get_cache
from src.data.models import (
    CompanyNews,
    CompanyNewsResponse,
    FinancialMetrics,
    FinancialMetricsResponse,
    Price,
    PriceResponse,
    LineItem,
    LineItemResponse,
    InsiderTrade,
    InsiderTradeResponse,
    CompanyFactsResponse,
)

# Global cache instance
_cache = get_cache()

# 获取环境变量
load_dotenv()
futu_api_host = os.getenv("FUTU_API_HOST")
futu_api_port = int(os.getenv("FUTU_API_PORT", "11111"))  # 默认值11111

def get_prices_origin(ticker: str, start_date: str, end_date: str) -> list[Price]:
    """Fetch price data from cache or API."""
    # Create a cache key that includes all parameters to ensure exact matches
    cache_key = f"{ticker}_{start_date}_{end_date}"
    
    # Check cache first - simple exact match
    if cached_data := _cache.get_prices(cache_key):
        return [Price(**price) for price in cached_data]

    # If not in cache, fetch from API
    headers = {}
    if api_key := os.environ.get("FINANCIAL_DATASETS_API_KEY"):
        headers["X-API-KEY"] = api_key

    url = f"https://api.financialdatasets.ai/prices/?ticker={ticker}&interval=day&interval_multiplier=1&start_date={start_date}&end_date={end_date}"
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        raise Exception(f"Error fetching data: {ticker} - {response.status_code} - {response.text}")

    # Parse response with Pydantic model
    price_response = PriceResponse(**response.json())
    prices = price_response.prices

    if not prices:
        return []

    # Cache the results using the comprehensive cache key
    _cache.set_prices(cache_key, [p.model_dump() for p in prices])
    return prices


# 修改后代码（AKShare适配）
def get_prices(ticker: str, start_date: str, end_date: str) -> list[Price]:
    # Create a cache key that includes all parameters to ensure exact matches
    cache_key = f"{ticker}_{start_date}_{end_date}"

    # Check cache first - simple exact match
    if cached_data := _cache.get_prices(cache_key):
        return [Price(**price) for price in cached_data]

    stock_df = ak.stock_hk_daily(symbol=ticker, start_date=start_date.replace("-", ""), end_date=end_date.replace("-", ""))
    prices = [
        Price(time=row["date"], open=row["open"], close=row["close"], high=row["high"], low=row["low"], volume=row["volume"])
        for _, row in stock_df.iterrows()
    ]

    # Cache the results using the comprehensive cache key
    _cache.set_prices(cache_key, [p.model_dump() for p in prices])

    return prices


def get_financial_metrics_origin(
    ticker: str,
    end_date: str,
    period: str = "ttm",
    limit: int = 10,
) -> list[FinancialMetrics]:
    """Fetch financial metrics from cache or API."""
    # Create a cache key that includes all parameters to ensure exact matches
    cache_key = f"{ticker}_{period}_{end_date}_{limit}"
    
    # Check cache first - simple exact match
    if cached_data := _cache.get_financial_metrics(cache_key):
        return [FinancialMetrics(**metric) for metric in cached_data]

    # If not in cache, fetch from API
    headers = {}
    if api_key := os.environ.get("FINANCIAL_DATASETS_API_KEY"):
        headers["X-API-KEY"] = api_key

    url = f"https://api.financialdatasets.ai/financial-metrics/?ticker={ticker}&report_period_lte={end_date}&limit={limit}&period={period}"
    response = requests.get(url, headers=headers)

    print("tikcker from https://api.financialdatasets.ai")


    if response.status_code != 200:
        raise Exception(f"Error fetching data: {ticker} - {response.status_code} - {response.text}")

    # Parse response with Pydantic model
    metrics_response = FinancialMetricsResponse(**response.json())
    financial_metrics = metrics_response.financial_metrics

    # retrieve spec ticker
    print(financial_metrics)

    if not financial_metrics:
        return []

    # Cache the results as dicts using the comprehensive cache key
    _cache.set_financial_metrics(cache_key, [m.model_dump() for m in financial_metrics])
    return financial_metrics


def get_financial_metrics(ticker: str, period: str = "annual") -> list[FinancialMetrics]:
    """
    获取港股完整财务指标 (使用AKShare数据源)

    参数:
        ticker: 港股代码 (如 "00700.HK")
        period: 报告周期 ("annual" 或 "quarterly")

    返回:
        按时间倒序排列的财务指标列表
    """
    # 确保代码格式正确
    if not ticker.endswith(".HK"):
        ticker += ".HK"
    pure_code = ticker.split(".")[0]  # 提取纯数字代码

    try:
        # 获取基础财务数据
        df_balance = ak.stock_financial_hk_balance_sheet(symbol=pure_code)
        df_income = ak.stock_financial_hk_income_statement(symbol=pure_code)
        df_cashflow = ak.stock_financial_hk_cash_flow_sheet(symbol=pure_code)

        # 获取市场数据
        quote_df = ak.stock_hk_spot()
        market_data = quote_df[quote_df["symbol"] == ticker].iloc[0] if ticker in quote_df["symbol"].values else {}

        # 获取历史价格数据用于计算增长率
        price_df = ak.stock_hk_daily(symbol=pure_code, adjust="qfq")

        # 合并所有报告日期
        all_dates = sorted(set(df_balance.index) | set(df_income.index) | set(df_cashflow.index), reverse=True)

        metrics_list = []
        prev_data = {}  # 存储前一期数据用于计算增长率

        for report_date in all_dates:
            # 提取各表数据
            balance = df_balance.loc[report_date] if report_date in df_balance.index else pd.Series(dtype=object)
            income = df_income.loc[report_date] if report_date in df_income.index else pd.Series(dtype=object)
            cashflow = df_cashflow.loc[report_date] if report_date in df_cashflow.index else pd.Series(dtype=object)

            # 港股特有字段映射
            field_map = {
                # 利润表指标
                "revenue": "營業額",
                "net_income": "股東應佔盈利",
                "gross_margin": "毛利率",
                "operating_margin": "經營利潤率",
                "net_margin": "淨利率",
                "earnings_per_share": "每股基本盈利",

                # 资产负债表指标
                "total_assets": "總資產",
                "total_liabilities": "總負債",
                "equity": "股東資金",
                "current_assets": "流動資產",
                "current_liabilities": "流動負債",
                "inventory": "存貨",
                "receivables": "應收賬款",
                "cash_and_equivalents": "現金及等價物",

                # 现金流量表指标
                "operating_cash_flow": "經營活動現金流量",
                "investing_cash_flow": "投資活動現金流量",
                "financing_cash_flow": "融資活動現金流量",
                "free_cash_flow": "自由現金流",

                # 港股特有指标
                "dividend_yield": "股息率",
                "h_share_ratio": "H股佔比",
                "red_chip_premium": "紅籌溢價"
            }

            # 计算财务比率
            def get_ratio(numerator, denominator):
                """安全计算比率"""
                num_val = numerator if isinstance(numerator, (int, float)) else 0
                den_val = denominator if isinstance(denominator, (int, float)) and denominator != 0 else 1
                return num_val / den_val

            # 创建财务指标对象
            metric = FinancialMetrics(
                ticker=ticker,
                report_period=report_date.strftime("%Y-%m-%d"),
                period=period,
                currency="HKD",  # 港币

                # 估值指标
                market_cap=market_data.get("market_cap", None),
                enterprise_value=market_data.get("enterprise_value", None),
                price_to_earnings_ratio=market_data.get("pe_ratio", None),
                price_to_book_ratio=(
                    get_ratio(market_data.get("price", 0), balance.get("每股賬面資產淨值", 0))
                    if "每股賬面資產淨值" in balance else None
                ),
                price_to_sales_ratio=(
                    get_ratio(market_data.get("price", 0), income.get("營業額", 0))
                    if "營業額" in income else None
                ),
                enterprise_value_to_ebitda_ratio=(
                    get_ratio(market_data.get("enterprise_value", 0), income.get("EBITDA", 0))
                    if "EBITDA" in income else None
                ),
                enterprise_value_to_revenue_ratio=(
                    get_ratio(market_data.get("enterprise_value", 0), income.get("營業額", 0))
                    if "營業額" in income else None
                ),
                free_cash_flow_yield=(
                    get_ratio(cashflow.get("自由現金流", 0), market_data.get("market_cap", 1))
                    if "自由現金流" in cashflow else None
                ),
                peg_ratio=None,  # 港股通常不提供PEG比率

                # 利润率指标
                gross_margin=income.get(field_map["gross_margin"], None),
                operating_margin=income.get(field_map["operating_margin"], None),
                net_margin=income.get(field_map["net_margin"], None),
                return_on_equity=(
                    get_ratio(income.get("股東應佔盈利", 0), balance.get("股東資金", 1))
                    if "股東應佔盈利" in income and "股東資金" in balance else None
                ),
                return_on_assets=(
                    get_ratio(income.get("股東應佔盈利", 0), balance.get("總資產", 1))
                    if "股東應佔盈利" in income and "總資產" in balance else None
                ),
                return_on_invested_capital=(
                    get_ratio(income.get("經營利潤", 0), (balance.get("總資產", 0) - balance.get("流動負債", 0)))
                    if "經營利潤" in income else None
                ),

                # 周转率指标
                asset_turnover=(
                    get_ratio(income.get("營業額", 0), balance.get("總資產", 1))
                    if "營業額" in income and "總資產" in balance else None
                ),
                inventory_turnover=(
                    get_ratio(income.get("營業額", 0), balance.get("存貨", 1))
                    if "營業額" in income and "存貨" in balance else None
                ),
                receivables_turnover=(
                    get_ratio(income.get("營業額", 0), balance.get("應收賬款", 1))
                    if "營業額" in income and "應收賬款" in balance else None
                ),
                days_sales_outstanding=(
                    365 / get_ratio(income.get("營業額", 0), balance.get("應收賬款", 1))
                    if "營業額" in income and "應收賬款" in balance else None
                ),
                operating_cycle=None,  # 港股通常不直接提供
                working_capital_turnover=(
                    get_ratio(income.get("營業額", 0), (balance.get("流動資產", 0) - balance.get("流動負債", 0)))
                    if "營業額" in income else None
                ),

                # 流动性指标
                current_ratio=(
                    get_ratio(balance.get("流動資產", 0), balance.get("流動負債", 1))
                    if "流動資產" in balance and "流動負債" in balance else None
                ),
                quick_ratio=(
                    get_ratio(
                        balance.get("流動資產", 0) - balance.get("存貨", 0),
                        balance.get("流動負債", 1)
                    ) if "流動資產" in balance and "存貨" in balance and "流動負債" in balance else None
                ),
                cash_ratio=(
                    get_ratio(balance.get("現金及等價物", 0), balance.get("流動負債", 1))
                    if "現金及等價物" in balance and "流動負債" in balance else None
                ),
                operating_cash_flow_ratio=(
                    get_ratio(cashflow.get("經營活動現金流量", 0), balance.get("流動負債", 1))
                    if "經營活動現金流量" in cashflow and "流動負債" in balance else None
                ),

                # 杠杆指标
                debt_to_equity=(
                    get_ratio(balance.get("總負債", 0), balance.get("股東資金", 1))
                    if "總負債" in balance and "股東資金" in balance else None
                ),
                debt_to_assets=(
                    get_ratio(balance.get("總負債", 0), balance.get("總資產", 1))
                    if "總負債" in balance and "總資產" in balance else None
                ),
                interest_coverage=(
                    get_ratio(income.get("經營利潤", 0), income.get("財務費用", 1))
                    if "經營利潤" in income and "財務費用" in income else None
                ),

                # 增长指标 (需要与上一期比较)
                revenue_growth=(
                    get_growth(income.get("營業額", 0), prev_data.get("revenue", 0))
                    if "營業額" in income and prev_data else None
                ),
                earnings_growth=(
                    get_growth(income.get("股東應佔盈利", 0), prev_data.get("net_income", 0))
                    if "股東應佔盈利" in income and prev_data else None
                ),
                book_value_growth=(
                    get_growth(balance.get("股東資金", 0), prev_data.get("equity", 0))
                    if "股東資金" in balance and prev_data else None
                ),
                earnings_per_share_growth=(
                    get_growth(income.get("每股基本盈利", 0), prev_data.get("earnings_per_share", 0))
                    if "每股基本盈利" in income and prev_data else None
                ),
                free_cash_flow_growth=(
                    get_growth(cashflow.get("自由現金流", 0), prev_data.get("free_cash_flow", 0))
                    if "自由現金流" in cashflow and prev_data else None
                ),
                operating_income_growth=(
                    get_growth(income.get("經營利潤", 0), prev_data.get("operating_income", 0))
                    if "經營利潤" in income and prev_data else None
                ),
                ebitda_growth=(
                    get_growth(income.get("EBITDA", 0), prev_data.get("ebitda", 0))
                    if "EBITDA" in income and prev_data else None
                ),

                # 派息指标
                payout_ratio=(
                    get_ratio(income.get("股息支出", 0), income.get("股東應佔盈利", 1))
                    if "股息支出" in income and "股東應佔盈利" in income else None
                ),

                # 每股指标
                earnings_per_share=income.get(field_map["earnings_per_share"], None),
                book_value_per_share=balance.get("每股賬面資產淨值", None),
                free_cash_flow_per_share=(
                    cashflow.get("自由現金流", 0) / income.get("已發行普通股數量", 1)
                    if "自由現金流" in cashflow and "已發行普通股數量" in income else None
                )
            )

            # 存储当前数据用于下一期增长计算
            prev_data = {
                "revenue": income.get("營業額", 0),
                "net_income": income.get("股東應佔盈利", 0),
                "equity": balance.get("股東資金", 0),
                "earnings_per_share": income.get("每股基本盈利", 0),
                "free_cash_flow": cashflow.get("自由現金流", 0),
                "operating_income": income.get("經營利潤", 0),
                "ebitda": income.get("EBITDA", 0)
            }

            metrics_list.append(metric)

        return sorted(metrics_list, key=lambda x: x.report_period, reverse=True)[:4]  # 返回最近4期

    except Exception as e:
        print(f"获取{ticker}财务数据失败: {str(e)}")
        return []


def get_growth(current: float, previous: float) -> Optional[float]:
    """计算增长率"""
    if previous == 0:
        return None
    return (current - previous) / previous * 100


def get_ratio(numerator: float, denominator: float) -> Optional[float]:
    """安全计算比率"""
    if denominator == 0:
        return None
    return numerator / denominator

def search_line_items(
    ticker: str,
    line_items: list[str],
    end_date: str,
    period: str = "ttm",
    limit: int = 10,
) -> list[LineItem]:
    """Fetch line items from API."""
    # If not in cache or insufficient data, fetch from API
    headers = {}
    if api_key := os.environ.get("FINANCIAL_DATASETS_API_KEY"):
        headers["X-API-KEY"] = api_key

    url = "https://api.financialdatasets.ai/financials/search/line-items"

    body = {
        "tickers": [ticker],
        "line_items": line_items,
        "end_date": end_date,
        "period": period,
        "limit": limit,
    }
    response = requests.post(url, headers=headers, json=body)
    if response.status_code != 200:
        raise Exception(f"Error fetching data: {ticker} - {response.status_code} - {response.text}")
    data = response.json()
    response_model = LineItemResponse(**data)
    search_results = response_model.search_results
    if not search_results:
        return []

    # Cache the results
    return search_results[:limit]


def get_insider_trades(
    ticker: str,
    end_date: str,
    start_date: str | None = None,
    limit: int = 1000,
) -> list[InsiderTrade]:
    """Fetch insider trades from cache or API."""
    # Create a cache key that includes all parameters to ensure exact matches
    cache_key = f"{ticker}_{start_date or 'none'}_{end_date}_{limit}"
    
    # Check cache first - simple exact match
    if cached_data := _cache.get_insider_trades(cache_key):
        return [InsiderTrade(**trade) for trade in cached_data]

    # If not in cache, fetch from API
    headers = {}
    if api_key := os.environ.get("FINANCIAL_DATASETS_API_KEY"):
        headers["X-API-KEY"] = api_key

    all_trades = []
    current_end_date = end_date

    while True:
        url = f"https://api.financialdatasets.ai/insider-trades/?ticker={ticker}&filing_date_lte={current_end_date}"
        if start_date:
            url += f"&filing_date_gte={start_date}"
        url += f"&limit={limit}"

        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            raise Exception(f"Error fetching data: {ticker} - {response.status_code} - {response.text}")

        data = response.json()
        response_model = InsiderTradeResponse(**data)
        insider_trades = response_model.insider_trades

        if not insider_trades:
            break

        all_trades.extend(insider_trades)

        # Only continue pagination if we have a start_date and got a full page
        if not start_date or len(insider_trades) < limit:
            break

        # Update end_date to the oldest filing date from current batch for next iteration
        current_end_date = min(trade.filing_date for trade in insider_trades).split("T")[0]

        # If we've reached or passed the start_date, we can stop
        if current_end_date <= start_date:
            break

    if not all_trades:
        return []

    # Cache the results using the comprehensive cache key
    _cache.set_insider_trades(cache_key, [trade.model_dump() for trade in all_trades])
    return all_trades


def get_company_news(
    ticker: str,
    end_date: str,
    start_date: str | None = None,
    limit: int = 1000,
) -> list[CompanyNews]:
    """Fetch company news from cache or API."""
    # Create a cache key that includes all parameters to ensure exact matches
    cache_key = f"{ticker}_{start_date or 'none'}_{end_date}_{limit}"
    
    # Check cache first - simple exact match
    if cached_data := _cache.get_company_news(cache_key):
        return [CompanyNews(**news) for news in cached_data]

    # If not in cache, fetch from API
    headers = {}
    if api_key := os.environ.get("FINANCIAL_DATASETS_API_KEY"):
        headers["X-API-KEY"] = api_key

    all_news = []
    current_end_date = end_date

    while True:
        url = f"https://api.financialdatasets.ai/news/?ticker={ticker}&end_date={current_end_date}"
        if start_date:
            url += f"&start_date={start_date}"
        url += f"&limit={limit}"

        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            raise Exception(f"Error fetching data: {ticker} - {response.status_code} - {response.text}")

        data = response.json()
        response_model = CompanyNewsResponse(**data)
        company_news = response_model.news

        if not company_news:
            break

        all_news.extend(company_news)

        # Only continue pagination if we have a start_date and got a full page
        if not start_date or len(company_news) < limit:
            break

        # Update end_date to the oldest date from current batch for next iteration
        current_end_date = min(news.date for news in company_news).split("T")[0]

        # If we've reached or passed the start_date, we can stop
        if current_end_date <= start_date:
            break

    if not all_news:
        return []

    # Cache the results using the comprehensive cache key
    _cache.set_company_news(cache_key, [news.model_dump() for news in all_news])
    return all_news


def get_market_cap(
    ticker: str,
    end_date: str,
) -> float | None:
    """Fetch market cap from the API."""
    # Check if end_date is today
    if end_date == datetime.datetime.now().strftime("%Y-%m-%d"):
        # Get the market cap from company facts API
        headers = {}
        if api_key := os.environ.get("FINANCIAL_DATASETS_API_KEY"):
            headers["X-API-KEY"] = api_key

        url = f"https://api.financialdatasets.ai/company/facts/?ticker={ticker}"
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            print(f"Error fetching company facts: {ticker} - {response.status_code}")
            return None

        data = response.json()
        response_model = CompanyFactsResponse(**data)
        return response_model.company_facts.market_cap

    financial_metrics = get_financial_metrics(ticker, end_date)
    if not financial_metrics:
        return None

    market_cap = financial_metrics[0].market_cap

    if not market_cap:
        return None

    return market_cap


def prices_to_df(prices: list[Price]) -> pd.DataFrame:
    """Convert prices to a DataFrame."""
    df = pd.DataFrame([p.model_dump() for p in prices])
    df["Date"] = pd.to_datetime(df["time"])
    df.set_index("Date", inplace=True)
    numeric_cols = ["open", "close", "high", "low", "volume"]
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df.sort_index(inplace=True)
    return df


# Update the get_price_data function to use the new functions
def get_price_data(ticker: str, start_date: str, end_date: str) -> pd.DataFrame:
    prices = get_prices(ticker, start_date, end_date)
    return prices_to_df(prices)
