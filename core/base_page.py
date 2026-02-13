#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@作者: laity.wang
@创建日期: 2026/2/13 12:04
@文件名: base_page.py
@项目名称: ui_auto_test
@文件完整绝对路径: D:/LaityTest/ui_auto_test/core\base_page.py
@文件相对项目路径:   # 可选，不需要可以删掉这行
@描述: 
"""
### 7. 增强版POM基类（core/base_page.py）
import allure
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

from core.element_locator import ElementLocator
from core.retry_decorator import retry_on_failure
from core.custom_exceptions import ElementOperateException
from utils.log_util import log
from utils.screenshot_util import ScreenshotUtil
from utils.config_util import config  # 补充导入，修正之前的遗漏


class BasePage:
    """
    企业级增强版POM基类（所有页面对象的父类）
    封装通用操作：等待/点击/输入/iframe切换/窗口切换/验证等
    核心特性：重试机制、失败截图、Allure步骤、多定位支持
    """

    def __init__(self, driver: webdriver.Remote):
        """
        初始化基类
        :param driver: Selenium驱动对象（由pytest夹具提供）
        """
        self.driver = driver
        # 从配置读取超时时间（多环境统一配置）
        self.implicitly_wait = config.get("browser.implicitly_wait", 10)
        self.explicit_wait = config.get("browser.explicit_wait", 20)
        # 设置隐式等待（全局元素等待）
        self.driver.implicitly_wait(self.implicitly_wait)

    # ==================== 核心等待方法 ====================
    @allure.step("等待元素可见：{locator}")
    def wait_element_visible(self, locator: dict | tuple | str | list, timeout: int = None):
        """
        显式等待元素可见（企业级核心等待方法，优先于隐式等待）
        :param locator: 元素定位器（支持多格式）
        :param timeout: 超时时间（默认使用配置的显式等待时间）
        :return: 定位到的元素对象
        """
        timeout = timeout or self.explicit_wait
        # 解析定位器
        parsed_locator = ElementLocator.parse_locator(locator)
        locator_desc = ElementLocator.get_locator_desc(locator)

        try:
            # 显式等待元素可见（可见=存在+显示）
            element = WebDriverWait(self.driver, timeout).until(
                EC.visibility_of_element_located(parsed_locator)
            )
            log.info(f"元素[{locator_desc}]已可见，等待耗时：{timeout}秒内")
            return element
        except TimeoutException:
            # 失败自动截图，附到Allure报告
            ScreenshotUtil.attach_to_allure(self.driver, f"等待元素[{locator_desc}]可见超时")
            raise ElementOperateException(locator, "等待可见", f"超时{timeout}秒，元素未显示")

    @allure.step("等待元素不可见：{locator}")
    def wait_element_invisible(self, locator: dict | tuple | str | list, timeout: int = None):
        """等待元素不可见（用于加载完成验证）"""
        timeout = timeout or self.explicit_wait
        parsed_locator = ElementLocator.parse_locator(locator)
        locator_desc = ElementLocator.get_locator_desc(locator)

        try:
            WebDriverWait(self.driver, timeout).until(
                EC.invisibility_of_element_located(parsed_locator)
            )
            log.info(f"元素[{locator_desc}]已不可见")
        except TimeoutException:
            ScreenshotUtil.attach_to_allure(self.driver, f"等待元素[{locator_desc}]不可见超时")
            raise ElementOperateException(locator, "等待不可见", f"超时{timeout}秒")

    # ==================== 核心操作方法 ====================
    @allure.step("点击元素：{locator}")
    @retry_on_failure(max_retries=3, delay=1)  # 失败重试3次
    def click(self, locator: dict | tuple | str | list):
        """
        点击元素（核心操作，带重试+失败截图）
        :param locator: 元素定位器
        """
        locator_desc = ElementLocator.get_locator_desc(locator)
        try:
            element = self.wait_element_visible(locator)
            element.click()
            log.info(f"点击元素[{locator_desc}]成功")
        except Exception as e:
            # 失败截图并抛出自定义异常
            ScreenshotUtil.attach_to_allure(self.driver, f"点击元素[{locator_desc}]失败")
            raise ElementOperateException(locator, "点击", str(e))

    @allure.step("输入文本：{locator}，文本：{text}")
    @retry_on_failure(max_retries=3, delay=1)
    def input_text(self, locator: dict | tuple | str | list, text: str):
        """
        输入文本（清空后输入，带重试+失败截图）
        :param locator: 元素定位器
        :param text: 要输入的文本
        """
        locator_desc = ElementLocator.get_locator_desc(locator)
        try:
            element = self.wait_element_visible(locator)
            element.clear()  # 清空输入框（避免残留内容）
            element.send_keys(text)
            log.info(f"向元素[{locator_desc}]输入文本：{text}")
        except Exception as e:
            ScreenshotUtil.attach_to_allure(self.driver, f"输入文本到[{locator_desc}]失败")
            raise ElementOperateException(locator, "输入", str(e))

    # ==================== 窗口/iframe切换 ====================
    @allure.step("切换到iframe：{locator}")
    def switch_to_iframe(self, locator: dict | tuple | str | list = None):
        """
        切换到iframe（企业级常用，如富文本编辑器、弹窗）
        :param locator: iframe定位器（None则切回主文档）
        """
        try:
            if locator:
                # 等待iframe可见并切换
                iframe_element = self.wait_element_visible(locator)
                self.driver.switch_to.frame(iframe_element)
                log.info(f"切换到iframe[{ElementLocator.get_locator_desc(locator)}]成功")
            else:
                # 切回主文档
                self.driver.switch_to.default_content()
                log.info("切换到主文档成功")
        except Exception as e:
            ScreenshotUtil.attach_to_allure(self.driver, "切换iframe失败")
            raise ElementOperateException(locator or "主文档", "切换iframe", str(e))

    @allure.step("切换到新窗口")
    def switch_to_new_window(self):
        """切换到新打开的窗口（如点击链接打开新标签页）"""
        try:
            windows = self.driver.window_handles  # 获取所有窗口句柄
            self.driver.switch_to.window(windows[-1])  # 切换到最后一个窗口（新窗口）
            log.info(f"切换到新窗口，句柄：{self.driver.current_window_handle}")
        except Exception as e:
            ScreenshotUtil.attach_to_allure(self.driver, "切换新窗口失败")
            raise ElementOperateException({}, "切换窗口", str(e))

    # ==================== 验证方法 ====================
    @allure.step("验证元素包含文本：{locator}，预期：{expected}")
    def verify_element_contains_text(self, locator: dict | tuple | str | list, expected: str) -> bool:
        """
        验证元素文本包含指定内容（核心验证方法）
        :param locator: 元素定位器
        :param expected: 预期包含的文本
        :return: 验证结果（True/False）
        """
        locator_desc = ElementLocator.get_locator_desc(locator)
        try:
            actual_text = self.get_element_text(locator)
            result = expected in actual_text
            # 记录验证结果到Allure
            allure.attach(
                f"预期包含：{expected}，实际文本：{actual_text}，验证结果：{result}",
                "文本验证结果"
            )
            if result:
                log.info(f"元素[{locator_desc}]文本包含[{expected}]，验证通过")
            else:
                log.error(f"元素[{locator_desc}]文本不包含[{expected}]，验证失败")
            return result
        except Exception as e:
            ScreenshotUtil.attach_to_allure(self.driver, f"验证元素[{locator_desc}]文本失败")
            raise ElementOperateException(locator, "验证文本", str(e))

    @allure.step("获取元素文本：{locator}")
    def get_element_text(self, locator: dict | tuple | str | list) -> str:
        """获取元素文本（去空格）"""
        locator_desc = ElementLocator.get_locator_desc(locator)
        try:
            element = self.wait_element_visible(locator)
            text = element.text.strip()  # 去首尾空格，避免格式问题
            log.info(f"获取元素[{locator_desc}]文本：{text}")
            return text
        except Exception as e:
            ScreenshotUtil.attach_to_allure(self.driver, f"获取元素[{locator_desc}]文本失败")
            raise ElementOperateException(locator, "获取文本", str(e))

    # ==================== 页面操作 ====================
    @allure.step("打开页面：{url}")
    def open_url(self, url: str):
        """打开指定URL（带失败截图）"""
        try:
            self.driver.get(url)
            log.info(f"打开页面成功：{url}")
        except Exception as e:
            ScreenshotUtil.attach_to_allure(self.driver, f"打开URL[{url}]失败")
            raise ElementOperateException({}, "打开URL", str(e))

    def get_current_url(self) -> str:
        """获取当前页面URL"""
        url = self.driver.current_url
        log.info(f"当前页面URL：{url}")
        return url

    @allure.step("刷新页面")
    def refresh_page(self):
        """刷新当前页面"""
        self.driver.refresh()
        log.info("页面刷新成功")