
# financial_mapping_hk.py
STANDARD_MAPPING = {
    # 资产负债表映射
    "balance_sheet": {
        "物业厂房及设备": "property_plant_equipment",
        "无形资产": "intangible_assets",
        "递延税项资产": "deferred_tax_assets",
        "预付款项": "prepayments",
        "长期投资": "long_term_investments",
        "其他投资": "other_investments",
        "指定以公允价值记账之金融资产": "financial_assets_fair_value",
        "非流动资产合计": "total_non_current_assets",
        "存货": "inventory",
        "应收帐款": "accounts_receivable",
        "预付款按金及其他应收款": "prepayments_deposits_receivables",
        "短期投资": "short_term_investments",
        "受限制存款及现金": "restricted_cash",
        "现金及等价物": "cash_equivalents",
        "流动资产合计": "total_current_assets",
        "总资产": "total_assets",
        "应付帐款": "accounts_payable",
        "应付票据": "notes_payable",
        "应付税项": "taxes_payable",
        "融资租赁负债(流动)": "lease_liabilities_current",
        "递延收入(流动)": "deferred_revenue_current",
        "其他应付款及应计费用": "accrued_expenses",
        "预收款项": "advances_from_customers",
        "短期贷款": "short_term_loans",
        "流动负债合计": "total_current_liabilities",
        "长期贷款": "long_term_loans",
        "递延税项负债": "deferred_tax_liabilities",
        "融资租赁负债(非流动)": "lease_liabilities_non_current",
        "应付票据(非流动)": "notes_payable_non_current",
        "非流动负债合计": "total_non_current_liabilities",
        "总负债": "total_liabilities",
        "少数股东权益": "minority_interest",
        "净资产": "net_assets",
        "股本": "share_capital",
        "股本溢价": "share_premium",
        "保留溢利(累计亏损)": "retained_earnings",
        "其他储备": "other_reserves",
        "股东权益": "shareholders_equity",
        "总权益": "total_equity"
    },

    # 利润表映射
    "income_statement": {
        "营业额": "revenue",
        "营运收入": "operating_income",
        "销售成本": "cost_of_sales",
        "毛利": "gross_profit",
        "其他收益": "other_income",
        "销售及分销费用": "selling_distribution_expenses",
        "行政开支": "administrative_expenses",
        "减值及拨备": "impairment_provisions",
        "重估盈余": "revaluation_surplus",
        "研发费用": "rd_expenses",
        "经营溢利": "operating_profit",
        "利息收入": "interest_income",
        "融资成本": "financing_costs",
        "溢利其他项目": "other_profit_items",
        "除税前溢利": "profit_before_tax",
        "税项": "tax_expense",
        "持续经营业务税后利润": "profit_after_tax_continuing",
        "除税后溢利": "profit_after_tax",
        "少数股东损益": "minority_interest_income",
        "股东应占溢利": "profit_attributable",
        "每股基本盈利": "basic_eps",
        "每股摊薄盈利": "diluted_eps"
    },

    # 现金流量表映射
    "cash_flow": {
        "经营业务现金净额": "net_cash_operating",
        "投资业务现金净额": "net_cash_investing",
        "融资业务现金净额": "net_cash_financing",
        "现金净额": "net_cash_change",
        "期初现金": "cash_beginning",
        "期间变动其他项目": "other_cash_adjustments",
        "期末现金": "cash_ending",
        "已付税项": "taxes_paid",
        "已收股息(投资)": "dividends_received",
        "处置固定资产": "fixed_assets_disposal",
        "购建固定资产": "fixed_assets_acquisition",
        "购建无形资产及其他资产": "intangible_assets_acquisition",
        "新增借款": "new_borrowings",
        "偿还借款": "loan_repayments",
        "已付股息(融资)": "dividends_paid",
        "发行股份": "share_issuance",
        "回购股份": "share_repurchase",
        "偿还融资租赁": "lease_repayments"
    }
}

