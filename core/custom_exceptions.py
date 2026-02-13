#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@作者: laity.wang
@创建日期: 2026/2/13 12:03
@文件名: custom_exceptions.py
@项目名称: ui_auto_test
@文件完整绝对路径: D:/LaityTest/ui_auto_test/core\custom_exceptions.py
@文件相对项目路径:   # 可选，不需要可以删掉这行
@描述: 
"""
### 4. 自定义异常（core/custom_exceptions.py）
class UiAutoException(Exception):
    """
    UI自动化基础异常类（所有自定义异常的父类）
    企业级规范：自定义异常便于定位问题类型
    """
    def __init__(self, msg: str = None):
        self.msg = msg or "UI自动化执行异常"
        super().__init__(self.msg)

class LocatorParseException(UiAutoException):
    """
    元素定位器解析异常（如格式错误、不支持的类型）
    """
    def __init__(self, locator: dict | tuple | str, msg: str = None):
        self.locator = locator  # 出错的定位器
        self.msg = msg or f"元素定位器解析失败：{locator}"
        super().__init__(self.msg)

class ElementOperateException(UiAutoException):
    """
    元素操作异常（点击/输入/切换iframe等）
    """
    def __init__(self, locator: dict | tuple | str, operate: str, msg: str = None):
        self.locator = locator  # 操作的元素定位器
        self.operate = operate  # 执行的操作（如"点击"）
        self.msg = msg or f"元素[{locator}]执行{operate}操作失败"
        super().__init__(self.msg)

class EnvConfigException(UiAutoException):
    """
    环境配置异常（如配置缺失、解密失败）
    """
    def __init__(self, env: str, msg: str = None):
        self.env = env  # 出错的环境
        self.msg = msg or f"环境[{env}]配置加载/校验失败"
        super().__init__(self.msg)

class CaseExecuteException(UiAutoException):
    """
    用例执行异常（步骤解析失败、参数替换失败）
    """
    def __init__(self, case_id: str, msg: str = None):
        self.case_id = case_id  # 出错的用例ID
        self.msg = msg or f"用例[{case_id}]执行失败"
        super().__init__(self.msg)