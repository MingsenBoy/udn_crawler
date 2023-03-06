import logging
from warnings import catch_warnings
FORMAT = '%(asctime)s %(levelname)s: %(message)s'


def setup_logger(name, log_file="./default.log", level=logging.DEBUG, format='%(asctime)s %(levelname)s: %(message)s',datefmt='%Y/%m/%d %H:%M:%S'):

    handler = logging.FileHandler(log_file, 'a', 'utf-8')   #設定輸出檔案

    formatter = logging.Formatter(format, datefmt)          #設定log輸出格式
    handler.setFormatter(formatter)

    logger = logging.getLogger(name)                        #取得logger
    logger.setLevel(level)
    logger.addHandler(handler)

    return logger