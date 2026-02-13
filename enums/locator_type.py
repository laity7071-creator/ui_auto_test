#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@作者: laity.wang
@创建日期: 2026/2/13 12:02
@文件名: locator_type.py
@项目名称: ui_auto_test
@文件完整绝对路径: D:/LaityTest/ui_auto_test/enums\locator_type.py
@文件相对项目路径:   # 可选，不需要可以删掉这行
@描述: 
"""
#### enums/locator_type.py（元素定位枚举）
from enum import Enum

class LocatorType(Enum):
    """
    元素定位方式枚举（覆盖Selenium所有支持的定位方式）
    企业级规范：定位方式统一管理，避免手写字符串出错
    """
    ID = "id"
    XPATH = "xpath"
    CSS_SELECTOR = "css selector"
    NAME = "name"
    CLASS_NAME = "class name"
    TAG_NAME = "tag name"
    LINK_TEXT = "link text"
    PARTIAL_LINK_TEXT = "partial link text"

    @classmethod
    def get_selenium_locator(cls, locator_type: str):
        """
        转换为Selenium原生的By.XX类型（核心方法）
        :param locator_type: 枚举值（如"id"）
        :return: By.ID/By.XPATH等
        """
        from selenium.webdriver.common.by import By
        locator_map = {
            cls.ID.value: By.ID,
            cls.XPATH.value: By.XPATH,
            cls.CSS_SELECTOR.value: By.CSS_SELECTOR,
            cls.NAME.value: By.NAME,
            cls.CLASS_NAME.value: By.CLASS_NAME,
            cls.TAG_NAME.value: By.TAG_NAME,
            cls.LINK_TEXT.value: By.LINK_TEXT,
            cls.PARTIAL_LINK_TEXT.value: By.PARTIAL_LINK_TEXT
        }
        if locator_type not in locator_map:
            raise ValueError(f"不支持的定位方式：{locator_type}，支持：{list(locator_map.keys())}")
        return locator_map[locator_type]