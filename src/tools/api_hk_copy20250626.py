# api_03690.py
import os
import sys
from dotenv import load_dotenv
import pandas as pd
from typing import List
from sqlalchemy.dialects.mysql import DATETIME
from src.data.models import FinancialMetrics
from src.tools.financial_mapping_03690 import (
    STANDARD_MAPPING,
    METRICS_CALCULATION,
    REPORT_PERIOD_MAPPING,
    CURRENCY_MAPPING
)

from src.tools.logger import logger
from src.futu.futu_market import FutuMarket # futu api

# 获取环境变量
load_dotenv()

# 全局配置 - 使用基于脚本目录的路径
DATA_SET_DIR = os.getenv("DATA_SET_DIR", "./DataSet")
logger.info(f"数据集目录: {DATA_SET_DIR}")

def load_excel(file_path: str, sheet_name: str) -> pd.DataFrame:
    try:
        # 读取Excel文件
        df = pd.read_excel(file_path, sheet_name=sheet_name, header=0)

        # 转换日期列名
        date_cols = []
        for col in df.columns[1:]:
            original_col = col
            dt = convert_to_datetime(col)
            if not pd.isna(dt):
                date_cols.append(dt)
            else:
                date_cols.append(col)
                logger.debug(f"转换失败: {original_col}")

        # ==== 关键修复：将转换后的列名应用到 DataFrame ====
        # 创建新的列名列表（第一列保持不变）
        new_columns = [df.columns[0]] + date_cols
        df.columns = new_columns  # 更新DataFrame的列名

        # 清理数据
        df = (
            df.dropna(how='all')
            .rename(columns={df.columns[0]: 'item'})  # 确保第一列名为'item'
            .replace(['--', 'N/A', '', ' '], pd.NA)
        )

        logger.info(f"处理后列名: {df.columns.tolist()}")
        logger.info(f"成功加载数据: {df.shape[0]} 行, {df.shape[1]} 列")
        return df

    except Exception as e:
        logger.error(f"[Exception]加载Excel失败: {str(e)} \n{file_path}", exc_info=True)
        return pd.DataFrame()

# 轉換日期
def convert_to_datetime(date_str):
    """将各种日期格式转换为统一的datetime对象"""
    try:
        # 尝试常见日期格式
        formats = [
            "%Y-%m-%d", "%Y/%m/%d", "%Y%m%d",
            "%Y年%m月%d日", "%d/%m/%Y", "%m/%d/%Y",
            "%Y.%m.%d", "%d-%b-%y", "%d-%b-%Y",
            "%b %d, %Y", "%B %d, %Y"
        ]

        # 尝试去除时间部分（如果有）
        if isinstance(date_str, str):
            date_str = date_str.split()[0]  # 取日期部分

            # 处理中文日期
            date_str = date_str.replace("年", "-").replace("月", "-").replace("日", "")

            # 处理特殊格式
            if "季度" in date_str:
                year, quarter = date_str.split("年")
                quarter = quarter.replace("季度", "").strip()
                month = {"一": "03", "二": "06", "三": "09", "四": "12"}.get(quarter, "01")
                date_str = f"{year}-{month}-01"

        for fmt in formats:
            try:
                return pd.to_datetime(date_str, format=fmt, errors="raise")
            except:
                continue

        # 作为最后手段尝试自动解析
        return pd.to_datetime(date_str, errors="coerce")
    except:
        return pd.NaT

