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
JSON_DATA = f"{ROOT}/JsonData"
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
    def get_market_snapshot_stock_price(ticker: str) -> float:
        """
        获取单只股票的最新价格

        Args:
            ticker: 股票代码，例如"HK.03690"

        Returns:
            股票的最新价格，如果获取失败则返回0.0
        """
        try:
            # 调用已有方法获取市场快照
            stock_code_list = [ticker]
            market_snapshot_list = FutuMarket.get_market_snapshot(stock_code_list)

            # 检查是否成功获取数据
            if not market_snapshot_list:
                logger.warning(f"无法获取股票 {ticker} 的市场快照数据")
                return 0.0

            # 获取第一个快照(因为只查询了一只股票)
            market_snapshot = market_snapshot_list[0]

            # 尝试获取最新价格，处理可能的属性访问问题
            if hasattr(market_snapshot, 'last_price'):
                return float(market_snapshot.last_price)
            elif isinstance(market_snapshot, dict) and 'last_price' in market_snapshot:
                return float(market_snapshot['last_price'])
            else:
                logger.warning(f"股票 {ticker} 的市场快照中不包含last_price字段")
                return 0.0

        except Exception as e:
            logger.error(f"获取股票 {ticker} 价格时发生错误: {str(e)}", exc_info=True)
            return 0.0



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
            ticker_price = FutuMarket.get_market_snapshot_stock_price(ticker)
            logger.info(f'{ticker} = {ticker_price}')
        else:
            logger.warning(f"未获取到 {ticker} 的市场快照")
    except Exception as e:
        logger.error(f"测试过程中出现错误: {str(e)}", exc_info=True)

if __name__ == "__main__":
    main()

