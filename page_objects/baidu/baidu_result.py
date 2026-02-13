#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@作者: laity.wang
@创建日期: 2026/2/13 12:08
@文件名: baidu_result.py
@项目名称: ui_auto_test
@文件完整绝对路径: D:/LaityTest/ui_auto_test/page_objects/baidu\baidu_result.py
@文件相对项目路径:   # 可选，不需要可以删掉这行
@描述: 
"""
### 1. page_objects/baidu/baidu_result.py（完整）
import allure
from core.base_page import BasePage
from utils.log_util import log

class BaiduResultPage(BasePage):
    """
    百度搜索结果页 页面对象
    职责：只封装本页面的元素定位 + 页面专属操作
    不写任何测试逻辑，测试逻辑由CaseEngine统一执行
    """
    # ==================== 元素定位器 ====================
    # 第一个搜索结果标题
    FIRST_RESULT_TITLE = {
        "type": "xpath",
        "value": "//div[@id='content_left']//h3/a[1]"
    }
    # 搜索结果数量提示
    RESULT_COUNT_TIP = {
        "type": "xpath",
        "value": "//div[@class='nums_text']"
    }

    def __init__(self, driver):
        super().__init__(driver)

    @allure.feature("百度搜索结果页")
    @allure.story("获取第一条结果标题")
    def get_first_result_title(self) -> str:
        """
        获取第一条搜索结果的标题文本
        :return: 标题字符串
        """
        title = self.get_element_text(self.FIRST_RESULT_TITLE)
        log.info(f"获取第一条搜索结果标题：{title}")
        return title

    @allure.feature("百度搜索结果页")
    @allure.story("验证结果包含关键词")
    def verify_keyword_in_result(self, keyword: str) -> bool:
        """
        验证第一条结果包含指定关键词（业务封装）
        :param keyword: 要验证的关键词
        :return: True/False
        """
        is_contain = self.verify_element_contains_text(
            self.FIRST_RESULT_TITLE,
            keyword
        )
        log.info(f"验证结果：结果标题{'包含' if is_contain else '不包含'}关键词「{keyword}」")
        return is_contain