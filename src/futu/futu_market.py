# logger.py
import logging
import string
from datetime import datetime
import os
from typing import AnyStr
from dotenv import load_dotenv
from src.tools.logger import logger
from futu import *
from src.futu.market_snapshot_model import MarketSnapShotModel
# 获取环境变量
load_dotenv()
ROOT = os.getenv("ROOT")
JSON_DATA = f"{ROOT}/JsonDdata"
os.makedirs(JSON_DATA, exist_ok=True)

FUTU_OPEND_HOST = os.getenv("FUTU_OPEND_HOST", "127.0.0.1")
FUTU_OPEND_PORT = int(os.getenv("FUTU_OPEND_PORT", "11111"))  # 默认值11111

class FutuMarket:
    def get_market_snapshot(any: stock_code_list):list[MarketSnapShotModel]
        try:
            quote_ctx = OpenQuoteContext(host=FUTU_OPEND_HOST, port=FUTU_OPEND_PORT)
            ret, data = quote_ctx.get_market_snapshot(stock_code_list)
            if ret == RET_OK:
                print(data)
                print(data['code'][0])  # 取第一条的股票代码
                print(data['code'].values.tolist())  # 转为 list
                ListOfMarketSnapShotModel = data['code'].values.tolist()
                return ListOfMarketSnapShotModel
            else:
                print('error:', data)
                quote_ctx.close()  # 结束后记得关闭当条连接，防止连接条数用尽
                return None
        except Exception as e:
            logger.error(f"处理数据时出错: {str(e)}", exc_info=True)