def merge_financial_statements(
        balance_sheet: pd.DataFrame,
        income_statement: pd.DataFrame,
        cash_flow: pd.DataFrame
) -> dict:
    """
    合并三大财务报表数据，按报告期组织

    返回:
        dict: {报告日期: {财务指标: 值}}
    """
    financials_dict = {}

    # 获取所有报告日期（从资产负债表获取）
    date_columns = [col for col in balance_sheet.columns if isinstance(col, pd.Timestamp)]

    # 添加详细的列类型信息
    column_types = [(col, type(col)) for col in balance_sheet.columns]
    logger.info(f"资产负债表列名及类型: {column_types}")

    if not date_columns:
        # 列出所有列名帮助调试
        logger.warning(f"日期转换失败，列名: {balance_sheet.columns.tolist()}")
        logger.warning(f"日期转换失败，列类型: {[type(col) for col in balance_sheet.columns]}")
        return financials_dict


    for date_col in date_columns:
        # 统一使用日期字符串作为键
        report_date = date_col.strftime('%Y-%m-%d')
        period_data = {}

        # 处理资产负债表
        for _, row in balance_sheet.iterrows():
            item = row['item']
            value = row[date_col]
            if pd.notna(value) and item in STANDARD_MAPPING["balance_sheet"]:
                eng_name = STANDARD_MAPPING["balance_sheet"][item]
                period_data[eng_name] = float(value)

        # 处理利润表
        for _, row in income_statement.iterrows():
            item = row['item']
            value = row[date_col]
            if pd.notna(value) and item in STANDARD_MAPPING["income_statement"]:
                eng_name = STANDARD_MAPPING["income_statement"][item]
                period_data[eng_name] = float(value)

        # 处理现金流量表
        for _, row in cash_flow.iterrows():
            item = row['item']
            value = row[date_col]
            if pd.notna(value) and item in STANDARD_MAPPING["cash_flow"]:
                eng_name = STANDARD_MAPPING["cash_flow"][item]
                period_data[eng_name] = float(value)

        financials_dict[report_date] = period_data

    logger.info(f"Merged {len(financials_dict)} 个报告期的财务数据")
    return financials_dict


