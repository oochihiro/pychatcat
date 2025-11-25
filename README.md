# 🎓 智能Python学习助手

一个功能完整的Python学习桌面应用，集成了代码编辑、AI助手、断点调试和数据分析功能。

## ✨ 核心特性

- **📝 代码编辑器** - 完整语法高亮、行号显示、断点调试
- **🖥️ 输出控制台** - 黑色背景、彩色输出、智能错误分析
- **🤖 AI学习助手** - DeepSeek AI集成、智能问答、代码示例
- **🐛 断点调试** - 可视化断点、单步执行、变量监控
- **📊 数据分析** - SQLite数据采集、学习行为追踪

## 🚀 快速启动

### 安装依赖
```bash
pip install -r requirements.txt
```

### 运行程序
```bash
python main.py
```

## 📁 项目结构

```
python-learning-assistant/
├── main.py                    # 主程序入口
├── requirements.txt           # 项目依赖
├── core/                      # 核心功能模块
│   ├── file_manager.py       # 文件管理
│   ├── code_executor.py      # 代码执行器
│   ├── deepseek_client.py    # DeepSeek AI客户端
│   └── sqlite_analytics.py   # SQLite数据分析
├── ui/                        # 用户界面组件
│   ├── pixel_code_editor.py  # 代码编辑器
│   ├── pixel_console.py      # 输出控制台
│   ├── pixel_ai_assistant.py # AI助手面板
│   └── debugger_panel.py     # 调试器面板
├── backend/                   # 后端API服务
│   ├── app.py                # Flask应用
│   └── requirements.txt      # 后端依赖
├── integrations/              # 集成模块
│   └── sqlite_integration.py # 数据采集集成
├── docs/                      # 文档目录
├── scripts/                   # 工具脚本
└── examples/                  # 示例代码
```

## 🛠️ 功能说明

### 代码编辑器
- 完整语法高亮（关键字、字符串、注释、函数名等）
- 行号显示，支持断点设置
- 右键菜单（复制、粘贴、剪切、清空）
- 文本选择（蓝底白字）

### 输出控制台
- 黑色背景，Hacker风格
- 彩色输出（错误、警告、信息、建议）
- 智能错误分析，准确行号定位
- 上下文感知的修改建议

### AI学习助手
- DeepSeek AI集成
- 智能问答，代码示例
- 对话历史保存（TXT/JSON格式）
- 可调整布局，响应式设计

### 断点调试
- 点击行号设置/取消断点
- 单步执行（步入、跳过、跳出）
- 变量监控和调用堆栈显示
- 调试器面板

### 数据分析
- SQLite本地数据库存储
- 学习行为自动采集
- 支持云端上报（Flask API）
- 详细的行为分析报告

## 📊 后端部署

### 服务器要求
- 轻量应用服务器：2核2G或更高
- 系统：Ubuntu 22.04 LTS
- 带宽：5-10Mbps

### 部署步骤
详细部署指南请参考：[docs/部署指南.md](docs/部署指南.md)

1. 上传 `backend/` 目录到服务器
2. 安装依赖：`pip install -r backend/requirements.txt`
3. 使用Gunicorn运行：`gunicorn -w 2 -b 0.0.0.0:5000 app:app`
4. 配置Nginx反向代理
5. 配置SSL证书（可选）

## 📚 文档

- [使用指南](docs/使用指南.txt)
- [项目说明](docs/项目说明.md)
- [数据分析方案](docs/数据分析方案.md)
- [部署指南](docs/部署指南.md)

## 🔧 配置

### 后端地址配置
编辑 `data/config.json`（如果存在）或环境变量：
```json
{
  "backend_url": "https://your-server.com"
}
```

## 📦 依赖

### 基础依赖
- `openai>=1.0.0` - DeepSeek API
- `Pillow>=8.0.0` - 图标支持

### 数据分析依赖（可选）
- `Flask>=2.3.0` - 后端API
- `Flask-CORS>=4.0.0` - 跨域支持
- `pandas>=2.0.0` - 数据分析
- `numpy>=1.24.0` - 数值计算

## ⌨️ 快捷键

- **F5** - 运行代码
- **F9** - 设置/取消断点
- **Ctrl+Enter** - 在AI助手中发送消息
- **Ctrl+C/V/X** - 复制/粘贴/剪切

## 🎯 使用场景

- Python初学者学习编程
- 代码调试和错误分析
- AI辅助编程学习
- 学习行为数据分析

## 📝 许可证

本项目仅供学习和教学使用。

## 🤝 贡献

欢迎提交Issue和Pull Request！

---

**注意**：首次运行会自动创建 `data/` 和 `logs/` 目录。数据库文件存储在 `data/learning_analytics.db`。
