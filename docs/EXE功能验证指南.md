# EXE功能验证指南

## 📋 验证清单

验证打包后的EXE是否正常工作，包括：
1. ✅ 云端连接是否正常
2. ✅ 本地数据采集是否工作
3. ✅ AI助手是否正常

---

## 🔍 方法1：使用验证脚本（推荐）

### 步骤1：运行验证脚本

```powershell
python verify_exe_features.py
```

### 步骤2：查看验证结果

脚本会检查：
- ✅ 数据库文件是否存在
- ✅ 最近的会话记录
- ✅ 最近的行为记录
- ✅ 日志文件
- ✅ 云端连接配置
- ✅ 云端连接测试
- ✅ 用户身份文件

---

## 🧪 方法2：手动验证

### 1. 验证云端连接

#### 步骤1：运行应用
- 双击运行 `dist\pychatcat.exe`
- 应用应该正常启动，不出现错误

#### 步骤2：查看控制台输出（如果有）
如果使用 `--console` 打包，应该看到：
```
🌐 云端行为上报已启用
📊 数据采集会话已开始: session_xxxxx
🌐 已连接云端会话: session_xxxxx
```

如果使用 `--noconsole` 打包，需要查看日志文件。

#### 步骤3：检查日志文件
```powershell
Get-Content logs\analytics_*.log | Select-Object -Last 20
```

应该看到：
- ✅ `Started session: session_xxxxx`
- ✅ `🌐 已连接云端会话: session_xxxxx`（如果云端连接成功）
- ✅ `Logged behavior: CP`（如果执行了代码操作）

#### 步骤4：测试云端连接
```powershell
python diagnose_cloud_connection_local.py
```

应该看到：
- ✅ `HTTP (备用) 连接成功!`
- ✅ `找到可用的连接地址!`

---

### 2. 验证本地数据采集

#### 步骤1：执行一些操作
在应用中执行以下操作：
1. **输入代码**：在代码编辑器中输入一些Python代码
2. **运行代码**：点击"运行"按钮执行代码
3. **使用AI助手**：向AI助手提问
4. **查看错误**：如果有错误，查看控制台的错误分析

#### 步骤2：等待1-2分钟
让数据采集系统有时间记录数据。

#### 步骤3：检查数据库
```powershell
python -c "import sqlite3; conn = sqlite3.connect('data/learning_analytics.db'); cursor = conn.cursor(); cursor.execute('SELECT COUNT(*) FROM learning_behaviors WHERE timestamp >= datetime(\"now\", \"-10 minutes\")'); print(f'最近10分钟的行为记录数: {cursor.fetchone()[0]}'); conn.close()"
```

应该看到：
- ✅ 行为记录数 > 0

#### 步骤4：查看详细数据
```powershell
python backend\view_data.py
```

应该看到：
- ✅ 总会话数 > 0
- ✅ 最近的学习行为记录
- ✅ 代码操作统计
- ✅ AI交互统计

---

### 3. 验证AI助手

#### 步骤1：打开AI助手面板
- 应用启动后，AI助手面板应该在右下角显示

#### 步骤2：发送测试消息
在AI助手输入框中输入：
```
你好，请介绍一下Python的基本语法
```

#### 步骤3：检查响应
- ✅ AI助手应该显示加载动画（"AI正在思考..."）
- ✅ 几秒后应该收到AI的回复
- ✅ 回复内容应该与Python相关

#### 步骤4：检查数据记录
运行验证脚本或查看日志，应该看到：
- ✅ `Logged AI interaction: ask_question`

---

## 📊 验证结果判断

### ✅ 全部正常
如果满足以下所有条件，说明功能正常：
1. ✅ 应用能正常启动
2. ✅ 云端连接成功（日志中有 `🌐 已连接云端会话`）
3. ✅ 数据库中有会话和行为记录
4. ✅ AI助手能正常回复
5. ✅ 日志文件中有相关记录

### ⚠️ 部分功能异常

#### 云端连接失败
**现象**：
- 日志中显示 `⚠️ 云端连接失败`
- `diagnose_cloud_connection_local.py` 显示连接失败

**可能原因**：
1. 服务器未运行
2. 网络被阻止（校园网/移动热点）
3. 防火墙阻止

**解决方案**：
1. 检查服务器状态：`python backend/diagnose_cloud_connection.py`（在服务器上运行）
2. 检查网络连接：`python diagnose_cloud_connection_local.py`
3. 本地数据采集不受影响，数据会保存在本地数据库

#### 本地数据采集未工作
**现象**：
- 数据库中没有记录
- 日志文件中没有行为记录

**可能原因**：
1. 集成代码未正确调用
2. 数据库路径错误
3. 权限问题

**解决方案**：
1. 检查日志文件：`Get-Content logs\analytics_*.log`
2. 检查数据库文件：`dir data\learning_analytics.db`
3. 运行诊断脚本：`python diagnose_data_collection.py`

#### AI助手无响应
**现象**：
- 发送消息后没有回复
- 一直显示"AI正在思考..."

**可能原因**：
1. DeepSeek API密钥问题
2. 网络连接问题
3. API配额用尽

**解决方案**：
1. 检查 `core/deepseek_client.py` 中的API密钥
2. 检查网络连接
3. 查看控制台错误信息（如果有）

---

## 🔧 快速验证命令

### 一键验证所有功能
```powershell
# 1. 运行验证脚本
python verify_exe_features.py

# 2. 检查云端连接
python diagnose_cloud_connection_local.py

# 3. 查看数据统计
python backend\view_data.py

# 4. 查看最新日志
Get-Content logs\analytics_*.log | Select-Object -Last 30
```

---

## 📝 验证报告模板

验证完成后，可以记录以下信息：

```
验证日期: 2025-11-15
EXE版本: pychatcat.exe

✅ 云端连接: 正常 / 失败
   - 连接地址: http://pychatcat.cloud
   - 连接状态: 成功 / 失败
   - 错误信息: (如果有)

✅ 本地数据采集: 正常 / 失败
   - 数据库文件: 存在 / 不存在
   - 会话记录数: X
   - 行为记录数: X
   - 日志文件: 存在 / 不存在

✅ AI助手: 正常 / 失败
   - 能发送消息: 是 / 否
   - 能收到回复: 是 / 否
   - 响应时间: X 秒

问题记录:
- (如果有问题，记录在这里)
```

---

## 💡 提示

1. **首次运行**：首次运行应用时，数据库和日志文件会自动创建，这是正常的
2. **等待时间**：数据采集是异步的，执行操作后需要等待几秒才能看到记录
3. **日志位置**：日志文件在 `logs/analytics_YYYYMMDD.log`
4. **数据库位置**：数据库文件在 `data/learning_analytics.db`
5. **云端连接**：即使云端连接失败，本地数据采集仍然工作，数据会保存在本地




