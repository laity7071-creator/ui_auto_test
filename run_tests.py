#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@作者: laity.wang
@创建日期: 2026/2/13 12:10
@文件名: run_tests.py
@项目名称: ui_auto_test
@文件完整绝对路径: D:/LaityTest/ui_auto_test\run_tests.py
@文件相对项目路径:   # 可选，不需要可以删掉这行
@描述: 
"""
## 十四、测试执行入口：run_tests.py
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
企业级UI自动化测试 - 统一执行入口
支持：
- 多环境并行/单环境运行
- 多标签筛选（smoke/regression/cross_env）
- 多报告（HTML+Allure）
- 多线程并发
- 自动生成报告、邮件发送（可扩展）
"""
import sys
import os
import pytest
import argparse

from utils.config_util import config
from utils.log_util import log
from utils.file_util import FileUtil

def main():
    # 1. 命令行参数解析
    parser = argparse.ArgumentParser(description="企业级UI自动化测试执行器")
    parser.add_argument("--env", default="test", help="指定运行环境：dev/test/prod，默认test")
    parser.add_argument("--tag", default="smoke", help="指定用例标签：smoke/regression/cross_env，默认smoke")
    parser.add_argument("--report", default="all", help="报告类型：html/allure/both，默认both")
    parser.add_argument("--thread", default=2, type=int, help="并发线程数，默认2")
    args = parser.parse_args()

    # 2. 设置环境变量（供ConfigUtil读取）
    os.environ["TEST_ENV"] = args.env

    # 3. 加载配置
    config.load_config(args.env)
    env = args.env
    tag = args.tag
    thread = args.thread

    # 4. 准备报告目录
    env_report_dir = os.path.join(config.get("report.html_dir"), env)
    env_allure_dir = config.get("report.allure_dir")
    FileUtil.create_dir(env_report_dir)
    FileUtil.create_dir(env_allure_dir)

    html_report_path = os.path.join(env_report_dir, "test_report.html")

    # 5. 构造pytest执行参数
    pytest_args = [
        "-v",                      # 详细输出
        "-s",                      # 打印print/log
        f"-n={thread}",            # 多线程
        "--reruns=1",              # 失败重跑1次
        "--reruns-delay=2",        # 重跑间隔2秒
        f"-m={tag}",                # 按标签执行
        "./test_cases",            # 用例目录
    ]

    # HTML报告
    if args.report in ["html", "both"]:
        pytest_args.append(f"--html={html_report_path}")
        pytest_args.append("--self-contained-html")

    # Allure报告
    if args.report in ["allure", "both"]:
        pytest_args.append(f"--alluredir={env_allure_dir}")
        pytest_args.append("--clean-alluredir")

    # 6. 开始执行
    log.info("=" * 60)
    log.info(f"          启动测试")
    log.info(f"  环境：{env}")
    log.info(f"  标签：{tag}")
    log.info(f"  线程：{thread}")
    log.info(f"  报告：{args.report}")
    log.info("=" * 60)

    exit_code = pytest.main(pytest_args)

    # 7. 执行完成
    if exit_code == 0:
        log.info("✅ 所有用例执行通过！")
    else:
        log.error("❌ 部分/全部用例执行失败！")

    sys.exit(exit_code)

if __name__ == "__main__":
    main()