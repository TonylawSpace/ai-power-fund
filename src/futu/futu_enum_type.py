from enum import Enum,IntEnum,auto
from typing import Optional, Union

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

# 股票状态
class SecurityStatus(IntEnum):
    """
    证券状态枚举类，包含各种证券交易状态及其相关信息
    """
    NONE = 0
    NORMAL = 1
    LISTING = 2
    PURCHASING = 3
    SUBSCRIBING = 4
    BEFORE_DRAK_TRADE_OPENING = 5
    DRAK_TRADING = 6
    DRAK_TRADE_END = 7
    TO_BE_OPEN = 8
    SUSPENDED = 9
    CALLED = 10
    EXPIRED_LAST_TRADING_DATE = 11
    EXPIRED = 12
    DELISTED = 13
    CHANGE_TO_TEMPORARY_CODE = 14
    TEMPORARY_CODE_TRADE_END = 15
    CHANGED_PLATE_TRADE_END = 16
    CHANGED_CODE_TRADE_END = 17
    RECOVERABLE_CIRCUIT_BREAKET = 18
    UN_RECOVERABLE_CIRCUIT_BREAKER = 19
    AFTER_COMBINATION = 20
    AFTER_TRANSATION = 21

    # 状态描述映射
    _descriptions = {
        NONE: "未知",
        NORMAL: "正常状态",
        LISTING: "待上市",
        PURCHASING: "申购中",
        SUBSCRIBING: "认购中",
        BEFORE_DRAK_TRADE_OPENING: "暗盘开盘前",
        DRAK_TRADING: "暗盘交易中",
        DRAK_TRADE_END: "暗盘已收盘",
        TO_BE_OPEN: "待开盘",
        SUSPENDED: "停牌",
        CALLED: "已收回",
        EXPIRED_LAST_TRADING_DATE: "已过最后交易日",
        EXPIRED: "已过期",
        DELISTED: "已退市",
        CHANGE_TO_TEMPORARY_CODE: "公司行动中，交易关闭，转至临时代码交易",
        TEMPORARY_CODE_TRADE_END: "临时买卖结束，交易关闭",
        CHANGED_PLATE_TRADE_END: "已转板，旧代码交易关闭",
        CHANGED_CODE_TRADE_END: "已换代码，旧代码交易关闭",
        RECOVERABLE_CIRCUIT_BREAKET: "可恢复性熔断",
        UN_RECOVERABLE_CIRCUIT_BREAKER: "不可恢复性熔断",
        AFTER_COMBINATION: "盘后撮合",
        AFTER_TRANSATION: "盘后交易"
    }

    @property
    def description(self) -> str:
        """获取状态描述"""
        return self._descriptions.get(self, "未知状态")

    @classmethod
    def from_value(cls, value: int) -> Optional["SecurityStatus"]:
        """
        根据值获取对应的证券状态

        Args:
            value: 状态整数值

        Returns:
            对应的 SecurityStatus 枚举值，如果未找到则返回 None
        """
        try:
            return cls(value)
        except ValueError:
            return NONE

# 窝轮类型枚举类 WrtType
class WrtType(IntEnum):
    """
    窝轮类型枚举类，包含各种窝轮的类型及其相关信息
    """
    UNKNOWN = 0
    CALL = 1
    PUT = 2
    BULL = 3
    BEAR = 4
    INLINE = 5

    # 类型描述映射
    _descriptions = {
        UNKNOWN: "未知",
        CALL: "认购窝轮",
        PUT: "认沽窝轮",
        BULL: "牛证",
        BEAR: "熊证",
        INLINE: "界内证"
    }

    @property
    def description(self) -> str:
        """获取窝轮类型的中文描述"""
        return self._descriptions.get(self, "未知类型")

    @classmethod
    def from_value(cls, value: int) -> Optional["WrtType"]:
        """
        根据整数值获取对应的窝轮类型枚举值

        Args:
            value: 窝轮类型的整数值

        Returns:
            对应的 WrtType 枚举值，若未找到则返回 None
        """
        try:
            return cls(value)
        except ValueError:
            return None

# 窝轮价内/外状态枚举类
class PriceType(IntEnum):
    """
    窝轮价内/外状态枚举类，用于表示窝轮价格与标的资产价格的相对关系
    """
    UNKNOW = 0
    OUTSIDE = 1
    WITH_IN = 2

    # 状态描述映射（包含窝轮和界内证的不同含义）
    _descriptions = {
        UNKNOW: "未知",
        OUTSIDE: {
            "warrant": "价外",
            "inline": "界外（界内证专用）"
        },
        WITH_IN: {
            "warrant": "价内",
            "inline": "界内（界内证专用）"
        }
    }

    @property
    def description(self) -> str:
        """获取状态的中文描述（默认返回窝轮场景的描述）"""
        return self._descriptions[self]["warrant"]

    def get_description(self, wrt_type: str = "warrant") -> str:
        """
        获取指定窝轮类型的状态描述

        Args:
            wrt_type: 窝轮类型，可选 "warrant"（普通窝轮）或 "inline"（界内证）

        Returns:
            对应的中文描述，若类型不支持则返回默认描述
        """
        return self._descriptions[self].get(wrt_type, self.description)

    @classmethod
    def from_value(cls, value: int) -> Optional["PriceType"]:
        """
        根据整数值获取对应的价格状态枚举值

        Args:
            value: 价格状态的整数值

        Returns:
            对应的 PriceType 枚举值，若未找到则返回 None
        """
        try:
            return cls(value)
        except ValueError:
            return None

# 期权方向类型枚举类 OptionType
class OptionType(IntEnum):
    """
    期权方向类型枚举类，用于表示期权的看涨/看跌属性及全量类型
    """
    ALL = 0
    CALL = 1
    PUT = 2

    # 类型描述映射
    _descriptions = {
        ALL: "所有期权",
        CALL: "看涨期权（赋予买入标的资产的权利）",
        CALL: "看涨期权（赋予买入标的资产的权利）",  # 修正重复键（实际应确保唯一）
        PUT: "看跌期权（赋予卖出标的资产的权利）"
    }

    @property
    def description(self) -> str:
        """获取期权类型的中文描述"""
        return self._descriptions.get(self, "未知类型")

    @classmethod
    def from_value(cls, value: int) -> Optional["OptionType"]:
        """
        根据整数值获取对应的期权类型枚举值

        Args:
            value: 期权类型的整数值

        Returns:
            对应的 OptionType 枚举值，若未找到则返回 None
        """
        try:
            return cls(value)
        except ValueError:
            return None

# 指数期权类型 IndexOptionType
class IndexOptionType(IntEnum):
    """指数期权类型"""
    NONE = 0  # 未知类型
    NORMAL = 1  # 普通的指数期权
    SMALL = 2  # 小型指数期权

# 期权行权类型（按行权时间分类） OptionAreaType
class OptionAreaType(IntEnum):
    """期权行权类型（按行权时间分类）"""
    NONE = 0  # 未知类型
    AMERICAN = 1  # 美式期权：行权时间为到期日前任意时间
    EUROPEAN = 2  # 欧式期权：行权时间为到期日当天
    BERMUDA = 3  # 百慕大期权：行权时间为到期日前的一系列特定日期

# 资产类别
class AssetClass(IntEnum):
    """资产类别"""
    UNKNOW = 0  # 未知资产类别
    STOCK = 1  # 股票
    BOND = 2  # 债券
    COMMODITY = 3  # 商品
    CURRENCY_MARKET = 4  # 货币市场
    FUTURE = 5  # 期货
    SWAP = 6  # 掉期（互换）