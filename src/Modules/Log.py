import logging

LOGGING_FILE_PATH = './Logs/app.log'

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(levelname)s] [%(filename)s:%(lineno)d] - %(message)s',
    # 写入日志文件，追加模式
    filename=LOGGING_FILE_PATH,
    filemode='a',
    datefmt='%Y-%m-%d %H:%M:%S'
)