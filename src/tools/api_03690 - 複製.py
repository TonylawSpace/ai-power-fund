# api_03690.py
import os
import sys
from dotenv import load_dotenv
import pandas as pd
from typing import List
from src.data.models import FinancialMetrics
from src.tools.financial_mapping_03690 import (
    STANDARD_MAPPING,
    METRICS_CALCULATION,
    REPORT_PERIOD_MAPPING,
    CURRENCY_MAPPING
)
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 获取环境变量
load_dotenv()

# 全局配置 - 使用基于脚本目录的路径
DATA_SET_DIR = os.getenv("DATA_SET_DIR", "./DataSet")
# logger.info(f"数据集目录: {DATA_SET_DIR}")

def load_excel(file_path: str, sheet_name: str) -> pd.DataFrame:
    """
    读取Excel文件并返回处理后的DataFrame

    参数:
        file_path: Excel文件路径
        sheet_name: 工作表名称

    返回:
        处理后的pandas DataFrame
    """
    try:
        # logger.info(f"Load Excel File: {file_path} - Sheet Name: {sheet_name}")

        # 读取Excel文件
        df = pd.read_excel(file_path, sheet_name=sheet_name, header=0)
        # 转换日期列名
        date_cols = []
        for col in df.columns[1:]:
            original_col = col  # 保存原始列名
            dt = convert_to_datetime(col)
            if not pd.isna(dt):
                date_cols.append(dt)
                # logger.info(f"成功转换: {original_col} -> {dt}")
            else:
                date_cols.append(col)
                logger.debug(f"转换失败: {original_col}")

        # date_cols
        logger.info(f"date_cols: {date_cols}")

        # 清理数据
        df = (
            df.dropna(how='all')  # 删除全空行
            .rename(columns={df.columns[0]: 'item'})  # 设置第一列为项目名称
            .replace(['--', 'N/A', '',' '], pd.NA)  # 处理特殊值
        )
        # 添加调试信息
        logger.info(f"原始列名: {df.columns.tolist()}")

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

    if not date_columns:
        logger.warning("日期轉換失敗，未找到日期列，检查Excel格式")
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


def calculate_derived_metrics(period_data: dict) -> dict:
    """
    根据原始财务数据计算衍生指标

    返回:
        dict: {指标名称: 计算值}
    """
    metrics = {}

    shares_outstanding = 6_280_000_000  # 流通股数 美团2023年总股本约62.8亿股

    try:
        # 1. 基本比率
        # 毛利率
        if all(k in period_data for k in ('gross_profit', 'revenue')) and period_data['revenue'] != 0:
            metrics['gross_margin'] = (period_data['gross_profit'] / period_data['revenue']) * 100

        # 净利润率
        if all(k in period_data for k in ('profit_attributable', 'revenue')) and period_data['revenue'] != 0:
            metrics['net_margin'] = (period_data['profit_attributable'] / period_data['revenue']) * 100

        # 营业利润率
        if all(k in period_data for k in ('operating_profit', 'revenue')) and period_data['revenue'] != 0:
            metrics['operating_margin'] = (period_data['operating_profit'] / period_data['revenue']) * 100

        # 2. 流动性比率
        # 流动比率
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

        # 4. 盈利能力比率
        # 总资产收益率(ROA)
        if all(k in period_data for k in ('profit_attributable', 'total_assets')) and period_data['total_assets'] != 0:
            metrics['return_on_assets'] = (period_data['profit_attributable'] / period_data['total_assets']) * 100

        # 净资产收益率(ROE)
        if all(k in period_data for k in ('profit_attributable', 'total_equity')) and period_data['total_equity'] != 0:
            metrics['return_on_equity'] = (period_data['profit_attributable'] / period_data['total_equity']) * 100

        # 5. 现金流比率
        # 经营活动现金流比率
        if all(k in period_data for k in ('net_cash_operating', 'total_current_liabilities')) and period_data[
            'total_current_liabilities'] != 0:
            metrics['operating_cash_flow_ratio'] = period_data['net_cash_operating'] / period_data[
                'total_current_liabilities']

        # 自由现金流
        if all(k in period_data for k in ('net_cash_operating', 'fixed_assets_acquisition')):
            metrics['free_cash_flow'] = period_data['net_cash_operating'] - period_data['fixed_assets_acquisition']

        # 6. 每股指标
        # 每股账面价值
        if 'shareholders_equity' in period_data:
            metrics['book_value_per_share'] = period_data['shareholders_equity'] / shares_outstanding

        # 每股收益(EPS)
        if 'profit_attributable' in period_data:
            metrics['earnings_per_share'] = period_data['profit_attributable'] / shares_outstanding

    except (KeyError, TypeError, ZeroDivisionError) as e:
        logger.warning(f"计算衍生指标时出错: {str(e)}")
    except Exception as e:
        logger.error(f"计算衍生指标时发生意外错误: {str(e)}", exc_info=True)

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


