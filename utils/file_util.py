#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@作者: laity.wang
@创建日期: 2026/2/13 12:06
@文件名: file_util.py
@项目名称: ui_auto_test
@文件完整绝对路径: D:/LaityTest/ui_auto_test/utils\file_util.py
@文件相对项目路径:   # 可选，不需要可以删掉这行
@描述: 
"""
#### utils/file_util.py（文件操作工具）
import os
import json
import yaml
import openpyxl
from loguru import logger
from utils.config_util import config


class FileUtil:
    """
    企业级文件操作工具（核心：YAML/Excel/CSV读取+目录操作）
    支持多环境数据隔离、跨平台路径兼容
    """

    # ==================== 目录操作 ====================
    @staticmethod
    def create_dir(dir_path: str):
        """
        创建目录（不存在则创建，支持多级目录）
        :param dir_path: 目录路径
        """
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
            logger.info(f"创建目录成功：{dir_path}")

    @staticmethod
    def clear_dir(dir_path: str):
        """
        清空目录（保留目录本身，删除所有文件/子目录）
        :param dir_path: 目录路径
        """
        if not os.path.exists(dir_path):
            logger.warning(f"目录不存在，无需清空：{dir_path}")
            return

        for file_name in os.listdir(dir_path):
            file_path = os.path.join(dir_path, file_name)
            if os.path.isfile(file_path):
                os.remove(file_path)
                logger.debug(f"删除文件：{file_path}")
            elif os.path.isdir(file_path):
                # 递归清空子目录
                FileUtil.clear_dir(file_path)
                os.rmdir(file_path)
                logger.debug(f"删除子目录：{file_path}")
        logger.info(f"清空目录成功：{dir_path}")

    # ==================== 配置/数据读取 ====================
    @staticmethod
    def read_yaml(file_path: str) -> dict:
        """
        读取YAML文件（企业级首选配置格式）
        :param file_path: 文件路径
        :return: 解析后的字典
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"YAML文件不存在：{file_path}")

        with open(file_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}

        logger.info(f"读取YAML文件成功：{file_path}，数据大小：{len(str(data))}字节")
        return data

    @staticmethod
    def read_json(file_path: str) -> dict:
        """读取JSON文件"""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"JSON文件不存在：{file_path}")

        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        logger.info(f"读取JSON文件成功：{file_path}")
        return data

    @staticmethod
    def read_excel(file_path: str, sheet_name: str = None) -> list:
        """
        读取Excel文件（适合非技术人员维护）
        :param file_path: 文件路径
        :param sheet_name: 工作表名（默认第一个）
        :return: 数据列表（每行是字典，key为表头）
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Excel文件不存在：{file_path}")

        # 加载工作簿（只读模式，提升性能）
        workbook = openpyxl.load_workbook(file_path, read_only=True)
        # 选择工作表
        sheet = workbook[sheet_name] if sheet_name else workbook.active
        # 获取表头（第一行）
        headers = [cell.value for cell in sheet[1]]
        # 读取数据（从第二行开始）
        data = []
        for row in sheet.iter_rows(min_row=2, values_only=True):
            # 跳过空行
            if not any(row):
                continue
            # 行数据与表头拼接为字典
            row_data = dict(zip(headers, row))
            data.append(row_data)

        workbook.close()
        logger.info(f"读取Excel文件成功：{file_path}，数据行数：{len(data)}")
        return data

    @staticmethod
    def read_csv(file_path: str, encoding: str = "utf-8") -> list:
        """
        读取CSV文件（兜底方案，适合简单数据）
        :param file_path: 文件路径
        :param encoding: 编码（默认utf-8）
        :return: 数据列表
        """
        import csv
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"CSV文件不存在：{file_path}")

        data = []
        with open(file_path, "r", encoding=encoding) as f:
            reader = csv.DictReader(f)
            for row in reader:
                data.append(dict(row))

        logger.info(f"读取CSV文件成功：{file_path}，数据行数：{len(data)}")
        return data

    # ==================== 多环境数据读取 ====================
    @staticmethod
    def read_env_data(file_name: str, sheet_name: str = None, data_type: str = "yaml") -> dict | list:
        """
        按当前环境读取测试数据（核心：多环境数据隔离）
        :param file_name: 数据文件名（如baidu_search_cases.yaml）
        :param sheet_name: Excel工作表名（仅data_type=excel需要）
        :param data_type: 数据类型（yaml/excel/json/csv）
        :return: 测试数据
        """
        # 获取当前环境的测试数据目录
        project_root = config.get("project_root")
        env_data_dir = os.path.join(project_root, "data", config.get_env())
        FileUtil.create_dir(env_data_dir)

        # 拼接文件路径
        file_path = os.path.join(env_data_dir, file_name)
        if not os.path.exists(file_path):
            raise FileNotFoundError(
                f"当前环境[{config.get_env()}]的测试数据文件不存在：{file_path}"
            )

        # 按类型读取
        if data_type == "yaml":
            return FileUtil.read_yaml(file_path)
        elif data_type == "excel":
            return FileUtil.read_excel(file_path, sheet_name)
        elif data_type == "json":
            return FileUtil.read_json(file_path)
        elif data_type == "csv":
            return FileUtil.read_csv(file_path)
        else:
            raise ValueError(f"不支持的数据类型：{data_type}，支持：yaml/excel/json/csv")