#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@作者: laity.wang
@创建日期: 2026/2/13 12:02
@文件名: browser_type.py
@项目名称: ui_auto_test
@文件完整绝对路径: D:/LaityTest/ui_auto_test/enums\browser_type.py
@文件相对项目路径:   # 可选，不需要可以删掉这行
@描述: 
"""
#### enums/browser_type.py（浏览器枚举）
from enum import Enum

class BrowserType(Enum):
    """
    浏览器类型枚举（企业级规范）
    支持Chrome/Firefox/Edge/Safari，扩展时只需加枚举值
    """
    CHROME = "chrome"
    FIREFOX = "firefox"
    EDGE = "edge"
    SAFARI = "safari"

    @classmethod
    def is_supported(cls, browser_type: str) -> bool:
        """校验浏览器是否支持"""
        return browser_type.lower() in [e.value for e in cls]