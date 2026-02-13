#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@作者: laity.wang
@创建日期: 2026/2/13 12:06
@文件名: log_util.py
@项目名称: ui_auto_test
@文件完整绝对路径: D:/LaityTest/ui_auto_test/utils\log_util.py
@文件相对项目路径:   # 可选，不需要可以删掉这行
@描述: 
"""
#### utils/log_util.py（日志工具）
import os
import time
import allure
from loguru import logger
from utils.config_util import config
from utils.file_util import FileUtil


class LogUtil:
    """
    企业级日志工具（核心：按环境/天分割+Allure集成+彩色输出）
    替代原生logging，配置更简单、输出更美观
    """
    _logger = None

    @classmethod
    def init_logger(cls):
        """初始化日志配置（单例）"""
        if cls._logger:
            return cls._logger

        # 1. 配置日志目录（按环境隔离）
        env = config.get_env()
        log_dir = os.path.join(config.get("log.dir", "./logs"), env)
        FileUtil.create_dir(log_dir)

        # 2. 日志文件名（按环境+天分割）
        log_file = os.path.join(log_dir, f"ui_auto_{env}_{time.strftime('%Y%m%d')}.log")

        # 3. 清除默认配置（避免重复输出）
        logger.remove()

        # 4. 添加文件处理器（按天分割，保留7天）
        cls._logger = logger.add(
            log_file,
            rotation="00:00",  # 每天0点分割
            retention="7 days",  # 保留7天日志
            encoding="utf-8",
            level=config.get("log.level", "INFO"),
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{line} | {message}"
        )

        # 5. 添加控制台处理器（彩色输出，便于调试）
        logger.add(
            sink=lambda msg: print(msg, end=""),
            colorize=True,
            format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
                   "<level>{level: <8}</level> | "
                   "<cyan>{name}:{line}</cyan> | "
                   "<level>{message}</level>"
        )

        return cls._logger

    # ==================== 日志级别方法 ====================
    @classmethod
    def info(cls, msg: str, attach_to_allure: bool = True):
        """INFO级别（常规日志，默认附Allure）"""
        cls.init_logger()
        logger.info(msg)
        if attach_to_allure:
            allure.attach(msg, "INFO日志", allure.attachment_type.TEXT)

    @classmethod
    def warning(cls, msg: str, attach_to_allure: bool = True):
        """WARNING级别（警告日志）"""
        cls.init_logger()
        logger.warning(msg)
        if attach_to_allure:
            allure.attach(msg, "WARNING日志", allure.attachment_type.TEXT)

    @classmethod
    def error(cls, msg: str, attach_to_allure: bool = True):
        """ERROR级别（错误日志）"""
        cls.init_logger()
        logger.error(msg)
        if attach_to_allure:
            allure.attach(msg, "ERROR日志", allure.attachment_type.TEXT)

    @classmethod
    def debug(cls, msg: str, attach_to_allure: bool = False):
        """DEBUG级别（调试日志，默认不附Allure）"""
        cls.init_logger()
        logger.debug(msg)
        if attach_to_allure:
            allure.attach(msg, "DEBUG日志", allure.attachment_type.TEXT)

    @classmethod
    def critical(cls, msg: str, attach_to_allure: bool = True):
        """CRITICAL级别（严重错误日志）"""
        cls.init_logger()
        logger.critical(msg)
        if attach_to_allure:
            allure.attach(msg, "CRITICAL日志", allure.attachment_type.TEXT)


# 初始化日志对象（全局使用）
log = LogUtil()