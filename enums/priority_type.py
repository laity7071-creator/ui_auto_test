#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@作者: laity.wang
@创建日期: 2026/2/13 12:03
@文件名: priority_type.py
@项目名称: ui_auto_test
@文件完整绝对路径: D:/LaityTest/ui_auto_test/enums\priority_type.py
@文件相对项目路径:   # 可选，不需要可以删掉这行
@描述: 
"""
#### enums/priority_type.py（用例优先级枚举）
from enum import Enum

class PriorityType(Enum):
    """
    用例优先级枚举（企业级用例管理）
    配合Allure报告的severity级别
    """
    CRITICAL = "critical"  # 阻塞级（核心流程）
    HIGH = "high"          # 高优先级（重要功能）
    NORMAL = "normal"      # 普通优先级（常规功能）
    LOW = "low"            # 低优先级（次要功能）