"""
云端行为日志上报客户端。

将本地采集的学习行为通过 REST API 上传到后端。
"""

from __future__ import annotations

import threading
from typing import Any, Dict, Optional

import requests

from config.backend_config import BACKEND_URL, ENABLE_CLOUD_ANALYTICS, REQUEST_TIMEOUT
from core.user_identity import get_user_identity


class CloudAnalyticsClient:
    """与云端后端交互的客户端。"""

    def __init__(self) -> None:
        self.enabled = ENABLE_CLOUD_ANALYTICS and bool(BACKEND_URL)
        self.base_url = BACKEND_URL
        self.session_id: Optional[str] = None
        self.user_identity = get_user_identity()
        self.lock = threading.Lock()

    # ---- 会话管理 ---------------------------------------------------------
    def start_session(self, alias: Optional[str] = None) -> None:
        if not self.enabled or self.session_id:
            return

        payload = {
            "user_id": self.user_identity.get("user_id"),
            "device_label": self.user_identity.get("device_label"),
        }
        if alias:
            payload["alias"] = alias
        self._post_async("/api/sessions", payload, save_session=True)

    def end_session(self) -> None:
        # 目前后端不要求显式结束会话，这里只清理本地状态
        if self.session_id:
            self.session_id = None

    # ---- 行为上报 ---------------------------------------------------------
    def log_behavior(self, behavior_code: str, duration: float = None, additional_data: Dict[str, Any] = None) -> None:
        if not self._ready():
            return

        payload = {
            "behavior_code": behavior_code,
            "duration": duration,
            "additional_data": additional_data or {},
        }
        endpoint = f"/api/sessions/{self.session_id}/behaviors"
        self._post_async(endpoint, payload)

    def log_code_operation(
        self,
        operation_type: str,
        code: str = None,
        success: bool = True,
        error_message: str = None,
        execution_time: float = None,
    ) -> None:
        if not self._ready():
            return

        payload = {
            "operation_type": operation_type,
            "code": code,
            "success": success,
            "execution_time": execution_time,
            "additional_data": {"error_message": error_message} if error_message else {},
        }
        endpoint = f"/api/sessions/{self.session_id}/code-operations"
        self._post_async(endpoint, payload)

    def log_ai_interaction(
        self,
        interaction_type: str,
        question: str = None,
        response: str = None,
        response_time: float = None,
        additional_data: Dict[str, Any] = None,
    ) -> None:
        if not self._ready():
            return

        payload = {
            "interaction_type": interaction_type,
            "question": question,
            "response": response,
            "response_time": response_time,
            "additional_data": additional_data or {},
        }
        endpoint = f"/api/sessions/{self.session_id}/ai-interactions"
        self._post_async(endpoint, payload)

    def log_error_analysis(
        self,
        error_type: str,
        error_line: int,
        error_message: str,
        fix_attempts: int = 0,
        fix_success: bool = False,
        additional_data: Dict[str, Any] = None,
    ) -> None:
        if not self._ready():
            return

        payload = {
            "error_type": error_type,
            "error_line": error_line,
            "error_message": error_message,
            "fix_attempts": fix_attempts,
            "fix_success": fix_success,
            "additional_data": additional_data or {},
        }
        endpoint = f"/api/sessions/{self.session_id}/errors"
        self._post_async(endpoint, payload)

    # ---- 工具方法 ---------------------------------------------------------
    def _ready(self) -> bool:
        return self.enabled and bool(self.session_id)

    def _post_async(self, endpoint: str, payload: Dict[str, Any], save_session: bool = False) -> None:
        if not self.enabled:
            return

        def worker() -> None:
            try:
                url = f"{self.base_url}{endpoint}"
                response = requests.post(url, json=payload, timeout=REQUEST_TIMEOUT)
                response.raise_for_status()
                if save_session:
                    data = response.json()
                    session_id = data.get("session_id")
                    if session_id:
                        with self.lock:
                            self.session_id = session_id
                            print(f"🌐 已连接云端会话: {session_id}")
            except requests.exceptions.ConnectionError as exc:
                # 连接错误（服务器未运行、端口被阻止、防火墙等）
                error_msg = str(exc)
                if "10061" in error_msg or "actively refused" in error_msg.lower():
                    # 只在第一次连接失败时显示详细提示
                    if not hasattr(self, '_connection_error_shown'):
                        self._connection_error_shown = True
                        print(f"⚠️ 云端连接失败: 无法连接到服务器 {self.base_url}")
                        print(f"   可能原因: 1) 服务器未运行  2) 网络被阻止(校园网/移动热点)  3) 防火墙阻止")
                        print(f"   💡 本地数据采集不受影响，数据将保存在本地数据库")
                else:
                    print(f"⚠️ 云端上报失败（{endpoint}）: {exc}")
            except requests.exceptions.Timeout as exc:
                print(f"⚠️ 云端上报超时（{endpoint}）: 请求超过 {REQUEST_TIMEOUT} 秒")
            except requests.exceptions.SSLError as exc:
                print(f"⚠️ 云端SSL错误（{endpoint}）: {exc}")
                print(f"   💡 可能是SSL证书问题，请检查服务器配置")
            except requests.RequestException as exc:
                print(f"⚠️ 云端上报失败（{endpoint}）: {exc}")

        threading.Thread(target=worker, daemon=True).start()


# 供外部引用的便捷函数
def create_cloud_client() -> CloudAnalyticsClient:
    return CloudAnalyticsClient()


