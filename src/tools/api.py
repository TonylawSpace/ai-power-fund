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
    使用富途API获取港股财务指标

    参数:
        ticker: 港股代码 (格式: "00700.HK" 或 "00700")

    返回:
        按报告期倒序排列的财务指标列表
    """
    # 标准化股票代码格式为富途要求格式: "HK.00700"
    if not ticker.startswith("HK."):
        if ticker.endswith(".HK"):
            ticker = f"HK.{ticker.split('.')[0]}"
        else:
            ticker = f"HK.{ticker}"

    metrics_list = []
    quote_ctx = OpenQuoteContext(host=FUTU_OPEND_HOST, port=FUTU_OPEND_PORT)

    try:
        # ==================== 1. 获取基本信息和实时估值 ====================
        # 获取市场快照
        ret, snapshot = quote_ctx.get_market_snapshot([ticker])
        if ret != RET_OK:
            print(f"获取市场快照失败: {snapshot}")
            return []
        snapshot_data = snapshot.iloc[0] if not snapshot.empty else {}

        # 获取股票基本信息 - 使用正确的代码格式
        ret, static_info = quote_ctx.get_stock_basicinfo(code_list=[ticker])
        if ret != RET_OK:
            print(f"获取基本信息失败: {static_info}")
            return []
        static_data = static_info.iloc[0] if not static_info.empty else {}

        # ==================== 2. 获取财务报告数据 ====================
        # 获取年报数据
        ret, annual_reports = quote_ctx.get_financial_info(
            stock=ticker,
            financial_type=FinaType.ANNUAL,
            start=0,
            num=5
        )

        # 获取季报数据
        ret, quarterly_reports = quote_ctx.get_financial_info(
            stock=ticker,
            financial_type=FinaType.QUARTER_1,
            start=0,
            num=8
        )

        # 合并报告数据
        all_reports = []
        if annual_reports is not None:
            all_reports.extend(annual_reports.values())
        if quarterly_reports is not None:
            all_reports.extend(quarterly_reports.values())

        # ==================== 3. 处理财务报告并计算指标 ====================
        for report in all_reports:
            # 确定报告类型
            report_type = "annual" if report['financial_type'] == FinancialInfoType.ANNUAL_REPORT else "quarterly"

            # 创建财务指标对象
            metric = FinancialMetrics(
                ticker=ticker,
                report_period=report['report_date'],
                period=report_type,
                currency="HKD",

                # 估值指标
                market_cap=snapshot_data.get('market_val', None),
                enterprise_value=static_data.get('total_mv', None),
                price_to_earnings_ratio=snapshot_data.get('pe', None),
                price_to_book_ratio=snapshot_data.get('pb', None),
                price_to_sales_ratio=snapshot_data.get('ps', None),
                enterprise_value_to_ebitda_ratio=report.get('ev_ebitda', None),
                enterprise_value_to_revenue_ratio=report.get('ev_revenue', None),
                free_cash_flow_yield=report.get('free_cash_flow_yield', None),
                peg_ratio=report.get('peg_ratio', None),

                # 盈利能力指标
                gross_margin=report.get('gross_profit_margin', None),
                operating_margin=report.get('operating_profit_margin', None),
                net_margin=report.get('net_profit_margin', None),
                return_on_equity=report.get('roe', None),
                return_on_assets=report.get('roa', None),
                return_on_invested_capital=report.get('roic', None),

                # 运营效率指标
                asset_turnover=report.get('asset_turnover', None),
                inventory_turnover=report.get('inventory_turnover', None),
                receivables_turnover=report.get('receivables_turnover', None),
                days_sales_outstanding=report.get('days_sales_outstanding', None),
                operating_cycle=report.get('operating_cycle', None),
                working_capital_turnover=report.get('working_capital_turnover', None),

                # 流动性指标
                current_ratio=report.get('current_ratio', None),
                quick_ratio=report.get('quick_ratio', None),
                cash_ratio=report.get('cash_ratio', None),
                operating_cash_flow_ratio=report.get('operating_cash_flow_ratio', None),

                # 杠杆指标
                debt_to_equity=report.get('debt_to_equity_ratio', None),
                debt_to_assets=report.get('debt_asset_ratio', None),
                interest_coverage=report.get('interest_coverage_ratio', None),

                # 增长指标
                revenue_growth=report.get('revenue_growth', None),
                earnings_growth=report.get('net_profit_growth', None),
                book_value_growth=report.get('book_value_growth', None),
                earnings_per_share_growth=report.get('eps_growth', None),
                free_cash_flow_growth=report.get('free_cash_flow_growth', None),
                operating_income_growth=report.get('operating_profit_growth', None),
                ebitda_growth=report.get('ebitda_growth', None),

                # 分红与每股指标
                payout_ratio=report.get('dividend_payout_ratio', None),
                earnings_per_share=report.get('eps', None),
                book_value_per_share=report.get('bps', None),
                free_cash_flow_per_share=report.get('free_cash_flow_per_share', None),

                # 港股特有指标
                dividend_yield=snapshot_data.get('dividend_ratio', None)
            )

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
