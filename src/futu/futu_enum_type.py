from enum import Enum

"""
用法
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
"""
# 风控状态
class CltRiskLevel(Enum):
    UNKNOWN = -1  # 未知
    SAFE = 0      # 安全
    WARNING = 1   # 预警
    DANGER = 2    # 危险
    ABSOLUTE_SAFE = 3  # 绝对安全
    OPT_DANGER = 4  # 危险（期权相关）

# 货币类型
class Currency(Enum):
    UNKNOWN = 0   # 未知货币
    HKD = 1       # 港元
    USD = 2       # 美元
    CNH = 3       # 离岸人民币
    JPY = 4       # 日元
    SGD = 5       # 新元
    AUD = 6       # 澳元
    CAD = 7       # 加拿大元
    MYR = 8       # 马来西亚林吉特

# 跟踪类型
class TrailType(Enum):
    UNKNOWN = 0   # 未知类型
    RATIO = 1     # 比例
    AMOUNT = 2    # 金额

# 修改订单操作
class ModifyOrderOp(Enum):
    UNKNOWN = 0   # 未知操作
    NORMAL = 1    # 修改订单
    CANCEL = 2    # 撤单
    DISABLE = 3   # 使失效
    ENABLE = 4    # 使生效
    DELETE = 5    # 删除

# 订单状态
class OrderStatus(Enum):
    UNKNOWN = -1  # 未知状态
    WAITING_SUBMIT = 1  # 待提交
    SUBMITTING = 2      # 提交中
    SUBMITTED = 5       # 已提交
    FILLED_PART = 10    # 部分成交
    FILLED_ALL = 11     # 全部已成交
    CANCELLED_PART = 14  # 部分成交已撤单
    CANCELLED_ALL = 15   # 全部撤单
    FAILED = 21         # 下单失败
    DISABLED = 22       # 已失效
    DELETED = 23        # 已删除

# 订单类型
class OrderType(Enum):
    UNKNOWN = 0          # 未知类型
    NORMAL = 1           # 限价单
    MARKET = 2           # 市价单
    ABSOLUTE_LIMIT = 5   # 绝对限价订单
    AUCTION = 6          # 竞价市价单
    AUCTION_LIMIT = 7    # 竞价限价单
    SPECIAL_LIMIT = 8    # 特别限价单
    STOP = 10            # 止损市价单
    STOP_LIMIT = 11      # 止损限价单

# 持仓方向
class PositionSide(Enum):
    LONG = 0          # 多仓
    UNKNOWN = -1      # 未知方向
    SHORT = 1         # 空仓

# 账户类型
class TrdAccType(Enum):
    UNKNOWN = 0       # 未知类型
    CASH = 1          # 现金账户
    MARGIN = 2        # 保证金账户

# 交易环境
class TrdEnv(Enum):
    SIMULATE = 0      # 模拟环境
    REAL = 1          # 真实环境

# 交易市场
class TrdMarket(Enum):
    UNKNOWN = 0       # 未知市场
    HK = 1            # 香港市场
    US = 2            # 美国市场
    CN = 3            # A 股市场
    FUTURES = 5       # 期货市场

# 财务报告类型常量
# 实际源码中的定义（简化版）
class FinaType(Enum):
    """财务报告类型"""
    ANNUAL = 0      # 年报
    QUARTER_1 = 1   # 第一季度报
    QUARTER_2 = 2   # 中期报告（半年报）
    QUARTER_3 = 3   # 第三季度报
    QUARTER_4 = 4   # 年报（同ANNUAL，但富途内部区分）
    REPORT_TYPE_1 = 5  # 第一季度报（同上）
    REPORT_TYPE_2 = 6  # 中期报告
    REPORT_TYPE_3 = 7  # 第三季度报
    REPORT_TYPE_4 = 8  # 年报

# 证劵类型
class SecurityType(Enum):
    UNKNOWN = 0          # 未知类型
    STOCK = 1            # 股票
    BOND = 2             # 债券
    FUND = 3             # 基金
    OPTION = 4           # 期权
    FUTURE = 5           # 期货
    ETF = 6              # 交易所交易基金
    WARRANT = 7          # 权证
    OTHER = 8            # 其他类型


# 所属交易所
class ExchType(Enum):
    UNKNOWN = 0                 # 未知
    HK_MAINBOARD = 1            # 港交所·主板
    HK_GEMBOARD = 2             # 港交所·创业板
    HK_HKEX = 3                  # 港交所
    US_NYSE = 4                  # 纽交所
    US_NASDAQ = 5                # 纳斯达克
    US_PINK = 6                  # OTC市场
    US_AMEX = 7                  # 美交所
    US_OPTION = 8                # 美国（仅美股期权适用）
    US_NYMEX = 9                 # NYMEX
    US_COMEX = 10                # COMEX
    US_CBOT = 11                 # CBOT
    US_CME = 12                  # CME
    US_CBOE = 13                 # CBOE
    CN_SH = 14                   # 上交所
    CN_SZ = 15                   # 深交所
    CN_STIB = 16                 # 科创板
    SG_SGX = 17                  # 新交所
    JP_OSE = 18                  # 大阪交易所