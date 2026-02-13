#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@作者: laity.wang
@创建日期: 2026/2/13 12:10
@文件名: test_cross_env.py
@项目名称: ui_auto_test
@文件完整绝对路径: D:/LaityTest/ui_auto_test/test_cases/test_regression\test_cross_env.py
@文件相对项目路径:   # 可选，不需要可以删掉这行
@描述: 
"""
### 2. test_cases/test_regression/test_cross_env.py（跨环境用例）
"""
跨环境联动测试用例（企业级必备）
场景：dev造数 → test验证 → 切回原环境
"""
import pytest
import allure

from core.env_switcher import EnvSwitcher
from utils.config_util import config
from utils.log_util import log

@allure.epic("跨环境测试")
@allure.feature("多环境数据一致性验证")
@pytest.mark.cross_env
@pytest.mark.regression
def test_cross_env_search_consistency(browser, baidu_home_page, baidu_result_page):
    """
    测试多环境搜索结果一致性
    1. 在当前环境（默认dev）搜索
    2. 切换到test环境搜索
    3. 对比结果是否一致
    4. 切回原环境
    """
    # 1. 记录原始环境
    original_env = config.get_env()
    keyword = "Python 自动化测试"
    log.info(f"原始环境：{original_env}，测试关键词：{keyword}")

    # 2. 原始环境搜索
    baidu_home_page.search(keyword)
    original_title = baidu_result_page.get_first_result_title()
    log.info(f"{original_env} 环境结果标题：{original_title}")

    # 3. 切换到 test 环境
    test_home_page = EnvSwitcher.switch_env(browser, "test", BaiduHomePage)
    test_home_page.search(keyword)
    test_title = baidu_result_page.get_first_result_title()
    log.info(f"test 环境结果标题：{test_title}")

    # 4. 验证多环境结果一致
    assert original_title == test_title, \
        f"多环境结果不一致：{original_env}=[{original_title}], test=[{test_title}]"

    # 5. 切回原始环境
    EnvSwitcher.switch_back_env(browser, original_env, BaiduHomePage)
    log.info("✅ 跨环境测试通过，已切回原始环境")