def calculate_derived_metrics(ticker: str,period_data: dict) -> dict:
    """
    根据原始财务数据计算衍生指标

    返回:
        dict: {指标名称: 计算值}
    """
    metrics = {}

    try:
        stock_code_list = [ticker]
        market_snapshot_list = FutuMarket.get_market_snapshot(stock_code_list)
        market_snapshot_model = market_snapshot_list[0]

        # 0. metrics['ticker'] = period_data['ticker']
        total_market_val = market_snapshot_model.total_market_val # 总市值
        shares_outstanding = market_snapshot_model.outstanding_shares # 6_280_000_000  # 美团2023年总股本约62.8亿股

        # 1. 基本比率
        # 毛利率
        if all(k in period_data for k in ('gross_profit', 'revenue')) and period_data['revenue'] != 0:
            metrics['gross_margin'] = (period_data['gross_profit'] / period_data['revenue']) * 100

        # 2、book_value_growth 账面价值增长 目前没有可计算

        # 3.每股账面价值  book_value_per_share 目前没有可计算

        # 净利润率 net_margin
        if all(k in period_data for k in ('profit_attributable', 'revenue')) and period_data['revenue'] != 0:
            metrics['net_margin'] = (period_data['profit_attributable'] / period_data['revenue']) * 100

        # 29.营业利润率 operating_margin
        if all(k in period_data for k in ('operating_profit', 'revenue')) and period_data['revenue'] != 0:
            metrics['operating_margin'] = (period_data['operating_profit'] / period_data['revenue']) * 100

        # 2. 流动性比率
        # 5.流动比率
        if all(k in period_data for k in ('total_current_assets', 'total_current_liabilities')) and period_data[
            'total_current_liabilities'] != 0:
            metrics['current_ratio'] = period_data['total_current_assets'] / period_data['total_current_liabilities']

        # 速动比率
        if all(k in period_data for k in ('cash_equivalents', 'accounts_receivable', 'total_current_liabilities')) and \
                period_data['total_current_liabilities'] != 0:
            quick_assets = period_data['cash_equivalents'] + period_data['accounts_receivable']
            metrics['quick_ratio'] = quick_assets / period_data['total_current_liabilities']

        # 现金比率
        if all(k in period_data for k in ('cash_equivalents', 'total_current_liabilities')) and period_data[
            'total_current_liabilities'] != 0:
            metrics['cash_ratio'] = period_data['cash_equivalents'] / period_data['total_current_liabilities']

        # 3. 杠杆比率
        # 资产负债率
        if all(k in period_data for k in ('total_liabilities', 'total_assets')) and period_data['total_assets'] != 0:
            metrics['debt_to_assets'] = period_data['total_liabilities'] / period_data['total_assets']

        # 产权比率
        if all(k in period_data for k in ('total_liabilities', 'total_equity')) and period_data['total_equity'] != 0:
            metrics['debt_to_equity'] = period_data['total_liabilities'] / period_data['total_equity']

        # 利息保障倍数
        if all(k in period_data for k in ('operating_profit', 'financing_costs')) and period_data[
            'financing_costs'] != 0:
            metrics['interest_coverage'] = period_data['operating_profit'] / period_data['financing_costs']

        # 4. 盈利能力比率
        # 总资产收益率(ROA)
        if all(k in period_data for k in ('profit_attributable', 'total_assets')) and period_data['total_assets'] != 0:
            metrics['return_on_assets'] = (period_data['profit_attributable'] / period_data['total_assets']) * 100

        # 净资产收益率(ROE)
        if all(k in period_data for k in ('profit_attributable', 'total_equity')) and period_data['total_equity'] != 0:
            metrics['return_on_equity'] = (period_data['profit_attributable'] / period_data['total_equity']) * 100

        # 投入资本回报率(ROI)
        if all(k in period_data for k in ('operating_profit', 'total_equity', 'total_liabilities')) and (
                period_data['total_equity'] + period_data['total_liabilities']) != 0:
            # 简化计算：ROI = EBIT / (总负债 + 股东权益)
            metrics['return_on_invested_capital'] = period_data['operating_profit'] / (
                        period_data['total_liabilities'] + period_data['total_equity'])

        # 5. 效率比率
        # 资产周转率
        if all(k in period_data for k in ('revenue', 'total_assets')) and period_data['total_assets'] != 0:
            metrics['asset_turnover'] = period_data['revenue'] / period_data['total_assets']

        # 存货周转率
        if all(k in period_data for k in ('cost_of_sales', 'inventory')) and period_data['inventory'] != 0:
            metrics['inventory_turnover'] = period_data['cost_of_sales'] / period_data['inventory']

        # 应收账款周转率
        if all(k in period_data for k in ('revenue', 'accounts_receivable')) and period_data[
            'accounts_receivable'] != 0:
            metrics['receivables_turnover'] = period_data['revenue'] / period_data['accounts_receivable']

        # 应收账款周转天数
        if 'receivables_turnover' in metrics and metrics['receivables_turnover'] != 0:
            metrics['days_sales_outstanding'] = 365 / metrics['receivables_turnover']

        # 6. 现金流比率
        # 经营活动现金流比率
        if all(k in period_data for k in ('net_cash_operating', 'total_current_liabilities')) and period_data[
            'total_current_liabilities'] != 0:
            metrics['operating_cash_flow_ratio'] = period_data['net_cash_operating'] / period_data[
                'total_current_liabilities']

        # 自由现金流 - 确保总是存在
        metrics['free_cash_flow'] = None
        if all(k in period_data for k in ('net_cash_operating', 'fixed_assets_acquisition')):
            try:
                metrics['free_cash_flow'] = float(period_data['net_cash_operating']) - float(
                    period_data['fixed_assets_acquisition'])
            except (TypeError, ValueError):
                pass

        # 7. 每股指标
        # 每股账面价值
        if 'shareholders_equity' in period_data:
            metrics['book_value_per_share'] = period_data['shareholders_equity'] / shares_outstanding

        # 每股收益(EPS)
        if 'profit_attributable' in period_data:
            metrics['earnings_per_share'] = period_data['profit_attributable'] / shares_outstanding

        # 每股自由现金流
        metrics['free_cash_flow_per_share'] = None
        if metrics['free_cash_flow'] is not None and shares_outstanding != 0:
            metrics['free_cash_flow_per_share'] = metrics['free_cash_flow'] / shares_outstanding

        # 8. 其他指标
        # 自由现金流收益率
        if 'free_cash_flow' in metrics and 'market_cap' in period_data and period_data['market_cap'] != 0:
            metrics['free_cash_flow_yield'] = metrics['free_cash_flow'] / period_data['market_cap']

        metrics['last_price'] = market_snapshot_model.last_price  # 最新价格
        metrics['open_price'] = market_snapshot_model.open_price  # 今日开盘价
        metrics['high_price'] = market_snapshot_model.high_price  # 最高价格
        metrics['low_price'] = market_snapshot_model.low_price  # 最低价格
        metrics['prev_close_price'] = market_snapshot_model.prev_close_price  # 昨收盘价格

        # 映射表没有的指标-------------------------------------------------------------------------------
        """
        book_value_growth
        earnings_growth
        earnings_per_share_growth
        ebitda_growth
        enterprise_value
        enterprise_value_to_ebitda_ratio
        enterprise_value_to_revenue_ratio
        free_cash_flow_growth
        free_cash_flow_yield
        operating_cash_flow
        operating_cycle
        operating_income_growth
        peg_ratio
        price_to_book_ratio
        price_to_earnings_ratio
        price_to_sales_ratio
        revenue_growth
        working_capital_turnover
        market_cap
        """
        metrics['book_value_growth']=None
        metrics['earnings_growth'] = None
        metrics['earnings_per_share_growth']=None
        metrics['ebitda_growth']=None
        metrics['enterprise_value']=None
        metrics['enterprise_value_to_ebitda_ratio']=None
        metrics['enterprise_value_to_revenue_ratio']=None
        metrics['free_cash_flow_growth']=None
        metrics['free_cash_flow_yield']=None
        metrics['operating_cash_flow']=None
        metrics['operating_cycle']=None
        metrics['operating_income_growth']=None
        metrics['peg_ratio']=None # pb_ratio
        metrics['payout_ratio']=None
        metrics['price_to_book_ratio']=None
        metrics['price_to_earnings_ratio']= market_snapshot_model.pe_ratio
        metrics['price_to_sales_ratio']=None
        metrics['revenue_growth']=None
        metrics['working_capital_turnover']=None
        metrics['market_cap']= total_market_val

        print(f"{market_snapshot_model.update_time} Ticker: {ticker} Market_Capital: { total_market_val} ")

        # 9. 确保所有模型字段都存在
        """
        required_fields = [
            'book_value_growth', 'earnings_growth', 'earnings_per_share_growth',
            'ebitda_growth', 'enterprise_value', 'enterprise_value_to_ebitda_ratio',
            'enterprise_value_to_revenue_ratio', 'free_cash_flow_growth',
            'operating_cash_flow', 'operating_cycle', 'operating_income_growth',
            'peg_ratio', 'price_to_book_ratio', 'price_to_earnings_ratio',
            'price_to_sales_ratio', 'revenue_growth', 'working_capital_turnover',
            'market_cap'
        ]

        for field in required_fields:
            metrics.setdefault(field, None)
        """

    except (KeyError, TypeError, ZeroDivisionError) as e1:
        logger.warning(f"计算衍生指标时出错: {str(e1)}")
    except Exception as e2:
        logger.error(f"计算衍生指标时发生意外错误: {str(e2)}", exc_info=True)

    return metrics

