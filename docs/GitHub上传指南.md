# GitHub 上传指南

本指南将帮助您将 PyChatCat 应用程序上传到 GitHub。

## 📋 前置准备

### 1. 安装 Git

如果您的系统还没有安装 Git，请先安装：

**Windows 系统：**
1. 访问 [Git 官网](https://git-scm.com/download/win)
2. 下载并安装 Git for Windows
3. 安装完成后，重启 PowerShell 或命令提示符

**验证安装：**
```bash
git --version
```

### 2. 创建 GitHub 账号和仓库

1. 访问 [GitHub](https://github.com) 并登录（如果没有账号，先注册）
2. 点击右上角的 **+** 号，选择 **New repository**
3. 填写仓库信息：
   - **Repository name**: `pychatcat` 或您喜欢的名称
   - **Description**: `智能Python学习助手 - Python Learning Assistant with AI`
   - **Visibility**: 选择 Public（公开）或 Private（私有）
   - **不要**勾选 "Initialize this repository with a README"（因为本地已有代码）
4. 点击 **Create repository**

创建完成后，GitHub 会显示仓库地址，类似：
```
https://github.com/您的用户名/pychatcat.git
```

## 🚀 上传步骤

### 步骤 1: 初始化 Git 仓库

在项目根目录（`E:\cursor_web`）打开 PowerShell 或命令提示符，执行：

```bash
# 初始化 Git 仓库
git init

# 配置用户信息（如果还没配置过）
git config --global user.name "您的名字"
git config --global user.email "您的邮箱@example.com"
```

### 步骤 2: 添加所有文件

```bash
# 查看 .gitignore 会排除哪些文件（数据库、日志、构建产物等）
git status

# 添加所有文件到暂存区
git add .

# 再次查看状态，确认要提交的文件
git status
```

### 步骤 3: 创建首次提交

```bash
# 创建提交
git commit -m "Initial commit: PyChatCat - Python Learning Assistant with AI"
```

### 步骤 4: 连接远程仓库

将您的 GitHub 仓库地址添加为远程仓库：

```bash
# 添加远程仓库（将 YOUR_USERNAME 和 YOUR_REPO_NAME 替换为您的实际信息）
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git

# 验证远程仓库
git remote -v
```

**示例：**
```bash
git remote add origin https://github.com/zhangsan/pychatcat.git
```

### 步骤 5: 推送到 GitHub

```bash
# 推送代码到 GitHub（首次推送）
git branch -M main
git push -u origin main
```

如果提示输入用户名和密码：
- **用户名**: 您的 GitHub 用户名
- **密码**: 使用 **Personal Access Token**（不是 GitHub 密码）

**如何获取 Personal Access Token：**
1. GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
2. 点击 "Generate new token (classic)"
3. 勾选 `repo` 权限
4. 生成后复制 token，在密码提示时粘贴

## 📝 后续更新代码

当您修改代码后，使用以下命令更新 GitHub：

```bash
# 1. 查看修改的文件
git status

# 2. 添加修改的文件
git add .

# 3. 提交修改
git commit -m "描述您的修改内容"

# 4. 推送到 GitHub
git push
```

## ⚠️ 重要注意事项

### 1. 敏感信息保护

确保以下文件**不会**被上传（已在 `.gitignore` 中配置）：
- `data/*.db` - 数据库文件（包含学生数据）
- `logs/*.log` - 日志文件
- `.env` - 环境变量文件
- `config.json` - 配置文件（如果包含 API 密钥）

### 2. 检查要上传的文件

在首次 `git add .` 后，执行 `git status` 确认：
- ✅ 源代码文件（`.py`）
- ✅ 文档文件（`docs/*.md`）
- ✅ 配置文件（`requirements.txt`）
- ❌ 数据库文件（`data/*.db`）
- ❌ 构建产物（`dist/`, `build/`）
- ❌ 日志文件（`logs/*.log`）

### 3. 如果误上传了敏感文件

如果已经推送了包含敏感信息的文件，需要：

```bash
# 1. 从 Git 历史中删除文件（但保留本地文件）
git rm --cached data/learning_analytics.db

# 2. 提交删除
git commit -m "Remove sensitive database file"

# 3. 推送到 GitHub
git push

# 4. 如果文件已经在 GitHub 上，需要清理历史记录
# 建议：删除仓库后重新创建，或使用 git filter-branch
```

## 🔍 验证上传结果

1. 访问您的 GitHub 仓库页面
2. 确认以下内容已上传：
   - ✅ `main.py` - 主程序
   - ✅ `core/` - 核心模块
   - ✅ `ui/` - UI 组件
   - ✅ `backend/` - 后端代码
   - ✅ `docs/` - 文档
   - ✅ `requirements.txt` - 依赖列表
   - ✅ `README.md` - 项目说明
3. 确认以下内容**未**上传：
   - ❌ `data/learning_analytics.db`
   - ❌ `dist/pychatcat.exe`
   - ❌ `logs/*.log`

## 📚 常用 Git 命令

```bash
# 查看状态
git status

# 查看提交历史
git log

# 查看远程仓库
git remote -v

# 拉取远程更新
git pull

# 创建新分支
git checkout -b feature/new-feature

# 切换分支
git checkout main

# 查看差异
git diff
```

## 🆘 遇到问题？

### 问题 1: "fatal: not a git repository"
**解决**: 确保在项目根目录执行 `git init`

### 问题 2: "Permission denied"
**解决**: 
- 检查 GitHub 用户名和 Personal Access Token
- 确认仓库地址正确

### 问题 3: "error: failed to push"
**解决**: 
- 先执行 `git pull origin main --allow-unrelated-histories`
- 解决冲突后再 `git push`

### 问题 4: 文件太大无法推送
**解决**: 
- 检查 `.gitignore` 是否正确排除大文件
- 如果 `dist/pychatcat.exe` 太大，确保已在 `.gitignore` 中

---

**完成！** 🎉 您的代码现在应该已经在 GitHub 上了！

