"""
云端后端配置。

可以通过环境变量 `PYCHATCAT_BACKEND_URL` 覆盖默认地址。
"""

import os

# 默认的云端后端地址
# 注意：如果HTTPS端口443被阻止（校园网/移动热点常见），请使用HTTP
_DEFAULT_URL = os.environ.get("PYCHATCAT_BACKEND_URL", "http://pychatcat.cloud").strip()

# 是否启用云端行为上报
ENABLE_CLOUD_ANALYTICS = os.environ.get("PYCHATCAT_ENABLE_CLOUD", "true").lower() == "true"

# 请求超时时间（秒）
REQUEST_TIMEOUT = float(os.environ.get("PYCHATCAT_REQUEST_TIMEOUT", "5"))

# 规范化地址（去除末尾斜杠）
BACKEND_URL = _DEFAULT_URL.rstrip("/") if _DEFAULT_URL else ""