def get_report_period(date_str: str) -> str:
    """
    根据日期字符串确定报告期类型

    参数:
        date_str: 日期字符串 (格式: YYYY-MM-DD)

    返回:
        str: 报告期类型 (annual, interim, quarterly)
    """
    for suffix, period_type in REPORT_PERIOD_MAPPING.items():
        if date_str.endswith(suffix):
            return period_type
    return "other"

def get_financial_metrics_hk(ticker: str = "HK.03690") -> List[FinancialMetrics]:
    """从本地Excel文件获取美团(HK.03690)的完整财务指标"""
    # 创建ticker特定的数据目录
    ticker_data_dir = f"{DATA_SET_DIR}\\{ticker}"
    # logger.info(f"股票数据目录: {ticker_data_dir}")
    print("=" * 90)
    print("\n")

    # 构建文件路径
    balance_sheet_path = f"{ticker_data_dir}\\{ticker}_balance_sheet.xlsx"  # os.path.join(ticker_data_dir, f"{ticker}_balance_sheet.xlsx")
    income_statement_path =  f"{ticker_data_dir}\\{ticker}_income_statement.xlsx"
    cash_flow_path = f"{ticker_data_dir}\\{ticker}_cash_flow.xlsx"  # os.path.join(ticker_data_dir, f"{ticker}_cash_flow.xlsx")

    logger.info(f"资产负债表路径: {balance_sheet_path}")
    logger.info(f"利润表路径: {income_statement_path}")
    logger.info(f"现金流量表路径: {cash_flow_path}")

    # 检查文件是否存在
    for path in [balance_sheet_path, income_statement_path, cash_flow_path]:
        if not os.path.exists(path):
            logger.error(f"文件不存在: {path}")
            # 列出目录内容帮助调试
            if os.path.exists(ticker_data_dir):
                logger.info(f"目录内容: {os.listdir(ticker_data_dir)}")
            else:
                logger.error(f"目录不存在: {ticker_data_dir}")
            return []

    # 表名 移除前后缀 .HK
    sheet_name = ticker.removesuffix(".HK")
    sheet_name = ticker.removeprefix("HK.")
    try:
        # 加载三大财务报表
        balance_sheet = load_excel(balance_sheet_path, sheet_name=sheet_name)
        income_statement = load_excel(income_statement_path, sheet_name=sheet_name)
        cash_flow = load_excel(cash_flow_path, sheet_name=sheet_name)

        # 将三大报表合并为按报告期组织的财务数据字典
        financials_dict = merge_financial_statements(
            balance_sheet,
            income_statement,
            cash_flow
        )

        if not financials_dict:
            logger.warning(f"未找到有效的财务数据: {ticker} (financials_dict=none merge exception)")
            return []

        metrics_list = []

        # 处理每个报告期
        for period_date, period_data in financials_dict.items():
            # 计算衍生指标
            calculated_metrics = calculate_derived_metrics(ticker,period_data)

            # 创建FinancialMetrics对象
            metrics = FinancialMetrics(
                ticker=ticker,
                period=period_date,
                report_period=get_report_period(period_date),
                currency=CURRENCY_MAPPING,
                **period_data,
                **calculated_metrics
            )
            metrics_list.append(metrics)

        # 按报告日期倒序排列
        metrics_list.sort(key=lambda x: x.period, reverse=True)

        logger.info(f"成功加载 {len(metrics_list)} 个报告期的财务数据")
        return metrics_list

    except Exception as e:
        logger.error(f"处理财务数据时出错: {str(e)}", exc_info=True)
        return []

