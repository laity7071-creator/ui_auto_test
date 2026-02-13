#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@作者: laity.wang
@创建日期: 2026/2/13 12:01
@文件名: env_type.py
@项目名称: ui_auto_test
@文件完整绝对路径: D:/LaityTest/ui_auto_test/enums\env_type.py
@文件相对项目路径:   # 可选，不需要可以删掉这行
@描述: 
"""
### 3. 枚举类（enums/）
#### enums/env_type.py（环境类型枚举）
from enum import Enum

class EnvType(Enum):
    """
    环境类型枚举（避免魔法值，提升代码可读性）
    企业级规范：所有环境相关的字符串都用枚举，防止拼写错误
    """
    DEV = "dev"       # 开发环境（造数/调试）
    TEST = "test"     # 测试环境（功能验证）
    PROD = "prod"     # 生产环境（冒烟/线上验证）

    @classmethod
    def get_all_envs(cls) -> list:
        """获取所有支持的环境列表（用于校验）"""
        return [e.value for e in cls]
