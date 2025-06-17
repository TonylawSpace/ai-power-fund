# Financial Metrics 財務指標



## class FinancialMetrics

```
class FinancialMetrics(BaseModel):
    """
    财务指标模型，包含公司财务分析常用的各项指标
    """
    asset_turnover: float | None  # 1.资产周转率 = 营业收入/平均资产总额
    
    book_value_growth: float |  None  # 2.账面价值增长率
    book_value_per_share: float |  None  # 3.每股账面价值
    
    cash_ratio: float |  None  # 4.现金比率
    current_ratio: float |  None  # 5.流动比率
    currency: str  # 6.货币单位
    
    days_sales_outstanding: float |  None  # 7.应收账款周转天数
    debt_to_assets: float |  None  # 8.资产负债率
    debt_to_equity: float |  None  # 9.产权比率
    dividend_yield: float |  None  # 10.股息率
    
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
    
    operating_cash_flow: float |  None  # 25.经营活动产生的现金流量
    operating_cash_flow_ratio: float |  None  # 26.经营活动现金流比率
    operating_cycle: float |  None  # 27.营业周期
    operating_income_growth: float |  None  # 28.营业利润增长率
    operating_margin: float |  None  # 29.营业利润率
    
    payout_ratio: float |  None  # 30.股息支付率
    peg_ratio: float |  None  # 31.市盈率相对盈利增长比率
    period: str  # 32.周期
    price_to_book_ratio: float |  None  # 33.市净率
    price_to_earnings_ratio: float |  None  # 34.市盈率
    price_to_sales_ratio: float |  None  # 35.市销率（Price-to-Sales Ratio，简称 P/S 或 PSR） 是评估企业估值的重要财务指标
    quick_ratio: float |  None  # 36.速动比率
    
    receivables_turnover: float | None  # 37.应收账款周转率
    report_period: str  # 38.报告期
    revenue_growth: float | None  # 39.营收增长率
    return_on_assets: float | None  # 40.总资产收益率(ROA)
    return_on_equity: float | None  # 41.净资产收益率(ROE)
    return_on_invested_capital: float | None  # 42.投入资本回报率(ROIC)
    ticker: str  # 43.股票代码
    
    market_cap: float | None  # 46.市值
    net_margin: float | None  # 47.净利润率
    operating_cash_flow: float | None  # 48.经营活动现金流

    return_on_assets: float | None  # 49.资产回报率
    return_on_equity: float | None  # 50.权益回报率
    revenue_growth: float | None  # 51.营收增长率
    
    working_capital_turnover: float | None  # 45.营运资本周转率

```

## TurnOver Rate 周转率 

周转率 = 时期内周转总量 ÷ 平均资源持有量

在财务与商业领域，"TurnOver" 通常指**资源的周转效率**，具体分类如下：

| 术语               | 英文全称                     | 核心公式                       | 应用场景                     |
| ------------------ | ---------------------------- | ------------------------------ | ---------------------------- |
| **资产周转率**     | Asset Turnover               | 营业收入 / 平均资产总额        | 评估企业整体资产运营效率     |
| **存货周转率**     | Inventory Turnover           | 销售成本 / 平均存货            | 衡量库存管理水平             |
| **应收账款周转率** | Accounts Receivable Turnover | 赊销收入 / 平均应收账款        | 评估信用政策与回款能力       |
| **员工离职率**     | Employee Turnover Rate       | 离职员工数 / 平均员工数 × 100% | 人力资源稳定性分析           |
| **固定资产周转率** | Fixed Asset Turnover         | 营业收入 / 平均固定资产净值    | 重资产行业（如制造业）效率评 |

## ROE 净收益

**Return on Equity (ROE)** 是一个重要的财务指标，用于衡量公司对股东权益的回报能力。它表示公司在一定时期内（通常为一年）从股东投资中获得的净收益。

### 计算公式

$$
$\text{ROE} = \frac{\text{净利润}}{\text{股东权益}} \times 100\%$
$$

### 含义

- **高 ROE**：通常表示公司有效地利用股东的投资来产生利润，可能意味着公司经营良好。
- **低 ROE**：可能表明公司未能有效利用股东资金，或者面临盈利能力下降的问题。

### 使用场景

- ROE 常被投资者用来比较不同公司的盈利效率，尤其是在同一行业内。
- 它也可以帮助评估公司的财务健康状况和管理层的表现。



## ROA 資產報酬率

**Return on Assets (ROA)** 是一个衡量公司资产使用效率的财务指标。它表示公司在一定时期内（通常为一年）从其总资产中获得的净收益。

### 计算公式

$$
$\text{ROA} = \frac{\text{净利润}}{\text{总资产}} \times 100\% $
$$

### 含义

- **高 ROA**：表示公司有效地利用资产来产生利润，通常意味着公司的经营效率较高。
- **低 ROA**：可能表明公司在资产使用上效率不足，或者存在盈利能力下降的问题。

### 使用场景

- ROA 常被投资者用来评估公司的资产管理能力，尤其在比较不同公司的资产利用效率时。
- 它可以帮助判断一家公司在其资产基础上创造收益的能力。

### 注意事项

- ROA 可能受到公司资本结构和行业特性的影响，不同行业的 ROA 基准差异较大，因此在行业内比较更为有效。