# 其他函数保持不变...

# 使用示例
if __name__ == "__main__":

    logger.info("=" * 90)
    # 如果原始数据为非数字，导致结算结果就是非数字 表示为 NAN
    logger.info("开始获取美团财务指标...（如果原始数据为非数字，表示为 NAN）")
    logger.info("=" * 90)

    ticker = "HK.03690"

    try:
        metrics = get_financial_metrics_hk(ticker)
        print("[BEGIN] FinancialMetrics","=" * 100,"\n")
        print(metrics)
        print("[END] FinancialMetrics", "=" * 100,"\n")

        if not metrics:
            print("\n [func::__main__] 未获取到财务数据，请检查文件路径和数据")
            sys.exit(1)

        # 只打印最近两个报告期的数据
        for i, metric in enumerate(metrics):
            print(f"\n{'=' * 90}")

            print(f"{'=' * 90}")

            # 打印关键指标
            print("\n关键财务指标:")
            print( f"报告日期: {metric.report_period}" )
            print("\n盈利能力指标:")
            print(f"毛利率: {metric.gross_margin:.2f}%" if metric.gross_margin is not None else "毛利率: NAN")
            print(f"净利润率: {metric.net_margin:.2f}%" if metric.net_margin is not None else "净利润率: NAN")
            print(f"ROE: {metric.return_on_equity:.2f}%" if metric.return_on_equity is not None else "ROE: NAN")
            print(f"ROA: {metric.return_on_assets:.2f}%" if metric.return_on_assets is not None else "ROA: NAN")

            print("\n流动性指标:")
            print(f"流动比率: {metric.current_ratio:.2f}" if metric.current_ratio is not None else "流动比率: NAN")
            print(f"速动比率: {metric.quick_ratio:.2f}" if metric.quick_ratio is not None else "速动比率: NAN")

            print(f"\n{'=' * 90}\n")

        print("=" * 90)
        print("财务指标获取完成")
        print("=" * 90)

    except Exception as e:
        logger.error(f"主程序运行时出错: {str(e)}", exc_info=True)
        sys.exit(1)