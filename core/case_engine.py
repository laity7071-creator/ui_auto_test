#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@作者: laity.wang
@创建日期: 2026/2/13 12:05
@文件名: case_engine.py
@项目名称: ui_auto_test
@文件完整绝对路径: D:/LaityTest/ui_auto_test/core\case_engine.py
@文件相对项目路径:   # 可选，不需要可以删掉这行
@描述: 
"""
### 9. 用例执行引擎（core/case_engine.py）
import re
import allure
from loguru import logger
from core.custom_exceptions import CaseExecuteException


class CaseEngine:
    """
    企业级用例执行引擎（核心：逻辑与数据完全解耦）
    解析YAML/Excel配置的用例步骤，动态调用Page层方法，无需修改代码
    """

    def __init__(self, page_obj):
        """
        初始化引擎
        :param page_obj: 页面对象（如BaiduHomePage）
        """
        self.page = page_obj  # 页面对象（提供操作方法）
        self.driver = page_obj.driver  # 浏览器驱动

    def load_case_config(self, config_path: str) -> dict:
        """
        加载YAML用例配置文件
        :param config_path: 配置文件路径
        :return: 解析后的用例配置字典
        """
        from utils.file_util import FileUtil
        try:
            case_config = FileUtil.read_yaml(config_path)
            logger.info(f"加载用例配置成功：{config_path}，用例数量：{len(case_config.get('cases', []))}")
            return case_config
        except Exception as e:
            raise CaseExecuteException("CONFIG_LOAD", f"加载用例配置失败：{e}")

    def execute_case(self, case_config: dict):
        """
        执行单个用例（核心方法：解析步骤并执行）
        :param case_config: 单个用例的配置字典
        """
        case_id = case_config.get("case_id", "UNKNOWN")
        case_name = case_config.get("case_name", "未知用例")

        # 设置Allure用例信息（报告展示）
        allure.dynamic.title(f"[{case_id}] {case_name}")
        allure.dynamic.tag(*case_config.get("tags", []))
        allure.dynamic.severity(case_config.get("priority", "normal"))

        logger.info(f"========== 开始执行用例[{case_id}]：{case_name} ==========")

        # 遍历测试步骤执行
        for step_idx, step in enumerate(case_config.get("steps", []), 1):
            step_name = f"步骤{step_idx}：{step.get('action', '未知操作')}"
            with allure.step(step_name):
                try:
                    self._execute_step(step, case_id, step_idx)
                except Exception as e:
                    raise CaseExecuteException(case_id, f"步骤{step_idx}执行失败：{e}")

        logger.info(f"========== 用例[{case_id}]执行完成 ==========")

    def _execute_step(self, step: dict, case_id: str, step_idx: int):
        """
        执行单个步骤（内部方法）
        :param step: 步骤配置（action/locator/params）
        :param case_id: 用例ID
        :param step_idx: 步骤序号
        """
        # 提取步骤信息
        action = step.get("action")  # 要执行的方法名（如input_text）
        locator = step.get("locator")  # 元素定位器
        params = step.get("params", {})  # 方法参数

        # 校验必要信息
        if not action:
            raise CaseExecuteException(case_id, f"步骤{step_idx}缺失action字段")

        # 动态获取Page层的方法
        try:
            page_method = getattr(self.page, action)
        except AttributeError:
            raise CaseExecuteException(
                case_id,
                f"步骤{step_idx}的action[{action}]不存在，Page层无此方法"
            )

        # 执行方法（根据参数类型适配）
        logger.info(f"执行步骤{step_idx}：{action}，定位器：{locator}，参数：{params}")
        if locator and params:
            # 有定位器+参数（如input_text(locator, text="xxx")）
            page_method(locator, **params)
        elif locator:
            # 只有定位器（如click(locator)）
            page_method(locator)
        elif params:
            # 只有参数（如open_url(url="xxx")）
            page_method(**params)
        else:
            # 无参数（如refresh_page()）
            page_method()

    def execute_case_with_data(self, case_config: dict):
        """
        多组数据执行用例（数据驱动）
        :param case_config: 用例配置
        """
        case_id = case_config.get("case_id", "UNKNOWN")
        data_list = case_config.get("data", [{}])  # 测试数据列表

        # 无数据时执行一次
        if not data_list:
            self.execute_case(case_config)
            return

        # 多组数据循环执行
        for data_idx, data in enumerate(data_list, 1):
            logger.info(f"用例[{case_id}]第{data_idx}组数据：{data}")
            # 替换步骤中的动态参数（如${keyword}→实际值）
            replaced_case = self._replace_params(case_config, data)
            # 执行替换后的用例
            self.execute_case(replaced_case)

    def _replace_params(self, case_config: dict, data: dict) -> dict:
        """
        替换步骤中的动态参数（核心：支持${变量名}格式）
        :param case_config: 原始用例配置
        :param data: 测试数据（如{"keyword": "Python"}）
        :return: 替换后的用例配置
        """
        import json
        # 先转为JSON字符串，替换参数后转回字典（简单高效）
        case_str = json.dumps(case_config, ensure_ascii=False)

        # 替换所有${变量名}为实际值
        for key, value in data.items():
            # 支持${key}或${KEY}（不区分大小写）
            pattern = re.compile(rf"\$\{{{key}\}}", re.IGNORECASE)
            case_str = pattern.sub(str(value), case_str)

        # 转回字典
        try:
            replaced_case = json.loads(case_str)
            return replaced_case
        except Exception as e:
            case_id = case_config.get("case_id", "UNKNOWN")
            raise CaseExecuteException(case_id, f"参数替换失败：{e}，原始数据：{data}")