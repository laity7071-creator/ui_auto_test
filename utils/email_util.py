#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@作者: laity.wang
@创建日期: 2026/2/13 12:07
@文件名: email_util.py
@项目名称: ui_auto_test
@文件完整绝对路径: D:/LaityTest/ui_auto_test/utils\email_util.py
@文件相对项目路径:   # 可选，不需要可以删掉这行
@描述: 
"""
#### utils/email_util.py（邮件推送）
import yagmail
import os
from utils.config_util import config
from utils.log_util import log


class EmailUtil:
    """
    企业级邮件推送工具（测试完成后自动发送报告）
    配置来自环境敏感配置（加密存储）
    """

    @classmethod
    def send_test_report(cls, report_path: str, subject: str = None):
        """
        发送测试报告邮件
        :param report_path: 报告文件路径（HTML/Allure）
        :param subject: 邮件主题
        """
        # 1. 读取邮件配置（敏感配置，已解密）
        email_config = config.get("email", {})
        sender = email_config.get("sender")
        password = email_config.get("password")
        recipients = email_config.get("recipients", [])
        smtp_server = email_config.get("smtp_server")
        smtp_port = email_config.get("smtp_port", 465)

        # 2. 校验配置
        if not all([sender, password, recipients, smtp_server]):
            log.error("邮件配置缺失，无法发送报告")
            return

        # 3. 配置邮件主题/内容
        env = config.get_env()
        subject = subject or f"[{env}]UI自动化测试报告_{os.path.basename(report_path)}"
        content = [
            f"您好！\n[{env}]环境UI自动化测试已完成，报告文件见附件。",
            f"测试环境：{env}",
            f"报告路径：{report_path}",
            "请查收，谢谢！"
        ]

        # 4. 发送邮件
        try:
            # 初始化邮件客户端
            yag = yagmail.SMTP(
                user=sender,
                password=password,
                host=smtp_server,
                port=smtp_port,
                smtp_ssl=True
            )
            # 发送邮件（带附件）
            yag.send(
                to=recipients,
                subject=subject,
                contents=content,
                attachments=report_path
            )
            log.info(f"✅ 测试报告邮件发送成功，收件人：{recipients}")
        except Exception as e:
            log.error(f"❌ 测试报告邮件发送失败：{e}")