#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@作者: laity.wang
@创建日期: 2026/2/13 12:04
@文件名: element_locator.py
@项目名称: ui_auto_test
@文件完整绝对路径: D:/LaityTest/ui_auto_test/core\element_locator.py
@文件相对项目路径:   # 可选，不需要可以删掉这行
@描述: 
"""
### 6. 元素定位解析器（core/element_locator.py）
from enums.locator_type import LocatorType
from core.custom_exceptions import LocatorParseException


class ElementLocator:
    """
    企业级元素定位解析器（核心功能：多格式解析+多定位降级）
    支持的定位器格式：
    1. 推荐格式：{"type": "id", "value": "kw"}（易维护）
    2. 兼容格式：("id", "kw") / "id=kw"
    3. 降级格式：[{"type": "id", "value": "kw"}, {"type": "xpath", "value": "//input[@id='kw']"}]
    """

    @staticmethod
    def parse_locator(locator: dict | tuple | str | list) -> tuple:
        """
        解析定位器为Selenium可识别的元组 (By.XX, value)
        :param locator: 定位器（支持单定位/多定位降级）
        :return: (By.XX, value)
        """
        # 多定位降级：传入列表时，遍历直到解析成功
        if isinstance(locator, list):
            for loc in locator:
                try:
                    return ElementLocator.parse_locator(loc)
                except LocatorParseException:
                    continue
            raise LocatorParseException(locator, "所有定位方式均解析失败")

        # 单定位解析
        try:
            if isinstance(locator, dict):
                # 推荐格式：{"type": "id", "value": "kw"}
                if "type" not in locator or "value" not in locator:
                    raise LocatorParseException(locator, "字典格式必须包含type和value字段")
                loc_type = locator["type"].lower()
                loc_value = locator["value"]
            elif isinstance(locator, tuple):
                # 兼容格式：("id", "kw")
                if len(locator) != 2:
                    raise LocatorParseException(locator, "元组格式必须是(length=2)")
                loc_type, loc_value = locator
                loc_type = loc_type.lower()
            elif isinstance(locator, str):
                # 兼容格式："id=kw"
                if "=" not in locator:
                    raise LocatorParseException(locator, "字符串格式必须包含=，如id=kw")
                loc_type, loc_value = locator.split("=", 1)  # 只分割一次，避免value含=
                loc_type = loc_type.lower()
            else:
                raise LocatorParseException(locator, f"不支持的定位器类型：{type(locator)}")

            # 转换为Selenium原生定位方式
            selenium_loc_type = LocatorType.get_selenium_locator(loc_type)
            return (selenium_loc_type, loc_value)
        except Exception as e:
            # 捕获所有解析异常，封装为自定义异常抛出
            raise LocatorParseException(locator, str(e))

    @staticmethod
    def get_locator_desc(locator: dict | tuple | str | list) -> str:
        """
        获取定位器描述（用于日志/报告，提升可读性）
        :param locator: 定位器
        :return: 易读的描述字符串
        """
        try:
            parsed = ElementLocator.parse_locator(locator)
            # 提取By.XX的后缀（如By.ID→ID）
            loc_type = parsed[0].split(".")[-1]
            return f"{loc_type}={parsed[1]}"
        except Exception as e:
            return f"定位器解析失败：{locator}（异常：{e}）"