def get_financial_metrics_meituan(ticker: str = "03690.HK") -> List[FinancialMetrics]:
    """从本地Excel文件获取美团(03690.HK)的完整财务指标"""
    # 创建ticker特定的数据目录
    ticker_data_dir = f"{DATA_SET_DIR}\\{ticker}"
    # logger.info(f"股票数据目录: {ticker_data_dir}")
    print("=" * 80)
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

    sheet_name = ticker.removesuffix(".HK")

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
            calculated_metrics = calculate_derived_metrics(period_data)

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
    # 添加详细日志输出
    logger.setLevel(logging.DEBUG)
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    print("=" * 80)
    # 如果原始数据为非数字，导致结算结果就是非数字 表示为 NAN
    print("开始获取美团财务指标...（如果原始数据为非数字，表示为 NAN）")
    print("=" * 80)

    try:
        metrics = get_financial_metrics_meituan("03690.HK")

        if not metrics:
            print("\n [func::__main__] 未获取到财务数据，请检查文件路径和数据")
            sys.exit(1)

        # 只打印最近两个报告期的数据
        for i, metric in enumerate(metrics[:2]):
            print(f"\n{'=' * 80}")
            print(f"报告期 {i + 1}: {metric.period} ({metric.report_period})")
            print(f"{'=' * 80}")

            # 打印关键指标
            print("\n关键财务指标:")
            print(
                f"总收入: {metric.revenue:,.0f} {metric.currency}" if metric.revenue is not None else "总收入: NAN")
            print(
                f"毛利润: {metric.gross_profit:,.0f} {metric.currency}" if metric.gross_profit is not None else "毛利润: NAN")
            print(
                f"净利润: {metric.profit_attributable:,.0f} {metric.currency}" if metric.profit_attributable is not None else "净利润: NAN")
            print(
                f"总资产: {metric.total_assets:,.0f} {metric.currency}" if metric.total_assets is not None else "总资产: NAN")
            print(
                f"总负债: {metric.total_liabilities:,.0f} {metric.currency}" if metric.total_liabilities is not None else "总负债: NAN")
            print(
                f"股东权益: {metric.shareholders_equity:,.0f} {metric.currency}" if metric.shareholders_equity is not None else "股东权益: NAN")

            print("\n盈利能力指标:")
            print(f"毛利率: {metric.gross_margin:.2f}%" if metric.gross_margin is not None else "毛利率: NAN")
            print(f"净利润率: {metric.net_margin:.2f}%" if metric.net_margin is not None else "净利润率: NAN")
            print(f"ROE: {metric.return_on_equity:.2f}%" if metric.return_on_equity is not None else "ROE: NAN")
            print(f"ROA: {metric.return_on_assets:.2f}%" if metric.return_on_assets is not None else "ROA: NAN")

            print("\n流动性指标:")
            print(f"流动比率: {metric.current_ratio:.2f}" if metric.current_ratio is not None else "流动比率: NAN")
            print(f"速动比率: {metric.quick_ratio:.2f}" if metric.quick_ratio is not None else "速动比率: NAN")

            print("\n杠杆指标:")
            print(
                f"资产负债率: {metric.debt_to_assets:.2%}" if metric.debt_to_assets is not None else "资产负债率: NAN")
            print(f"产权比率: {metric.debt_to_equity:.2f}" if metric.debt_to_equity is not None else "产权比率: NAN")

            print("\n每股指标:")
            print(
                f"每股收益 (EPS): {metric.earnings_per_share:.2f} {metric.currency}" if metric.earnings_per_share is not None else "每股收益: NAN")
            print(
                f"每股账面价值: {metric.book_value_per_share:.2f} {metric.currency}" if metric.book_value_per_share is not None else "每股账面价值: NAN")

            print(f"\n{'=' * 80}\n")

        print("=" * 80)
        print("财务指标获取完成")
        print("=" * 80)

    except Exception as e:
        logger.error(f"主程序运行时出错: {str(e)}", exc_info=True)
        sys.exit(1)