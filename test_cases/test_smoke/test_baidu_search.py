#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@作者: laity.wang
@创建日期: 2026/2/13 12:09
@文件名: test_baidu_search.py
@项目名称: ui_auto_test
@文件完整绝对路径: D:/LaityTest/ui_auto_test/test_cases/test_smoke\test_baidu_search.py
@文件相对项目路径:   # 可选，不需要可以删掉这行
@描述: 
"""
### 1. test_cases/test_smoke/test_baidu_search.py（冒烟用例）
"""
百度搜索 - 冒烟测试用例
企业级特点：
- 代码只有几行，永不修改
- 所有步骤/数据/验证都在 YAML 里
- 需求变更只改配置，不改代码
"""
import pytest
import allure

from core.case_engine import CaseEngine
from utils.file_util import FileUtil

# 加载当前环境的用例配置（YAML文件）
case_config = FileUtil.read_env_data(
    file_name="baidu_search_cases.yaml",
    data_type="yaml"
)

@allure.epic("百度模块")
@allure.feature("搜索功能")
@pytest.mark.smoke  # 冒烟测试标签
@pytest.mark.parametrize("case", case_config["cases"])
def test_baidu_search_smoke(case, baidu_home_page):
    """
    百度搜索冒烟测试入口
    :param case: 从YAML读取的单条用例
    :param baidu_home_page: 百度首页页面对象
    """
    # 初始化用例引擎
    engine = CaseEngine(baidu_home_page)
    # 执行用例（自动解析步骤+数据）
    engine.execute_case_with_data(case)