# 财务指标计算映射
METRICS_CALCULATION = {

    # 基本比率
    "gross_margin": {
        "formula": "gross_profit / revenue",
        "components": ["gross_profit", "revenue"],
        "source": "income_statement"
    },
    "net_margin": {
        "formula": "profit_attributable / revenue",
        "components": ["profit_attributable", "revenue"],
        "source": "income_statement"
    },
    "operating_margin": {
        "formula": "operating_profit / revenue",
        "components": ["operating_profit", "revenue"],
        "source": "income_statement"
    },

    # 流动性比率
    "current_ratio": {
        "formula": "total_current_assets / total_current_liabilities",
        "components": ["total_current_assets", "total_current_liabilities"],
        "source": "balance_sheet"
    },
    "quick_ratio": {
        "formula": "(cash_equivalents + accounts_receivable) / total_current_liabilities",
        "components": ["cash_equivalents", "accounts_receivable", "total_current_liabilities"],
        "source": "balance_sheet"
    },
    "cash_ratio": {
        "formula": "cash_equivalents / total_current_liabilities",
        "components": ["cash_equivalents", "total_current_liabilities"],
        "source": "balance_sheet"
    },

    # 杠杆比率
    "debt_to_assets": {
        "formula": "total_liabilities / total_assets",
        "components": ["total_liabilities", "total_assets"],
        "source": "balance_sheet"
    },
    "debt_to_equity": {
        "formula": "total_liabilities / total_equity",
        "components": ["total_liabilities", "total_equity"],
        "source": "balance_sheet"
    },
    "interest_coverage": {
        "formula": "operating_profit / financing_costs",
        "components": ["operating_profit", "financing_costs"],
        "source": "income_statement",
        "condition": "financing_costs != 0"
    },

    # 效率比率
    "inventory_turnover": {
        "formula": "cost_of_sales / average_inventory",
        "components": ["cost_of_sales"],
        "source": "income_statement",
        "additional": "average_inventory requires two periods"
    },
    "receivables_turnover": {
        "formula": "revenue / average_receivables",
        "components": ["revenue"],
        "source": "income_statement",
        "additional": "average_receivables requires two periods"
    },
    # 资产周转率
    "asset_turnover": {
        "formula": "revenue / average_total_assets",
        "components": ["revenue"],
        "source": "income_statement",
        "additional": "average_total_assets requires two periods"
    },

    # 盈利能力比率
    "return_on_assets": {
        "formula": "profit_attributable / average_total_assets",
        "components": ["profit_attributable"],
        "source": "income_statement",
        "additional": "average_total_assets requires two periods"
    },
    "return_on_equity": {
        "formula": "profit_attributable / average_shareholders_equity",
        "components": ["profit_attributable"],
        "source": "income_statement",
        "additional": "average_shareholders_equity requires two periods"
    },
    "return_on_invested_capital": {
        "formula": "operating_profit * (1 - tax_rate) / (total_equity + interest_bearing_debt)",
        "components": ["operating_profit"],
        "source": "income_statement",
        "additional": "Requires tax_rate and debt calculation"
    },

    # 现金流比率
    "operating_cash_flow_ratio": {
        "formula": "net_cash_operating / total_current_liabilities",
        "components": ["net_cash_operating", "total_current_liabilities"],
        "source": ["cash_flow", "balance_sheet"]
    },
    "free_cash_flow": {
        "formula": "net_cash_operating - fixed_assets_acquisition",
        "components": ["net_cash_operating", "fixed_assets_acquisition"],
        "source": "cash_flow"
    },

    # 增长比率
    "revenue_growth": {
        "formula": "(current_revenue - previous_revenue) / previous_revenue",
        "components": [],
        "additional": "Requires multi-period data"
    },
    "earnings_growth": {
        "formula": "(current_profit - previous_profit) / previous_profit",
        "components": [],
        "additional": "Requires multi-period data"
    },

    # 每股指标
    "book_value_per_share": {
        "formula": "shareholders_equity / shares_outstanding",
        "components": ["shareholders_equity"],
        "source": "balance_sheet",
        "additional": "Requires shares outstanding"
    },
    "earnings_per_share": {
        "formula": "profit_attributable / shares_outstanding",
        "components": ["profit_attributable"],
        "source": "income_statement",
        "additional": "Requires shares outstanding"
    }
}

# 港股特殊项目处理
HK_SPECIAL_MAPPING = {
    "保留溢利(累计亏损)": "retained_earnings",
    "预付款按金及其他应收款": "prepayments_deposits_receivables",
    "递延收入(流动)": "deferred_revenue_current",
    "指定以公允价值记账之金融资产": "financial_assets_fair_value",
    "除税前溢利": "profit_before_tax",
    "除税后溢利": "profit_after_tax",
    "经营业务现金净额": "net_cash_operating"
}

# 报告期识别
REPORT_PERIOD_MAPPING = {
    "12-31": "annual",
    "06-30": "interim",
    "03-31": "quarterly"
}

# 货币单位
CURRENCY_MAPPING = "CNY"  # 所有金额单位为人民币

