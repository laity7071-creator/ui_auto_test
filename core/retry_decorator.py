#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@作者: laity.wang
@创建日期: 2026/2/13 12:03
@文件名: retry_decorator.py
@项目名称: ui_auto_test
@文件完整绝对路径: D:/LaityTest/ui_auto_test/core\retry_decorator.py
@文件相对项目路径:   # 可选，不需要可以删掉这行
@描述: 
"""
### 5. 失败重试装饰器（core/retry_decorator.py）
import time
import functools
from loguru import logger
from core.custom_exceptions import ElementOperateException

def retry_on_failure(max_retries: int = 3, delay: float = 1.0, exceptions: tuple = (ElementOperateException,)):
    """
    企业级失败重试装饰器（核心用于元素操作）
    解决动态元素、页面加载慢导致的偶发失败问题
    :param max_retries: 最大重试次数（默认3次）
    :param delay: 重试间隔（默认1秒，避免频繁重试）
    :param exceptions: 需要重试的异常类型（默认元素操作异常）
    :return: 装饰后的函数
    """
    def decorator(func):
        # 保留原函数信息（如名称、文档字符串），便于日志/调试
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            retry_count = 0  # 已重试次数
            while retry_count < max_retries:
                try:
                    # 执行原函数，成功则直接返回
                    return func(*args, **kwargs)
                except exceptions as e:
                    retry_count += 1
                    logger.warning(
                        f"执行函数[{func.__name__}]失败，第{retry_count}次重试（最大{max_retries}次），异常：{e}"
                    )
                    # 达到最大重试次数，抛出异常
                    if retry_count >= max_retries:
                        logger.error(f"函数[{func.__name__}]重试{max_retries}次仍失败，终止重试并抛出异常")
                        raise
                    # 未达到最大次数，等待后重试
                    time.sleep(delay)
            # 理论上不会走到这里，防止极端情况
            return func(*args, **kwargs)
        return wrapper
    return decorator