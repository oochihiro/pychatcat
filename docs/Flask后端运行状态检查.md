# Flask 后端运行状态检查指南

## 📊 进程状态解读

### `ps aux | grep gunicorn` 输出说明

```
root     3579  0.0  1.1  28748 23924 ?    S    Nov13   0:01 /usr/bin/python3 /usr/local/bin/gunicorn -c /www/wwwroot/.../gunicorn_conf.py app:app
www      3580  0.0  3.8 257884 77088 ?    S1   Nov13   0:01 /usr/bin/python3 /usr/local/bin/gunicorn -c /www/wwwroot/.../gunicorn_conf.py app:app
www      3581  0.0  3.8 258908 77580 ?    S1   Nov13   0:01 /usr/bin/python3 /usr/local/bin/gunicorn -c /www/wwwroot/.../gunicorn_conf.py app:app
www      3582  0.0  3.8 257884 77120 ?    S1   Nov13   0:01 /usr/bin/python3 /usr/local/bin/gunicorn -c /www/wwwroot/.../gunicorn_conf.py app:app
www      3583  0.0  3.8 258900 77744 ?    S1   Nov13   0:01 /usr/bin/python3 /usr/local/bin/gunicorn -c /www/wwwroot/.../gunicorn_conf.py app:app
```

### 字段说明

| 字段 | 说明 | 示例 |
|------|------|------|
| **USER** | 运行用户 | `root`（主进程）、`www`（工作进程） |
| **PID** | 进程ID | `3579`、`3580` 等 |
| **%CPU** | CPU使用率 | `0.0` 表示空闲 |
| **%MEM** | 内存使用率 | `1.1%`、`3.8%` |
| **VSZ** | 虚拟内存大小（KB） | `28748`、`257884` |
| **RSS** | 物理内存大小（KB） | `23924`、`77088` |
| **TTY** | 终端 | `?` 表示后台进程 |
| **STAT** | 进程状态 | `S`（睡眠）、`S1`（多线程睡眠） |
| **START** | 启动时间 | `Nov13` 表示 11月13日启动 |
| **TIME** | CPU累计时间 | `0:01` 表示使用了1分钟CPU时间 |
| **COMMAND** | 完整命令 | Gunicorn 启动命令 |

### 进程类型

1. **Master 进程（PID 3579）**
   - 用户：`root`
   - 作用：管理所有 worker 进程
   - 状态：正常 ✅

2. **Worker 进程（PID 3580-3583）**
   - 用户：`www`
   - 数量：4 个
   - 作用：处理实际的 HTTP 请求
   - 状态：正常 ✅

---

## 🔍 进一步检查

### 1. 检查端口是否监听

```bash
# 方法 1：使用 netstat
netstat -tlnp | grep 5000

# 方法 2：使用 ss（更现代）
ss -tlnp | grep 5000

# 方法 3：使用 lsof
lsof -i :5000
```

**预期输出：**
```
tcp        0      0 0.0.0.0:5000            0.0.0.0:*               LISTEN      3579/python3
```

**说明：**
- `0.0.0.0:5000` 表示监听所有网络接口的 5000 端口
- `LISTEN` 表示正在监听
- `3579/python3` 是进程 PID 和名称

### 2. 测试内部连接

```bash
# 测试健康检查接口
curl http://127.0.0.1:5000/api/health

# 预期输出应该是 JSON：
# {"status":"healthy","timestamp":"...","database":"..."}
```

### 3. 检查 Gunicorn 配置

```bash
cd /www/wwwroot/pychatcat.cloud/python-learning-assistant/backend
cat gunicorn_conf.py
```

**检查要点：**
- `bind` 地址应该是 `0.0.0.0:5000` 或 `127.0.0.1:5000`
- `workers` 数量（通常是 2-4 个）
- `timeout` 设置

### 4. 查看 Gunicorn 日志

```bash
# 查看日志文件
tail -n 50 /www/wwwroot/pychatcat.cloud/python-learning-assistant/backend/gunicorn.log

# 或者如果配置了日志目录
ls -lh /www/wwwroot/pychatcat.cloud/python-learning-assistant/backend/logs/
```

---

## ⚠️ 常见问题

### 问题 1：进程在运行但无法连接

**可能原因：**
1. 端口未正确监听（检查 `netstat`）
2. 防火墙阻止（检查 `iptables` 或 `firewalld`）
3. Gunicorn 绑定地址错误（检查配置文件）

**解决方案：**
```bash
# 检查端口
netstat -tlnp | grep 5000

# 如果端口未监听，重启 Gunicorn
# 通过宝塔 Python 项目管理器重启
```

### 问题 2：Worker 进程数量不对

**正常情况：**
- 1 个 Master + 2-4 个 Worker

**如果只有 1 个进程：**
- 可能是直接运行 `python app.py`，不是用 Gunicorn
- 建议使用 Gunicorn 运行

### 问题 3：进程占用内存过高

**正常情况：**
- Master: ~20-30 MB
- Worker: ~70-80 MB 每个

**如果内存过高：**
- 检查是否有内存泄漏
- 考虑重启服务

---

## ✅ 健康检查清单

- [ ] Gunicorn 进程正在运行（`ps aux | grep gunicorn`）
- [ ] 端口 5000 正在监听（`netstat -tlnp | grep 5000`）
- [ ] 内部连接正常（`curl http://127.0.0.1:5000/api/health`）
- [ ] Nginx 配置正确（检查反向代理）
- [ ] 外部访问正常（`curl https://pychatcat.cloud/api/health`）

---

## 🔧 重启服务

如果需要重启 Flask 后端：

### 方法 1：通过宝塔面板（推荐）

1. 登录宝塔面板
2. 点击 **"Python项目"**
3. 找到您的项目
4. 点击 **"重启"**

### 方法 2：通过命令行

```bash
# 查找进程
ps aux | grep gunicorn

# 杀死进程（替换 PID）
kill -9 3579

# 重新启动（通过宝塔 Python 项目管理器，或手动启动）
cd /www/wwwroot/pychatcat.cloud/python-learning-assistant/backend
nohup gunicorn -w 2 -b 0.0.0.0:5000 app:app > gunicorn.log 2>&1 &
```

---

## 📝 下一步

根据您的检查结果：
1. ✅ **进程在运行** - 继续检查端口和连接
2. ⚠️ **端口未监听** - 检查 Gunicorn 配置
3. ❌ **无法连接** - 检查防火墙和 Nginx 配置




