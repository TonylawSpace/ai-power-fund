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
from src.futu.futu_cache import get_futu_cache

# 获取环境变量
load_dotenv()
ROOT = os.getenv("ROOT")
JSON_DATA = f"{ROOT}/JsonDdata"
os.makedirs(JSON_DATA, exist_ok=True)

FUTU_OPEND_HOST = os.getenv("FUTU_OPEND_HOST", "127.0.0.1")
FUTU_OPEND_PORT = int(os.getenv("FUTU_OPEND_PORT", "11111"))  # 默认值11111

# Global cache instance
_futuCache = get_futu_cache()

class FutuMarket:
    @staticmethod
    def get_market_snapshot(stock_code_list: List[str]) -> List[MarketSnapShotModel]:

        """Fetch financial metrics from cache or API."""
        # Check cache first
        ticker_list = '_'.join(stock_code_list)
        if futu_cached_data := _futuCache.get_market_snapshot(ticker_list):
            # Filter cached data by date and limit
            futu_cached_data = [MarketSnapShotModel(**snapShotModel) for snapShotModel in futu_cached_data]

            if futu_cached_data:
                logger.info(f"DATA->List[MarketSnapShotModel] RETURN FROM FUTU CACHE DATA")
                return futu_cached_data[:limit]

        try:
            quote_ctx = OpenQuoteContext(host=FUTU_OPEND_HOST, port=FUTU_OPEND_PORT)
            ret, data = quote_ctx.get_market_snapshot(stock_code_list)
            if ret == RET_OK:
                # print(data['code'][0],data[0])  # 取第一条的股票代码与股价
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

    @staticmethod
    def get_market_snapshopt_stock_price(ticker:string):float

        stock_code_list=[ticker]
        if marketSnapShotList := get_market_snapshot(stock_code_list) :
            market_snapshot = marketSnapShotList[0]
            return market_snapshot["last_price"]



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

    quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)

    ret_sub, err_message = quote_ctx.subscribe(['HK.03690'], [SubType.QUOTE], subscribe_push=False)
    # 先订阅 K 线类型。订阅成功后 OpenD 将持续收到服务器的推送，False 代表暂时不需要推送给脚本
    if ret_sub == RET_OK:  # 订阅成功
        ret, data = quote_ctx.get_stock_quote(['HK.03690'])  # 获取订阅股票报价的实时数据
        if ret == RET_OK:
            print(data)
            print(data['code'][0])  # 取第一条的股票代码
            print(data['code'].values.tolist())  # 转为 list
        else:
            print('error:', data)
    else:
        Logger(f'subscription failed: {err_message}')
    quote_ctx.close()  # 关闭当条连接，OpenD 会在1分钟后自动取消相应股票相应类型的订阅