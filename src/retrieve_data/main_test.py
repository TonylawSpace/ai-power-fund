import akshare as ak
import pandas as pd
from datetime import datetime
from typing import List, Optional

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

from src.data.cache import get_cache

def get_financial_metrics(ticker: str) -> List[FinancialMetrics]:
    """
    获取港股财务指标 (使用AKShare可靠接口)

    参数:
        ticker: 港股代码 (如 "00700.HK")

    返回:
        按时间倒序排列的财务指标列表
    """
    # 确保代码格式正确
    if not ticker.endswith(".HK"):
        ticker += ".HK"
    pure_code = ticker.split(".")[0]  # 提取纯数字代码

    try:
        # 方法1: 使用港股财务报告摘要接口
        df_financial = ak.stock_financial_abstract_hk(symbol=pure_code)

        # 方法2: 如果方法1失败，使用新浪财经接口
        if df_financial.empty:
            df_financial = ak.stock_financial_report_sina(stock=ticker, symbol="balancesheet")

        # 方法3: 如果前两种方法都失败，使用腾讯财经接口
        if df_financial.empty:
            df_financial = ak.stock_financial_analysis_indicator(stock=ticker)

        # 如果所有方法都失败，返回空列表
        if df_financial.empty:
            print(f"无法获取 {ticker} 的财务数据")
            return []

        # 获取市场数据
        quote_df = ak.stock_hk_spot()
        market_data = quote_df[quote_df["symbol"] == ticker].iloc[0] if not quote_df.empty and ticker in quote_df[
            "symbol"].values else {}

        metrics_list = []

        # 遍历财务数据
        for _, row in df_financial.iterrows():
            # 尝试解析报告日期
            report_date = row.get("报告日期", "")
            if not report_date:
                continue

            try:
                # 转换为标准日期格式
                report_date = datetime.strptime(report_date, "%Y-%m-%d").strftime("%Y-%m-%d")
            except:
                report_date = report_date[:10]  # 取前10个字符作为日期

            # 创建财务指标对象
            metric = FinancialMetrics(
                ticker=ticker,
                report_period=report_date,
                period=row.get("报告期类型", "annual"),
                currency="HKD",

                # 估值指标
                market_cap=market_data.get("总市值", None),
                price_to_earnings_ratio=row.get("市盈率", None),
                price_to_book_ratio=row.get("市净率", None),

                # 利润率指标
                gross_margin=row.get("毛利率", None),
                operating_margin=row.get("营业利润率", None),
                net_margin=row.get("净利率", None),
                return_on_equity=row.get("净资产收益率", None),
                return_on_assets=row.get("总资产收益率", None),

                # 流动性指标
                current_ratio=row.get("流动比率", None),
                quick_ratio=row.get("速动比率", None),

                # 杠杆指标
                debt_to_equity=row.get("负债权益比率", None),
                debt_to_assets=row.get("资产负债率", None),

                # 增长指标
                revenue_growth=row.get("营业收入增长率", None),
                earnings_growth=row.get("净利润增长率", None),

                # 每股指标
                earnings_per_share=row.get("每股收益", None),
                book_value_per_share=row.get("每股净资产", None),

                # 其他指标
                payout_ratio=row.get("股息支付率", None),
                asset_turnover=row.get("总资产周转率", None),
                inventory_turnover=row.get("存货周转率", None)
            )

            # 添加其他可能存在的字段
            for field in FinancialMetrics.__fields__:
                if field not in metric.dict() and field in row:
                    setattr(metric, field, row[field])

            metrics_list.append(metric)

        # 按报告日期排序
        return sorted(metrics_list, key=lambda x: x.report_period, reverse=True)[:4]

    except Exception as e:
        print(f"获取{ticker}财务数据失败: {str(e)}")
        return []


# 测试函数
if __name__ == "__main__":

    # test
    get_roll_yield_bar_df = ak.get_roll_yield_bar(type_method="date", var="RB", start_day="20250602",
                                                  end_day="20250611")
    print(get_roll_yield_bar_df)

    # 测试腾讯控股
    tencent_metrics = get_financial_metrics("00700.HK")
    for metric in tencent_metrics:
        print(f"{metric.report_period}: 市盈率={metric.price_to_earnings_ratio}, ROE={metric.return_on_equity}")

    # 测试美团
    meituan_metrics = get_financial_metrics("03690.HK")
    for metric in meituan_metrics:
        print(f"{metric.report_period}: 营收增长={metric.revenue_growth}%")