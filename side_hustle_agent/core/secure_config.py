"""
安全配置存储

API Key 加密存储
"""

import os
import hashlib
import base64
import json
import secrets
from pathlib import Path
from typing import Any

try:
    from cryptography.fernet import Fernet
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
except ImportError:
    # 如果没有 cryptography，使用简单加密（仅作为演示）
    Fernet = None


class SecureConfig:
    """安全配置管理"""

    def __init__(self, config_path: str | None = None):
        if config_path is None:
            config_path = os.path.join(os.path.dirname(__file__), "config.json")
        self.config_path = Path(config_path)
        self._config: dict[str, Any] = {}
        self._fernet = None
        self._load_or_create()

    def _load_or_create(self):
        """加载或创建配置"""
        if self.config_path.exists():
            try:
                with open(self.config_path, "r") as f:
                    self._config = json.load(f)
            except:
                self._config = {}

        # 生成或加载密钥
        key_file = self.config_path.with_suffix(".key")
        if key_file.exists():
            with open(key_file, "rb") as f:
                key = f.read()
        else:
            key = secrets.token_bytes(32)
            with open(key_file, "wb") as f:
                f.write(key)

        if Fernet:
            self._fernet = Fernet(self._derive_key(key))
        else:
            self._fernet = SimpleCipher(key)

    def _derive_key(self, key: bytes) -> bytes:
        """从密码派生密钥"""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=b"side_hustle_agent_salt",
            iterations=100000,
        )
        return base64.urlsafe_b64encode(kdf.derive(key))

    def get(self, key: str, default: Any = None) -> Any:
        """获取配置值"""
        return self._config.get(key, default)

    def set(self, key: str, value: Any) -> None:
        """设置配置值"""
        self._config[key] = value

    def set_encrypted(self, key: str, value: str) -> None:
        """设置加密值"""
        if self._fernet:
            encrypted = self._fernet.encrypt(value.encode())
            self._config[key] = base64.b64encode(encrypted).decode()
        else:
            self._config[key] = value

    def get_decrypted(self, key: str, default: str = "") -> str:
        """获取解密值"""
        encrypted = self._config.get(key)
        if not encrypted:
            return default

        if self._fernet:
            try:
                data = base64.b64decode(encrypted.encode())
                return self._fernet.decrypt(data).decode()
            except:
                return default
        else:
            return encrypted

    def save(self) -> None:
        """保存配置到文件"""
        with open(self.config_path, "w") as f:
            json.dump(self._config, f, indent=2, ensure_ascii=False)

    def get_all(self) -> dict:
        """获取所有配置（敏感值除外）"""
        result = dict(self._config)
        # 不返回实际 API Key
        if "llm_api_key" in result:
            result["llm_api_key"] = "********" if result["llm_api_key"] else ""
        return result


class SimpleCipher:
    """简单加密（用于没有 cryptography 的情况）"""

    def __init__(self, key: bytes):
        self.key = key

    def encrypt(self, data: bytes) -> bytes:
        result = bytearray()
        for i, b in enumerate(data):
            result.append(b ^ self.key[i % len(self.key)])
        return bytes(result)

    def decrypt(self, data: bytes) -> bytes:
        return self.encrypt(data)  # XOR 是自逆的


# 全局配置实例
_config: SecureConfig | None = None


def get_secure_config() -> SecureConfig:
    """获取安全配置单例"""
    global _config
    if _config is None:
        _config = SecureConfig()
    return _config