#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@作者: laity.wang
@创建日期: 2026/2/13 12:07
@文件名: baidu_home.py
@项目名称: ui_auto_test
@文件完整绝对路径: D:/LaityTest/ui_auto_test/page_objects/baidu\baidu_home.py
@文件相对项目路径:   # 可选，不需要可以删掉这行
@描述: 
"""
#### page_objects/baidu/baidu_home.py
import allure
from core.base_page import BasePage
from utils.config_util import config

class BaiduHomePage(BasePage):
    """
    百度首页页面对象（POM规范，按业务模块组织）
    核心：封装页面元素+业务操作，不包含测试逻辑
    """
    # 元素定位器（企业级规范：统一管理，支持多定位降级）
    SEARCH_INPUT = [
        {"type": "id", "value": "kw"},          # 优先ID定位
        {"type": "xpath", "value": "//input[@name='wd']"},  # 降级XPath
        {"type": "css selector", "value": "#kw"}  # 降级CSS
    ]
    SEARCH_BUTTON = [
        {"type": "id", "value": "su"},
        {"type": "xpath", "value": "//input[@value='百度一下']"}
    ]
    BAIDU_LOGO = {"type": "xpath", "value": "//div[@id='lg']/img"}

    def __init__(self, driver):
        """初始化：调用父类构造方法"""
        super().__init__(driver)
        self.baidu_url = config.get("server.baidu_url")

    @allure.feature("百度首页")
    @allure.story("打开百度首页")
    def open_baidu_home(self):
        """打开百度首页（封装业务操作）"""
        self.open_url(self.baidu_url)
        # 验证页面加载成功（等待logo可见）
        self.wait_element_visible(self.BAIDU_LOGO)
        log.info(f"百度首页打开成功：{self.baidu_url}")

    @allure.feature("百度搜索")
    @allure.story("执行搜索")
    def search(self, keyword: str):
        """
        执行百度搜索（核心业务操作）
        :param keyword: 搜索关键词
        """
        # 输入关键词
        self.input_text(self.SEARCH_INPUT, keyword)
        # 点击搜索按钮
        self.click(self.SEARCH_BUTTON)
        # 等待搜索结果加载（等待logo不可见）
        self.wait_element_invisible(self.BAIDU_LOGO, timeout=15)