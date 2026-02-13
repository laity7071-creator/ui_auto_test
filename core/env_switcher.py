#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@作者: laity.wang
@创建日期: 2026/2/13 12:04
@文件名: env_switcher.py
@项目名称: ui_auto_test
@文件完整绝对路径: D:/LaityTest/ui_auto_test/core\env_switcher.py
@文件相对项目路径:   # 可选，不需要可以删掉这行
@描述: 
"""
### 8. 多环境切换工具（core/env_switcher.py）
import allure
from selenium.webdriver import Remote
from utils.config_util import config
from utils.log_util import log
from core.custom_exceptions import EnvConfigException
from enums.env_type import EnvType


class EnvSwitcher:
    """
    企业级多环境切换工具（核心用于跨环境联动测试）
    支持：dev→test→prod切换，复用浏览器驱动，提升测试效率
    """

    @staticmethod
    @allure.step("切换到目标环境：{target_env}")
    def switch_env(driver: Remote, target_env: str, page_cls=None) -> object:
        """
        切换到目标环境（核心方法）
        :param driver: 浏览器驱动（复用，不重启）
        :param target_env: 目标环境（dev/test/prod）
        :param page_cls: 目标环境的首页PO类（如BaiduHomePage）
        :return: 目标环境的首页PO对象
        """
        # 1. 校验目标环境合法性
        if target_env not in EnvType.get_all_envs():
            raise EnvConfigException(
                target_env,
                f"无效的目标环境：{target_env}，支持：{EnvType.get_all_envs()}"
            )

        # 2. 记录当前环境，便于日志
        current_env = config.get_env()
        if current_env == target_env:
            log.info(f"当前已处于[{target_env}]环境，无需切换")
            if page_cls:
                return page_cls(driver)
            return None

        # 3. 加载目标环境配置（重置全局配置）
        log.info(f"开始从[{current_env}]环境切换到[{target_env}]环境")
        config.load_config(env=target_env)

        # 4. 打开目标环境首页（重置页面状态）
        if page_cls:
            home_page = page_cls(driver)
            home_page.open_url(config.get("server.baidu_url"))
            # 验证环境切换成功
            assert config.get_env() == target_env, f"环境切换失败，当前仍为[{current_env}]"
            assert config.get("server.baidu_url") in home_page.get_current_url(), \
                f"目标环境URL不匹配：预期[{config.get('server.baidu_url')}]，实际[{home_page.get_current_url()}]"
            log.info(f"✅ 成功切换到[{target_env}]环境，首页URL：{config.get('server.baidu_url')}")
            return home_page

        log.info(f"✅ 成功切换到[{target_env}]环境（无页面类）")
        return None

    @staticmethod
    @allure.step("切换回原始环境：{original_env}")
    def switch_back_env(driver: Remote, original_env: str, page_cls=None) -> object:
        """
        切换回原始环境（跨环境测试后必做，避免影响后续用例）
        :param driver: 浏览器驱动
        :param original_env: 原始环境
        :param page_cls: 首页PO类
        :return: 原始环境的首页PO对象
        """
        return EnvSwitcher.switch_env(driver, original_env, page_cls)