# -*- coding:utf-8 -*-

# ==============================================================================
# 日志的配置以及使用方法。
# ==============================================================================

import os
import datetime
import logging
import logging.config
import yaml
import config.common_config as com_config
from config.common_config import COMMON_LOG_DIR


# =========================== 全局变量 ===========================
# common log directory

# 创建目录路径
if not os.path.exists(COMMON_LOG_DIR):
    os.makedirs(COMMON_LOG_DIR)

LOG_FILE = "application.log"

LOGGING_DICT = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "simple": {
                'format': '%(asctime)s [%(name)s:%(lineno)d] [%(levelname)s]- %(message)s'
            },
            'standard': {
                'format': '%(asctime)s [%(threadName)s:%(thread)d] [%(name)s:%(lineno)d] [%(levelname)s]- %(message)s'
            },
        },

        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": "DEBUG",
                "formatter": "simple",
                "stream": "ext://sys.stdout"
            },

            "default": {
                "class": "logging.handlers.RotatingFileHandler",
                "level": "INFO",
                "formatter": "simple",
                "filename": os.path.join(COMMON_LOG_DIR, LOG_FILE),
                'mode': 'w+',
                "maxBytes": 1024*1024*5,  # 5 MB
                "backupCount": 20,
                "encoding": "utf8"
            },
        },

        "loggers": {
            "app": {
                "level": "INFO",
                "handlers": ["console"],
                "propagate": "no"
            }
        },

        "root": {
            'handlers': ['default'],
            'level': "INFO",
            'propagate': False
        }
    }


def test_dictConfig():
    """
    通过字典配置日志。
    :return:
    """
    logging.config.dictConfig(LOGGING_DICT)

    log = logging.getLogger()
    print("print A")
    log.info("log B")


def test_yaml_config():
    """
    通过yaml文件配置日志。
    :return:
    """
    yaml_file = os.path.join(com_config.CONFIG_DIR, 'logging.yml')
    with open(yaml_file, 'r') as f_conf:
        dict_conf = yaml.load(f_conf)
    logging.config.dictConfig(dict_conf)

    logger = logging.getLogger('simpleExample')
    logger.debug('debug message')
    logger.info('info message')
    logger.info('通过yaml文件配置日志')
    logger.warning('warn message')
    logger.error('error message')
    logger.critical('critical message')


def test_basicConfig():
    """
    配置日志基本信息。
    :return:
    """
    file_name = os.path.join(COMMON_LOG_DIR, LOG_FILE)
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                        datefmt='%m-%d %H:%M',
                        filename=file_name,
                        filemode='w')
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
    console.setFormatter(formatter)
    # add the handler to the root logger
    logging.getLogger('').addHandler(console)

    logger = logging.getLogger('')
    logger.info('info message')


if __name__ == '__main__':
    pass
    # test_dictConfig()
    test_yaml_config()
    # test_basicConfig()