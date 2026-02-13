#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@作者: laity.wang
@创建日期: 2026/2/13 12:09
@文件名: conftest.py
@项目名称: ui_auto_test
@文件完整绝对路径: D:/LaityTest/ui_auto_test/test_cases\conftest.py
@文件相对项目路径:   # 可选，不需要可以删掉这行
@描述: 
"""
### test_cases/conftest.py
"""
pytest 全局夹具/钩子定义文件
企业级作用：
1. 测试前环境初始化（健康检查、清空目录）
2. 浏览器驱动全局管理（单例、自动管理驱动）
3. 用例失败自动截图
4. 用例标签/排序管理
5. 全局前后置
"""
import os
import pytest
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.microsoft import EdgeChromiumDriverManager

from enums.browser_type import BrowserType
from utils.config_util import config
from utils.log_util import log
from utils.file_util import FileUtil
from utils.screenshot_util import ScreenshotUtil
from utils.env_checker import EnvChecker
from page_objects.baidu.baidu_home import BaiduHomePage
from page_objects.baidu.baidu_result import BaiduResultPage

# ======================== 会话级全局初始化 ========================
@pytest.fixture(scope="session", autouse=True)
def global_init():
    """
    整个测试会话只执行一次的全局初始化
    autouse=True：自动运行，无需用例主动调用
    """
    log.info("=" * 60)
    log.info("          企业级UI自动化测试 - 全局初始化开始")
    log.info("=" * 60)

    # 1. 加载配置
    config.load_config()
    env = config.get_env()
    log.info(f"当前运行环境：【{env}】")

    # 2. 环境健康检查（必做，防止环境挂了白跑）
    EnvChecker.check_env_health()

    # 3. 清空历史截图、报告（保证本次结果干净）
    screenshot_dir = os.path.join(config.get("screenshot.dir"), env)
    report_html_dir = os.path.join(config.get("report.html_dir"), env)
    FileUtil.clear_dir(screenshot_dir)
    FileUtil.clear_dir(report_html_dir)
    log.info("历史截图/报告已清空")

    log.info("=" * 60)
    log.info("          全局初始化完成，开始执行测试用例")
    log.info("=" * 60)

    # 测试执行完毕后（后置）
    yield

    log.info("=" * 60)
    log.info("          所有用例执行完毕，测试会话结束")
    log.info("=" * 60)

# ======================== 浏览器驱动夹具 ========================
@pytest.fixture(scope="session")
def browser():
    """
    浏览器驱动全局夹具（会话级，整个测试只启一次浏览器）
    企业级优点：
    - 自动下载对应版本驱动
    - 统一浏览器配置
    - 用完自动关闭，不残留进程
    """
    driver = None
    browser_type = config.get("browser.type", BrowserType.CHROME.value).lower()

    try:
        # ========== Chrome 浏览器 ==========
        if browser_type == BrowserType.CHROME.value:
            chrome_options = webdriver.ChromeOptions()
            # 去掉“自动化控制”提示条
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option("useAutomationExtension", False)
            # 通用优化
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--start-maximized")
            chrome_options.add_argument("--no-sandbox")

            # 自动安装并启动Chrome
            driver = webdriver.Chrome(
                executable_path=ChromeDriverManager().install(),
                options=chrome_options
            )
            log.info("✅ Chrome 浏览器启动成功")

        # ========== Edge 浏览器 ==========
        elif browser_type == BrowserType.EDGE.value:
            edge_options = webdriver.EdgeOptions()
            edge_options.add_argument("--start-maximized")
            driver = webdriver.Edge(
                executable_path=EdgeChromiumDriverManager().install(),
                options=edge_options
            )
            log.info("✅ Edge 浏览器启动成功")

        else:
            raise ValueError(f"暂不支持浏览器类型：{browser_type}")

        # 隐式等待
        driver.implicitly_wait(config.get("browser.implicitly_wait", 10))
        yield driver

    # 异常捕获
    except Exception as e:
        log.critical(f"❌ 浏览器启动失败：{str(e)}")
        raise

    # 最终关闭浏览器
    finally:
        if driver:
            driver.quit()
            log.info("✅ 浏览器已安全关闭")

# ======================== 业务页面夹具 ========================
@pytest.fixture(scope="function")
def baidu_home_page(browser):
    """百度首页夹具：每个用例执行前打开首页"""
    page = BaiduHomePage(browser)
    page.open_baidu_home()
    yield page

@pytest.fixture(scope="function")
def baidu_result_page(browser):
    """搜索结果页夹具"""
    yield BaiduResultPage(browser)

# ======================== 用例失败自动截图钩子 ========================
@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """
    pytest 原生钩子：用例执行结果监听
    作用：用例失败 → 自动截图 → 自动进Allure报告
    """
    outcome = yield
    report = outcome.get_result()

    # 只在“用例调用阶段”失败时截图
    if report.when == "call" and report.failed:
        try:
            # 从用例参数里取出 driver
            driver = item.funcargs["browser"]
            ScreenshotUtil.attach_to_allure(driver, f"失败用例：{item.name}")
            log.error(f"❌ 用例【{item.name}】执行失败，已自动截图")
        except Exception as e:
            log.error(f"失败截图异常：{str(e)}")

# ======================== 用例排序/标签 ========================
def pytest_collection_modifyitems(items):
    """
    用例收集完成后的处理：
    1. 按用例名字母排序
    2. 自动打标签（冒烟/回归）
    """
    # 按名字排序
    items.sort(key=lambda x: x.name)

    # 自动给冒烟用例打标记
    for item in items:
        if "smoke" in item.nodeid:
            item.add_marker(pytest.mark.smoke)
        if "regression" in item.nodeid:
            item.add_marker(pytest.mark.regression)
        if "cross_env" in item.nodeid:
            item.add_marker(pytest.mark.cross_env)

    log.info(f"共加载用例：{len(items)} 条")