from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Union
from src.futu.futu_enum_type import (
 IndexOptionType    # 指数期权类别
,OptionAreaType     # 期权类型（按行权时间）
,AssetClass         # 资产类别
,WrtType            # 窝轮类型
,PriceType          # 窝轮价内/外
,SecurityStatus     # 股票状态
,OptionType         # 期权类型（按方向）

)

@dataclass
class MarketSnapShotModel:
    """市场快照数据模型，表示金融产品的实时市场数据"""
    
    # 基础信息
    code: str  # 股票代码
    name: str  # 股票名称
    update_time: str  # 当前价更新时间
    
    # 价格信息
    last_price: float  # 最新价格
    open_price: float  # 今日开盘价
    high_price: float  # 最高价格
    low_price: float  # 最低价格
    prev_close_price: float  # 昨收盘价格
    
    # 交易信息
    volume: int  # 成交数量
    turnover: float  # 成交金额
    turnover_rate: float  # 换手率
    suspension: bool  # 是否停牌
    listing_date: str  # 上市日期
    
    # 股票特有信息
    equity_valid: bool  # 是否正股
    issued_shares: int  # 总股本
    total_market_val: float  # 总市值
    net_asset: int  # 资产净值
    net_profit: int  # 净利润
    earning_per_share: float  # 每股盈利
    outstanding_shares: int  # 流通股本
    net_asset_per_share: float  # 每股净资产
    circular_market_val: float  # 流通市值
    ey_ratio: float  # 收益率
    pe_ratio: float  # 市盈率
    pb_ratio: float  # 市净率
    pe_ttm_ratio: float  # 市盈率TTM
    dividend_ttm: float  # 股息TTM，派息
    dividend_ratio_ttm: float  # 股息率TTM
    dividend_lfy: float  # 股息LFY，上一年度派息
    dividend_lfy_ratio: float  # 股息率LFY
    
    # 窝轮特有信息
    stock_owner: str  # 窝轮所属正股的代码或期权的标的股代码
    wrt_valid: bool  # 是否是窝轮
    wrt_conversion_ratio: float  # 换股比率
    wrt_type: WrtType  # 窝轮类型
    wrt_strike_price: float  # 行使价格
    wrt_maturity_date: str  # 格式化窝轮到期时间
    wrt_end_trade: str  # 格式化窝轮最后交易时间
    wrt_leverage: float  # 杠杆比率
    wrt_ipop: float  # 价内/价外
    wrt_break_even_point: float  # 打和点
    wrt_conversion_price: float  # 换股价
    wrt_price_recovery_ratio: float  # 正股距收回价
    wrt_score: float  # 窝轮综合评分
    wrt_code: str  # 窝轮对应的正股（此字段已废除，修改为stock_owner）
    wrt_recovery_price: float  # 窝轮收回价
    wrt_street_vol: float  # 窝轮街货量
    wrt_issue_vol: float  # 窝轮发行量
    wrt_street_ratio: float  # 窝轮街货占比
    wrt_delta: float  # 窝轮对冲值
    wrt_implied_volatility: float  # 窝轮引伸波幅
    wrt_premium: float  # 窝轮溢价
    wrt_upper_strike_price: float  # 上限价
    wrt_lower_strike_price: float  # 下限价
    wrt_inline_price_status: PriceType  # 界内界外
    wrt_issuer_code: str  # 发行人代码
    
    # 期权特有信息
    option_valid: bool  # 是否是期权
    option_type: OptionType  # 期权类型
    strike_time: str  # 期权行权日
    option_strike_price: float  # 行权价
    option_contract_size: float  # 每份合约数
    option_open_interest: int  # 总未平仓合约数
    option_implied_volatility: float  # 隐含波动率
    option_premium: float  # 溢价
    option_delta: float  # 希腊值Delta
    option_gamma: float  # 希腊值Gamma
    option_vega: float  # 希腊值Vega
    option_theta: float  # 希腊值Theta
    option_rho: float  # 希腊值Rho
    index_option_type: IndexOptionType  # 指数期权类型
    option_net_open_interest: int  # 净未平仓合约数
    option_expiry_date_distance: int  # 距离到期日天数
    option_contract_nominal_value: float  # 合约名义金额
    option_owner_lot_multiplier: float  # 相等正股手数
    option_area_type: OptionAreaType  # 期权类型（按行权时间）
    option_contract_multiplier: float  # 合约乘数
    
    # 板块信息
    plate_valid: bool  # 是否为板块类型
    plate_raise_count: int  # 板块类型上涨支数
    plate_fall_count: int  # 板块类型下跌支数
    plate_equal_count: int  # 板块类型平盘支数
    
    # 指数信息
    index_valid: bool  # 是否有指数类型
    index_raise_count: int  # 指数类型上涨支数
    index_fall_count: int  # 指数类型下跌支数
    index_equal_count: int  # 指数类型平盘支数
    
    # 交易单位信息
    lot_size: int  # 每手股数，股票期权表示每份合约的股数，期货表示合约乘数
    
    # 摆盘信息
    price_spread: float  # 当前向上的摆盘价差
    ask_price: float  # 卖价
    bid_price: float  # 买价
    ask_vol: float  # 卖量
    bid_vol: float  # 买量
    
    # 融资融券信息（已废弃）
    enable_margin: bool  # 是否可融资（已废弃）
    mortgage_ratio: float  # 股票抵押率（已废弃）
    long_margin_initial_ratio: float  # 融资初始保证金率（已废弃）
    enable_short_sell: bool  # 是否可卖空（已废弃）
    short_sell_rate: float  # 卖空参考利率（已废弃）
    short_available_volume: int  # 剩余可卖空数量（已废弃）
    short_margin_initial_ratio: float  # 卖空（融券）初始保证金率（已废弃）
    
    # 股票状态
    sec_status: SecurityStatus  # 股票状态
    
    # 其他价格指标
    amplitude: float  # 振幅
    avg_price: float  # 平均价
    bid_ask_ratio: float  # 委比
    volume_ratio: float  # 量比
    highest52weeks_price: float  # 52周最高价
    lowest52weeks_price: float  # 52周最低价
    highest_history_price: float  # 历史最高价
    lowest_history_price: float  # 历史最低价
    
    # 盘前数据
    pre_price: float  # 盘前价格
    pre_high_price: float  # 盘前最高价
    pre_low_price: float  # 盘前最低价
    pre_volume: int  # 盘前成交量
    pre_turnover: float  # 盘前成交额
    pre_change_val: float  # 盘前涨跌额
    pre_change_rate: float  # 盘前涨跌幅
    pre_amplitude: float  # 盘前振幅
    
    # 盘后数据
    after_price: float  # 盘后价格
    after_high_price: float  # 盘后最高价
    after_low_price: float  # 盘后最低价
    after_volume: int  # 盘后成交量
    after_turnover: float  # 盘后成交额
    after_change_val: float  # 盘后涨跌额
    after_change_rate: float  # 盘后涨跌幅
    after_amplitude: float  # 盘后振幅
    
    # 夜盘数据
    overnight_price: float  # 夜盘价格
    overnight_high_price: float  # 夜盘最高价
    overnight_low_price: float  # 夜盘最低价
    overnight_volume: int  # 夜盘成交量
    overnight_turnover: float  # 夜盘成交额
    overnight_change_val: float  # 夜盘涨跌额
    overnight_change_rate: float  # 夜盘涨跌幅
    overnight_amplitude: float  # 夜盘振幅
    
    # 期货特有信息
    future_valid: bool  # 是否期货
    future_last_settle_price: float  # 昨结
    future_position: float  # 持仓量
    future_position_change: float  # 日增仓
    future_main_contract: bool  # 是否主连合约
    future_last_trade_time: str  # 最后交易时间
    
    # 基金特有信息
    trust_valid: bool  # 是否基金
    trust_dividend_yield: float  # 股息率
    trust_aum: float  # 资产规模
    trust_outstanding_units: int  # 总发行量
    trust_netAssetValue: float  # 单位净值
    trust_premium: float  # 溢价
    trust_assetClass: AssetClass  # 资产类别    