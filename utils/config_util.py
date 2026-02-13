#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@作者: laity.wang
@创建日期: 2026/2/13 12:05
@文件名: config_util.py
@项目名称: ui_auto_test
@文件完整绝对路径: D:/LaityTest/ui_auto_test/utils\config_util.py
@文件相对项目路径:   # 可选，不需要可以删掉这行
@描述: 
"""
#### utils/config_util.py（多环境配置读取+敏感配置解密）
import os
import yaml
from cryptography.fernet import Fernet
from enums.env_type import EnvType
from core.custom_exceptions import EnvConfigException
from utils.log_util import log

# 加密密钥（企业级需放在环境变量/配置中心，切勿硬编码！）
# 生成密钥命令：python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
ENCRYPT_KEY = os.getenv("ENCRYPT_KEY", "gAAAAABl7eQZ-xxxxxxx-xxxxxxx-xxxxxxx")
cipher = Fernet(ENCRYPT_KEY.encode("utf-8"))


class ConfigUtil:
    """
    企业级多环境配置工具（核心：多环境隔离+敏感配置解密+配置校验）
    优先级：命令行参数 > 系统环境变量 > 默认test
    """
    _config = None  # 单例存储配置
    _current_env = None  # 当前环境

    @classmethod
    def load_config(cls, env: str = None) -> dict:
        """
        加载配置（核心方法）
        :param env: 环境（dev/test/prod）
        :return: 合并后的配置字典
        """
        # 单例模式：已加载且环境未变，直接返回
        if cls._config and cls._current_env == env:
            return cls._config

        # 1. 确定当前环境
        cls._current_env = env or os.getenv("TEST_ENV", EnvType.TEST.value)
        if cls._current_env not in EnvType.get_all_envs():
            raise EnvConfigException(
                cls._current_env,
                f"无效环境，支持：{EnvType.get_all_envs()}"
            )

        # 2. 定义路径（跨平台兼容）
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        global_config_path = os.path.join(project_root, "config", "global_config.yaml")
        env_core_path = os.path.join(project_root, "config", "env", cls._current_env, "env_config.yaml")
        env_secret_path = os.path.join(project_root, "config", "env", cls._current_env, "secret_config.yaml")

        # 3. 加载全局配置
        cls._load_file(global_config_path, "全局")
        with open(global_config_path, "r", encoding="utf-8") as f:
            global_config = yaml.safe_load(f) or {}

        # 4. 加载环境核心配置
        cls._load_file(env_core_path, f"{cls._current_env}环境核心")
        with open(env_core_path, "r", encoding="utf-8") as f:
            env_core_config = yaml.safe_load(f) or {}

        # 5. 加载敏感配置（自动解密）
        env_secret_config = {}
        if os.path.exists(env_secret_path):
            cls._load_file(env_secret_path, f"{cls._current_env}环境敏感")
            with open(env_secret_path, "r", encoding="utf-8") as f:
                secret_data = yaml.safe_load(f) or {}
                env_secret_config = cls._decrypt_secret_config(secret_data)

        # 6. 合并配置（优先级：敏感配置 > 环境核心 > 全局）
        cls._config = {**global_config, **env_core_config, **env_secret_config}
        cls._config["env"] = cls._current_env  # 记录当前环境
        cls._config["project_root"] = project_root  # 项目根路径

        # 7. 配置校验（企业级必备，避免核心配置缺失）
        cls._validate_env_config()

        log.info(f"✅ 加载[{cls._current_env}]环境配置完成")
        return cls._config

    @classmethod
    def _load_file(cls, file_path: str, file_desc: str):
        """内部方法：检查文件是否存在，不存在则抛出异常"""
        if not os.path.exists(file_path):
            raise EnvConfigException(
                cls._current_env,
                f"{file_desc}配置文件缺失：{file_path}"
            )
        log.info(f"加载{file_desc}配置文件：{file_path}")

    @classmethod
    def _decrypt_secret_config(cls, secret_data: dict) -> dict:
        """
        内部方法：解密敏感配置（仅解密ENC(xxx)格式的内容）
        :param secret_data: 原始敏感配置
        :return: 解密后的配置
        """
        decrypted_data = {}
        for key, value in secret_data.items():
            if isinstance(value, dict):
                # 递归解密嵌套字典
                decrypted_data[key] = cls._decrypt_secret_config(value)
            elif isinstance(value, str) and value.startswith("ENC(") and value.endswith(")"):
                # 解密ENC(xxx)格式的内容
                try:
                    ciphertext = value[4:-1].encode("utf-8")
                    decrypted_value = cipher.decrypt(ciphertext).decode("utf-8")
                    decrypted_data[key] = decrypted_value
                    log.debug(f"解密敏感配置[{key}]成功")
                except Exception as e:
                    raise EnvConfigException(
                        cls._current_env,
                        f"敏感配置[{key}]解密失败：{e}"
                    )
            else:
                # 非加密内容直接保留
                decrypted_data[key] = value
        return decrypted_data

    @classmethod
    def _validate_env_config(cls):
        """内部方法：校验核心配置是否缺失"""
        required_keys = [
            "server.baidu_url",
            "browser.type",
            "log.dir",
            "screenshot.dir"
        ]
        for key in required_keys:
            if not cls.get(key):
                raise EnvConfigException(
                    cls._current_env,
                    f"核心配置缺失：{key}"
                )
        log.info(f"✅ [{cls._current_env}]环境配置校验通过")

    # ==================== 对外接口 ====================
    @classmethod
    def get_env(cls) -> str:
        """获取当前环境"""
        if not cls._current_env:
            cls.load_config()
        return cls._current_env

    @classmethod
    def get(cls, key: str, default=None):
        """
        获取配置值（支持嵌套key，如"server.baidu_url"）
        :param key: 配置键（支持嵌套）
        :param default: 默认值
        :return: 配置值
        """
        if not cls._config:
            cls.load_config()

        # 解析嵌套key（如"server.baidu_url"→["server", "baidu_url"]）
        keys = key.split(".")
        value = cls._config
        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default

    @classmethod
    def get_env_path(cls, sub_path: str = "") -> str:
        """获取当前环境的目录路径（如config/env/dev）"""
        project_root = cls.get("project_root")
        env_path = os.path.join(project_root, "config", "env", cls.get_env())
        return os.path.join(env_path, sub_path) if sub_path else env_path


# 初始化配置工具（全局单例）
config = ConfigUtil()