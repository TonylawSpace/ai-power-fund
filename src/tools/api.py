from dotenv import load_dotenv
from futu import *
from src.futu.futu_enum_type import (
    CltRiskLevel,
    Currency,
    TrailType,
    ModifyOrderOp,
    OrderStatus,
    OrderType,
    PositionSide,
    TrdAccType,
    TrdEnv,
    TrdMarket,
    FinaType)


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

# 富途连接配置（从.env读取）
FUTU_OPEND_HOST = os.getenv("FUTU_OPEND_HOST", "127.0.0.1")
FUTU_OPEND_PORT = int(os.getenv("FUTU_OPEND_PORT", "11111"))  # 默认值11111
FUTU_MARKET = TrdMarket.HK  # 港股市场


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


def get_financial_metrics(ticker: str) -> list[FinancialMetrics]:
    """
    使用富途官方API获取港股财务指标

    参数:
        ticker: 港股代码 (如 "00700.HK" 或 "00700")

    返回:
        按报告期倒序排列的财务指标列表
    """
    # 标准化股票代码格式
    if not ticker.endswith(".HK"):
        ticker += ".HK"
    pure_code = ticker.split(".")[0]
    stock_code = f"HK.{pure_code}"

    metrics_list = []
    quote_ctx = OpenQuoteContext(host=FUTU_OPEND_HOST, port=FUTU_OPEND_PORT)

    try:
        # ==================== 1. 获取基本信息和实时估值 ====================
        # 获取股票快照
        ret, snapshot = quote_ctx.get_market_snapshot([stock_code])
        if ret != RET_OK:
            print(f"获取市场快照失败: {snapshot}")
            return []

        snapshot_data = snapshot.iloc[0] if not snapshot.empty else {}

        # 获取股票静态信息
        ret, static_info = quote_ctx.get_stock_basicinfo(market=FUTU_MARKET, code_list=[pure_code])
        if ret != RET_OK:
            print(f"获取基本信息失败: {static_info}")
            return []

        static_data = static_info.iloc[0] if not static_info.empty else {}

        # ==================== 2. 获取财务报表数据 ====================
        # 获取年报数据
        ret, annual_reports = quote_ctx.get_stock_financial(
            stock_code=stock_code,
            fina_type=FinaType.ANNUAL,  # 年度报告
            start=0,
            max_count=5  # 获取最近5份年报
        )

        # 获取季报数据
        ret, quarterly_reports = quote_ctx.get_stock_financial(
            stock_code=stock_code,
            fina_type=FinaType.QUARTERLY,  # 季度报告
            start=0,
            max_count=8  # 获取最近8份季报
        )

        # 合并报告数据
        all_reports = pd.concat([annual_reports,
                                 quarterly_reports]) if not annual_reports.empty and not quarterly_reports.empty else annual_reports

        # ==================== 3. 处理财务报告并计算指标 ====================
        for _, report in all_reports.iterrows():
            # 确定报告类型
            report_type = "annual" if report['fina_type'] == FinaType.ANNUAL else "quarterly"
            report_date = report['report_date']

            # 计算财务比率
            ratios = calculate_financial_ratios(report)

            # 创建财务指标对象
            metric = FinancialMetrics(
                ticker=ticker,
                report_period=report_date.strftime("%Y-%m-%d"),
                period=report_type,
                currency="HKD",

                # 估值指标 (从快照获取最新值)
                market_cap=snapshot_data.get('market_val', None),
                price_to_earnings_ratio=snapshot_data.get('pe_ratio', None),
                price_to_book_ratio=snapshot_data.get('pb_ratio', None),
                price_to_sales_ratio=snapshot_data.get('ps_ratio', None),
                dividend_yield=snapshot_data.get('dividend_ratio', None),

                # 盈利能力指标
                gross_margin=ratios.get('gross_profit_margin', None),
                operating_margin=ratios.get('operating_profit_margin', None),
                net_margin=ratios.get('net_profit_margin', None),
                return_on_equity=ratios.get('roe', None),
                return_on_assets=ratios.get('roa', None),

                # 流动性指标
                current_ratio=ratios.get('current_ratio', None),
                quick_ratio=ratios.get('quick_ratio', None),

                # 杠杆指标
                debt_to_equity=ratios.get('debt_to_equity', None),
                debt_to_assets=ratios.get('debt_to_assets', None),

                # 每股指标
                earnings_per_share=report.get('basic_eps', None),
                book_value_per_share=report.get('nav_per_share', None),

                # 其他指标
                payout_ratio=ratios.get('dividend_payout_ratio', None),

                # 富途特有指标
                enterprise_value=static_data.get('total_mv', None),
                free_cash_flow_per_share=report.get('fcf_per_share', None)
            )

            # 添加增长指标 (需要历史数据计算)
            if len(metrics_list) > 0:
                last_metric = metrics_list[0]
                metric.revenue_growth = calculate_growth(report['total_revenue'], last_metric.revenue)
                metric.earnings_growth = calculate_growth(report['net_profit'], last_metric.net_income)

            metrics_list.append(metric)

        # 按报告日期排序 (最新在前)
        metrics_list.sort(key=lambda x: x.report_period, reverse=True)

        return metrics_list

    except Exception as e:
        print(f"富途接口获取{ticker}财务数据失败: {str(e)}")
        return []
    finally:
        # 确保关闭连接
        quote_ctx.close()



def calculate_financial_ratios(report: pd.Series) -> dict[str, float]:
    """根据财务报表计算财务比率"""
    ratios = {}

    try:
        # 利润率计算
        if report['total_revenue'] > 0:
            ratios['gross_profit_margin'] = (report['gross_profit'] / report['total_revenue']) * 100
            ratios['operating_profit_margin'] = (report['operating_profit'] / report['total_revenue']) * 100
            ratios['net_profit_margin'] = (report['net_profit'] / report['total_revenue']) * 100

        # 回报率计算
        if report['total_assets'] > 0:
            ratios['roa'] = (report['net_profit'] / report['total_assets']) * 100
        if report['total_equity'] > 0:
            ratios['roe'] = (report['net_profit'] / report['total_equity']) * 100

        # 流动性比率
        if report['current_liability'] > 0:
            ratios['current_ratio'] = report['current_asset'] / report['current_liability']
            ratios['quick_ratio'] = (report['current_asset'] - report['inventories']) / report['current_liability']

        # 杠杆比率
        if report['total_equity'] > 0:
            ratios['debt_to_equity'] = report['total_liability'] / report['total_equity']
        if report['total_assets'] > 0:
            ratios['debt_to_assets'] = report['total_liability'] / report['total_assets']

        # 股息支付率
        if report['net_profit'] > 0:
            ratios['dividend_payout_ratio'] = (report['dividend_payable'] / report['net_profit']) * 100

    except (ZeroDivisionError, KeyError, TypeError):
        pass

    return ratios


def calculate_growth(current: float, previous: float) -> Optional[float]:
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
