"""
生成并缓存本地唯一的学习者标识。

默认保存到 data/user_identity.json，内容包括：
{
    "user_id": "...",
    "device_label": "...",
    "created_at": "2025-11-11T19:30:00"
}
"""

from __future__ import annotations

import json
import os
import platform
import uuid
from datetime import datetime
from typing import Dict

IDENTITY_FILE = os.path.join("data", "user_identity.json")


def _ensure_directory(path: str) -> None:
    directory = os.path.dirname(path)
    if directory and not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)


def _generate_user_id() -> Dict[str, str]:
    node = uuid.getnode()
    seed = f"{node}-{platform.node()}-{platform.system()}-{platform.version()}"
    user_uuid = uuid.uuid5(uuid.NAMESPACE_DNS, seed)
    return {
        "user_id": str(user_uuid),
        "device_label": platform.node() or "unknown-device",
        "created_at": datetime.utcnow().isoformat(timespec="seconds"),
    }


def get_user_identity() -> Dict[str, str]:
    """获取或生成唯一学习者标识。"""
    _ensure_directory(IDENTITY_FILE)

    if os.path.exists(IDENTITY_FILE):
        try:
            with open(IDENTITY_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            if "user_id" in data:
                return data
        except (json.JSONDecodeError, OSError):
            pass  # 重新生成

    identity = _generate_user_id()
    try:
        with open(IDENTITY_FILE, "w", encoding="utf-8") as f:
            json.dump(identity, f, ensure_ascii=False, indent=2)
    except OSError:
        pass

    return identity





