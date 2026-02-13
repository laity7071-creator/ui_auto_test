#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@作者: laity.wang
@创建日期: 2026/2/13 12:07
@文件名: env_checker.py
@项目名称: ui_auto_test
@文件完整绝对路径: D:/LaityTest/ui_auto_test/utils\env_checker.py
@文件相对项目路径:   # 可选，不需要可以删掉这行
@描述: 
"""
#### utils/env_checker.py（环境健康检查）
import requests
from utils.config_util import config
from utils.log_util import log
from core.custom_exceptions import EnvConfigException


class EnvChecker:
    """
    企业级环境健康检查工具（测试前验证，避免白跑用例）
    核心：检查URL可访问、核心接口可用
    """

    @staticmethod
    def check_env_health():
        """检查当前环境健康状态（会话级夹具自动调用）"""
        env = config.get_env()
        log.info(f"========== 开始检查[{env}]环境健康状态 ==========")

        # 1. 检查首页URL可访问
        baidu_url = config.get("server.baidu_url")
        try:
            response = requests.get(baidu_url, timeout=10)
            response.raise_for_status()  # 非200状态码抛出异常
            log.info(f"✅ 首页URL可访问：{baidu_url}，状态码：{response.status_code}")
        except Exception as e:
            raise EnvConfigException(
                env,
                f"首页URL不可访问：{baidu_url}，异常：{e}"
            )

        # 2. 检查核心接口可用（示例：百度搜索接口）
        search_api = f"{baidu_url}/s"
        try:
            response = requests.get(search_api, params={"wd": "health_check"}, timeout=10)
            response.raise_for_status()
            log.info(f"✅ 核心接口可访问：{search_api}，状态码：{response.status_code}")
        except Exception as e:
            # 接口不可访问不阻塞测试，仅警告
            log.warning(f"⚠️ 核心接口访问警告：{search_api}，异常：{e}")

        log.info(f"========== [{env}]环境健康检查通过 ==========")