# logger.py
import logging
import string
from datetime import datetime
import os
from typing import AnyStr, List
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
    @staticmethod
    def get_market_snapshot(stock_code_list: List[str]) -> List[MarketSnapShotModel]:
        quote_ctx = None
        try:
            quote_ctx = OpenQuoteContext(host=FUTU_OPEND_HOST, port=FUTU_OPEND_PORT)
            ret, data = quote_ctx.get_market_snapshot(stock_code_list)
            if ret == RET_OK:
                print(data['code'][0])  # 取第一条的股票代码
                print(data['code'].values.tolist())  # 转为 list
                market_snapshot_list = []
                for index, row in data.iterrows():
                    # 假设 MarketSnapShotModel 可以通过字典解包初始化
                    market_snapshot_list.append(row)
                return market_snapshot_list
            else:
                logger.error(f'获取市场快照出错: {data}')
                return []
        except Exception as e:
            logger.error(f"处理数据时出错: {str(e)}", exc_info=True)
            return []
        finally:
            if quote_ctx:
                quote_ctx.close()  # 结束后记得关闭当条连接，防止连接条数用尽


def main():
    ticker = "HK.03690"
    try:
        # 调用 get_market_snapshot 函数获取市场快照
        market_snapshots = FutuMarket.get_market_snapshot([ticker])

        if market_snapshots:
            logger.info(f"成功获取 {ticker} 的市场快照 {len(market_snapshots)}")
            # for snapshot in market_snapshots:
                # 打印市场快照的信息，这里假设 MarketSnapShotModel 类有 __str__ 方法
                # logger.info(snapshot)
        else:
            logger.warning(f"未获取到 {ticker} 的市场快照")
    except Exception as e:
        logger.error(f"测试过程中出现错误: {str(e)}", exc_info=True)

if __name__ == "__main__":
    main()