# logger.py
import logging
from datetime import datetime
import os
from dotenv import load_dotenv

# 获取环境变量
load_dotenv()
ROOT = os.getenv("ROOT", "/")

# 创建一个日志记录器
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)  # 设置日志级别为 DEBUG

# 生成当前日期的字符串，格式为 YYYYMMDD
log_folder = f"{ROOT}/log"
os.makedirs(log_folder, exist_ok=True)  # exist_ok=True 表示如果目录已存在不报错
current_date = datetime.now().strftime("%Y%m%d")
log_filename = f"{ROOT}/log/log_{current_date}.log"  # 例如：log_20250624

# 创建一个文件处理器，使用格式化后的文件名
file_handler = logging.FileHandler(log_filename)
file_handler.setLevel(logging.INFO)  # 设置文件处理器的日志级别为 INFO

# 创建一个格式化器，并将其添加到文件处理器
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)

# 将文件处理器添加到日志记录器
logger.addHandler(file_handler)

# 现在你可以使用日志记录器了
# logger.debug('This is a debug message')  # 不会被写入文件，因为文件处理器级别是 INFO
# logger.info('This is a info message')
# logger.warning('This is a warning message')
# logger.error('This is a error message')