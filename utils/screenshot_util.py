#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@作者: laity.wang
@创建日期: 2026/2/13 12:06
@文件名: screenshot_util.py
@项目名称: ui_auto_test
@文件完整绝对路径: D:/LaityTest/ui_auto_test/utils\screenshot_util.py
@文件相对项目路径:   # 可选，不需要可以删掉这行
@描述: 
"""
#### utils/screenshot_util.py（截图工具）
import os
import time
import allure
from selenium.webdriver import Remote
from utils.config_util import config
from utils.file_util import FileUtil
from utils.log_util import log


class ScreenshotUtil:
    """
    企业级截图工具（核心：失败自动截图+Allure集成+多环境隔离）
    """

    @staticmethod
    def take_screenshot(driver: Remote, desc: str = "screenshot") -> str:
        """
        截取当前页面
        :param driver: 浏览器驱动
        :param desc: 截图描述（用于文件名）
        :return: 截图文件路径
        """
        # 1. 配置截图目录（按环境隔离）
        env = config.get_env()
        screenshot_dir = os.path.join(config.get("screenshot.dir", "./screenshots"), env)
        FileUtil.create_dir(screenshot_dir)

        # 2. 截图文件名（环境+描述+时间戳，避免重复）
        screenshot_name = f"{env}_{desc}_{time.strftime('%Y%m%d_%H%M%S')}.png"
        screenshot_path = os.path.join(screenshot_dir, screenshot_name)

        # 3. 执行截图
        try:
            driver.save_screenshot(screenshot_path)
            log.info(f"截图成功，路径：{screenshot_path}")
            return screenshot_path
        except Exception as e:
            log.error(f"截图失败：{e}")
            raise

    @staticmethod
    def attach_to_allure(driver: Remote, desc: str = "失败截图"):
        """
        截图并附加到Allure报告（核心：失败用例自动调用）
        :param driver: 浏览器驱动
        :param desc: 截图描述（报告中显示）
        """
        try:
            screenshot_path = ScreenshotUtil.take_screenshot(driver, desc)
            # 附加到Allure报告
            allure.attach.file(
                screenshot_path,
                name=desc,
                attachment_type=allure.attachment_type.PNG
            )
            log.info(f"截图已附加到Allure报告：{desc}")
        except Exception as e:
            log.error(f"截图附加到Allure失败：{e}")