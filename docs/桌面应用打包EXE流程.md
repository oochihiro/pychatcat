# 桌面应用打包 EXE 操作记录

本文记录从源码打包到 EXE 分发的完整操作流程，便于后续汇报或团队复用。

---

## 1. 环境要求

- Windows 10/11
- 已安装 Python 3.9 及以上版本（当前为 3.11）
- 项目源码目录：`E:\cursor_web`
- 已安装依赖：`pip install -r requirements.txt`

> 建议在命令提示符或 PowerShell 中执行以下操作，所有命令均假设当前工作目录为 `E:\cursor_web`。

---

## 2. 关键新增文件

- `pyproject.toml`：定义包信息、依赖和命令行入口
- `run_app.py`：统一的启动入口（兼容源码运行 / wheel 安装 / EXE 打包）

以上文件已提交到仓库，无需额外修改。

---

## 3. Wheel 包构建（可选，用于 pip 分发）

1. 安装构建工具
   ```powershell
   python -m pip install --upgrade build
   ```

2. 构建并生成发行包
   ```powershell
   python -m build
   ```
   输出文件位于 `dist/` 目录，例如：
   - `pychatcat_assistant-0.1.0-py3-none-any.whl`
   - `pychatcat_assistant-0.1.0.tar.gz`

3. 本机验证（可确保依赖完整）
   ```powershell
   python -m pip install --upgrade --force-reinstall .\dist\pychatcat_assistant-0.1.0-py3-none-any.whl
   python -m run_app
   ```

---

## 4. 打包 EXE 步骤（重点）

1. 安装 PyInstaller（仅需一次）
   ```powershell
   python -m pip install --upgrade pyinstaller
   ```

2. 打包命令
   ```powershell
   python -m PyInstaller --noconsole --onefile --name PyChatCat --hidden-import main run_app.py
   ```
   说明：
   - `--noconsole`：隐藏黑色控制台窗口
   - `--onefile`：打包成单个 EXE
   - `--hidden-import main`：显式包含 `main.py`
   - 输出文件：`dist/PyChatCat.exe`

3. 可选：自定义图标（需准备 .ico 文件）
   ```powershell
   python -m PyInstaller --noconsole --onefile --icon .\resources\cat.ico --name PyChatCat --hidden-import main run_app.py
   ```

4. 测试 EXE
   - 双击 `dist/PyChatCat.exe`，确认界面正常启动
   - 控制台不再出现 `No module named main` 等错误提示

5. 分发
   - 仅需分发 `dist/PyChatCat.exe`
   - 可压缩成 ZIP 后分享给学生，无需他们安装 Python

---

## 5. 常见问题与解决方案

| 问题                                   | 现象/提示                             | 解决方案                                   |
|----------------------------------------|----------------------------------------|--------------------------------------------|
| `pyinstaller` 不是内部或外部命令       | `CommandNotFoundException: pyinstaller`| 使用 `python -m PyInstaller ...`           |
| 找不到 `main` 模块                     | 弹窗 `No module named main`            | 打包命令添加 `--hidden-import main`       |
| EXE 运行后无输出/闪退                  | 依赖缺失或加载失败                     | 先通过 `python -m run_app` 确认依赖无误   |
| 想更新 EXE                             | 源码有改动后重新执行第 4 步打包命令    | 新 EXE 会覆盖旧文件                        |
| 想同时提供 wheel + EXE                | 先执行第 3 步，再执行第 4 步           | 两种分发方式互不影响                       |

---

## 6. 桌面应用连接云端后端的配置

### 6.1 默认行为
- AI 助手通过 `core/deepseek_client.py` 直接调用 DeepSeek 官方 API（已内置密钥和 `https://api.deepseek.com/v1` 地址），无需额外配置。
- 数据采集默认使用本地 SQLite，可选择保留或改为上传到云端。

### 6.2 将行为日志发往云端后端
若需要把学习行为同步到 `http://pychatcat.cloud` 上的 Flask 后端，可在 `core/sqlite_analytics.py` 中引入网络上报逻辑。推荐做法：

1. **启用已有 REST 接口**（已在 `backend/app.py` 实现）：
   - `/api/sessions`
   - `/api/sessions/<session_id>/behaviors`
   - `/api/sessions/<session_id>/code-operations`
   - `/api/sessions/<session_id>/ai-interactions`
   - `/api/sessions/<session_id>/errors`

2. **本地应用端新增上报代码**（示例伪代码，可扩展到 `SQLiteIntegration` 中）：
   ```python
   import requests

   BACKEND_URL = "https://pychatcat.cloud"  # 或 http://

   def upload_behavior(session_id, payload):
       url = f"{BACKEND_URL}/api/sessions/{session_id}/behaviors"
       try:
           requests.post(url, json=payload, timeout=5)
       except requests.RequestException as exc:
           print(f"行为上报失败：{exc}")
   ```

3. **配置位置说明**
   - 如果要全局修改后端地址，可在 `config/backend_config.py`（可新建）统一管理，例如：
     ```python
     BACKEND_URL = "https://pychatcat.cloud"
     ```
     然后在 `integrations/sqlite_integration.py` 或新的网络集成模块中引用。
   - 当前版本尚未内置该配置，后续若要切换后端，只需在上述常量位置把地址改为 `http://pychatcat.cloud` 并重新打包 EXE。

4. **验证方式**
   - 桌面应用运行一次操作后，在服务器上执行：
     ```bash
     tail -n 20 /www/wwwlogs/backend.log
     tail -n 20 /www/wwwroot/pychatcat.cloud/backend/gunicorn.log
     ```
   - 查看是否有对应的 API 请求记录。

---

## 7. 汇报建议

- **背景**：说明项目原为 Python + Tkinter 桌面应用，需要支持离线安装及批量分发。
- **过程**：列出本指南第 3、4、6 节的关键步骤，配上构建日志或截图（如打包完成、EXE 运行成功的画面）。
- **成果**：展示最终产物（`PyChatCat.exe`）、云端接口调用情况、学生端安装说明等。
- **下一步计划**：若需接入云端数据中心，可引用第 6 节的网络上报方案。

---

## 8. 联系方式
若后续需要扩展功能（如自动更新、安装向导、云端配置可视化等），建议保留当前打包流程的命令记录，方便快速迭代。需要进一步支持时，请在文档中标注新增需求点。  

---

**最后更新时间：** 2025-11-11




