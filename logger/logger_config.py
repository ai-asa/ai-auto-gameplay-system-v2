import logging
import datetime

logger = None

def setup_logger():
    global logger

    if logger is not None:
        return logger

    # 現在の日時を取得
    current_time = datetime.datetime.now().strftime("%Y%m%d%H%M%S")

    # ログファイル名に現在の日時を含める
    log_filename = f"logs/{current_time}.log"

    logger = logging.getLogger('my_app')
    logger.setLevel(logging.DEBUG)

    # ファイルハンドラーの設定
    file_handler = logging.FileHandler(log_filename, encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))

    # コンソールハンドラーの設定
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    console_handler.setFormatter(logging.Formatter('%(levelname)s - %(message)s'))

    if not logger.handlers:
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

    return logger
