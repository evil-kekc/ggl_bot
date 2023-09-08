import logging


def get_logger(logger_name: str, log_file_name: str):
    """Getting and writing logs to a file

    :param logger_name: name of logger
    :param log_file_name: the name of the file to which the logs will be written
    :return:
    """
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    aiogram_logger = logging.getLogger(logger_name)
    aiogram_logger.setLevel(logging.INFO)
    log_file_handler = logging.FileHandler(log_file_name)
    log_file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    aiogram_logger.addHandler(log_file_handler)
