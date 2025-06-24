from pydantic import BaseModel


class Price(BaseModel):
    open: float
    close: float
    high: float
    low: float
    volume: int
    time: str


class PriceResponse(BaseModel):
    ticker: str
    prices: list[Price]


class FinancialMetricsHK(BaseModel):
    """
    财务指标模型，包含公司财务分析常用的各项指标
    """
    asset_turnover: float | None  # 1.资产周转率
    book_value_growth: float |  None  # 2.账面价值增长率
    book_value_per_share: float |  None  # 3.每股账面价值
    cash_ratio: float |  None  # 4.现金比率
    current_ratio: float |  None  # 5.流动比率
    currency: str  # 6.货币单位
    days_sales_outstanding: float |  None  # 7.应收账款周转天数
    debt_to_assets: float |  None  # 8.资产负债率
    debt_to_equity: float |  None  # 9.产权比率

    # dividend_yield: float |  None  # 10.股息率 不是放在这个模型

    earnings_growth: float |  None  # 11.利润增长率
    earnings_per_share: float |  None  # 12.每股收益(EPS)
    earnings_per_share_growth: float |  None  # 13.每股收益增长率
    ebitda_growth: float |  None  # 14.EBITDA增长率
    enterprise_value: float |  None  # 15.企业价值
    enterprise_value_to_ebitda_ratio: float | None  # 16.企业价值/EBITDA
    enterprise_value_to_revenue_ratio: float |  None  # 17.企业价值/营收
    free_cash_flow: float |  None  # 18.自由现金流
    free_cash_flow_growth: float |  None  # 19.自由现金流增长率
    free_cash_flow_per_share: float |  None  # 20.每股自由现金流
    free_cash_flow_yield: float |  None  # 21.自由现金流收益率
    gross_margin: float |  None  # 22.毛利率
    interest_coverage: float |  None  # 23.利息保障倍数
    inventory_turnover: float |  None  # 24.存货周转率
    operating_cash_flow: float |  None  # 25.经营活动现金流
    operating_cash_flow_ratio: float |  None  # 26.经营活动现金流比率
    operating_cycle: float |  None  # 27.营业周期
    operating_income_growth: float |  None  # 28.营业利润增长率
    operating_margin: float |  None  # 29.营业利润率
    # payout_ratio: float |  None  # 30.股息支付率 不是放在这个模型
    peg_ratio: float |  None  # 31.市盈率相对盈利增长比率
    period: str  # 32.周期
    price_to_book_ratio: float |  None  # 33.市净率
    price_to_earnings_ratio: float |  None  # 34.市盈率
    price_to_sales_ratio: float |  None  # 35.市销率 市销率（Price-to-Sales Ratio，简称 P/S 或 PSR） 是评估企业估值的重要财务指标，常用于衡量股价与销售额之间的关系。
    quick_ratio: float |  None  # 36.速动比率
    receivables_turnover: float | None  # 37.应收账款周转率
    report_period: str  # 38.报告期
    revenue_growth: float | None  # 39.营收增长率
    return_on_assets: float | None  # 40.总资产收益率(ROA)
    return_on_equity: float | None  # 41.净资产收益率(ROE)
    return_on_invested_capital: float | None  # 42.投入资本回报率(RIC)
    ticker: str  # 43.股票代码
    working_capital_turnover: float | None  # 45.营运资本周转率
    market_cap: float | None  # 46.市值
    net_margin: float | None  # 47.净利润率

class FinancialMetrics(BaseModel):
    ticker: str
    report_period: str
    period: str
    currency: str
    market_cap: float | None
    enterprise_value: float | None
    price_to_earnings_ratio: float | None
    price_to_book_ratio: float | None
    price_to_sales_ratio: float | None
    enterprise_value_to_ebitda_ratio: float | None
    enterprise_value_to_revenue_ratio: float | None
    free_cash_flow_yield: float | None
    peg_ratio: float | None
    gross_margin: float | None
    operating_margin: float | None
    net_margin: float | None
    return_on_equity: float | None
    return_on_assets: float | None
    return_on_invested_capital: float | None
    asset_turnover: float | None
    inventory_turnover: float | None
    receivables_turnover: float | None
    days_sales_outstanding: float | None
    operating_cycle: float | None
    working_capital_turnover: float | None
    current_ratio: float | None
    quick_ratio: float | None
    cash_ratio: float | None
    operating_cash_flow_ratio: float | None
    debt_to_equity: float | None
    debt_to_assets: float | None
    interest_coverage: float | None
    revenue_growth: float | None
    earnings_growth: float | None
    book_value_growth: float | None
    earnings_per_share_growth: float | None
    free_cash_flow_growth: float | None
    operating_income_growth: float | None
    ebitda_growth: float | None
    payout_ratio: float | None
    earnings_per_share: float | None
    book_value_per_share: float | None
    free_cash_flow_per_share: float | None

class FinancialMetricsResponse(BaseModel):
    financial_metrics: list[FinancialMetrics]


class LineItem(BaseModel):
    ticker: str
    report_period: str
    period: str
    currency: str

    # Allow additional fields dynamically
    model_config = {"extra": "allow"}


class LineItemResponse(BaseModel):
    search_results: list[LineItem]


class InsiderTrade(BaseModel):
    ticker: str
    issuer: str | None
    name: str | None
    title: str | None
    is_board_director: bool | None
    transaction_date: str | None
    transaction_shares: float | None
    transaction_price_per_share: float | None
    transaction_value: float | None
    shares_owned_before_transaction: float | None
    shares_owned_after_transaction: float | None
    security_title: str | None
    filing_date: str


class InsiderTradeResponse(BaseModel):
    insider_trades: list[InsiderTrade]


class CompanyNews(BaseModel):
    ticker: str
    title: str
    author: str
    source: str
    date: str
    url: str
    sentiment: str | None = None


class CompanyNewsResponse(BaseModel):
    news: list[CompanyNews]


class CompanyFacts(BaseModel):
    ticker: str
    name: str
    cik: str | None = None
    industry: str | None = None
    sector: str | None = None
    category: str | None = None
    exchange: str | None = None
    is_active: bool | None = None
    listing_date: str | None = None
    location: str | None = None
    market_cap: float | None = None
    number_of_employees: int | None = None
    sec_filings_url: str | None = None
    sic_code: str | None = None
    sic_industry: str | None = None
    sic_sector: str | None = None
    website_url: str | None = None
    weighted_average_shares: int | None = None


class CompanyFactsResponse(BaseModel):
    company_facts: CompanyFacts


class Position(BaseModel):
    cash: float = 0.0
    shares: int = 0
    ticker: str


class Portfolio(BaseModel):
    positions: dict[str, Position]  # ticker -> Position mapping
    total_cash: float = 0.0


class AnalystSignal(BaseModel):
    signal: str | None = None
    confidence: float | None = None
    reasoning: dict | str | None = None
    max_position_size: float | None = None  # For risk management signals


class TickerAnalysis(BaseModel):
    ticker: str
    analyst_signals: dict[str, AnalystSignal]  # agent_name -> signal mapping


class AgentStateData(BaseModel):
    tickers: list[str]
    portfolio: Portfolio
    start_date: str
    end_date: str
    ticker_analyses: dict[str, TickerAnalysis]  # ticker -> analysis mapping


class AgentStateMetadata(BaseModel):
    show_reasoning: bool = False
    model_config = {"extra": "allow"}
