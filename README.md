# Task Manager

一个基于 **FastAPI** + **Vue 3** 的定时任务调度系统，支持通过 REST API 动态创建、管理和执行 Python 代码任务，并可将执行结果推送到指定 Webhook。

---

## 功能特性

- 📋 **任务管理**：通过 REST API 增删改查任务
- ⏰ **灵活的触发时间**：支持按月份、星期、月份中的天、小时、分钟组合触发
- ⚡ **立即执行**：支持标记任务立即运行，无需等待触发时间
- 🔒 **进程隔离执行**：每个任务在独立子进程中运行，超时自动终止
- 📡 **结果推送**：任务执行完毕后可将结果以 HTTP POST 方式推送到指定 URL
- 🖥️ **Web 管理界面**：基于 Vue 3 的前端，支持任务的可视化管理
- 🤖 **内置 AI 函数**：集成 OpenAI 兼容 API（默认 DeepSeek），可在任务代码中调用
- 📝 **日志记录**：全链路操作日志

---

## 项目结构

```
task-manager/
├── main.py                   # FastAPI 主程序，定义所有 REST API
├── config.json               # 全局配置（超时时间、AI API 等）
├── functions.json            # 函数配置（预留）
├── pyproject.toml            # Python 项目依赖
├── Modules/
│   ├── task.py               # Task / Trigger_time 数据模型
│   └── Log.py                # 日志模块
├── Scheduler/
│   └── scheduler_core.py     # 调度器核心（任务轮询与入队）
├── Worker/
│   └── worker_core.py        # 工作进程（任务执行与结果推送）
├── Default_functions/
│   └── functions.py          # 内置函数（AI 接口等）
├── Task_functions/
│   └── task_functions.py     # 示例任务函数（如 NASA 每日图片）
├── Tasks/
│   └── tasks_list.json       # 任务持久化存储
├── Log/                      # 日志输出目录
└── Vue/
    └── web-ui/               # Vue 3 前端项目
```

---

## 快速开始

### 环境要求

- Python >= 3.12
- Node.js >= 16（运行前端）
- [uv](https://github.com/astral-sh/uv)（推荐）或 pip

### 后端启动

```bash
# 安装依赖
uv sync

# 启动服务（默认监听 0.0.0.0:8000）
uv run python main.py
```

或使用 uvicorn 直接启动：

```bash
uv run uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### 前端启动

```bash
cd Vue/web-ui
npm install
npm run serve
```

前端默认运行在 `http://localhost:8080`。

---

## 配置说明

编辑 `config.json` 修改全局配置：

```json
{
    "timeout": 60,
    "AI_API_URL": "https://api.deepseek.com",
    "AI_API_KEY": "your_api_key_here",
    "AI_API_MODEL": "deepseek-chat"
}
```

| 字段 | 说明 | 默认值 |
|------|------|--------|
| `timeout` | 任务执行超时时间（秒） | `60` |
| `AI_API_URL` | OpenAI 兼容 API 地址 | `https://api.deepseek.com` |
| `AI_API_KEY` | API 密钥 | `""` |
| `AI_API_MODEL` | 使用的模型名称 | `deepseek-chat` |

---

## API 文档

服务启动后可访问 `http://localhost:8000/docs` 查看交互式 Swagger 文档。

### 接口概览

| 方法 | 路径 | 说明 |
|------|------|------|
| `GET` | `/` | 欢迎信息 |
| `GET` | `/health` | 健康检查 |
| `POST` | `/add_task` | 添加任务 |
| `GET` | `/tasks` | 获取所有任务 |
| `GET` | `/set_done/{task_id}` | 标记任务为已完成 |
| `GET` | `/set_undone/{task_id}` | 标记任务为未完成 |
| `DELETE` | `/delete_task/{task_id}` | 删除任务 |
| `PUT` | `/update_task/{task_id}` | 更新任务 |

### 添加任务示例

```http
POST /add_task
Content-Type: application/json

{
    "title": "每日 NASA 图片",
    "description": "每天定时获取 NASA 天文图片并推送",
    "code": "def get_daily_NASA_img():\n    ...",
    "trigger_time_list": [
        {
            "mouth": [],
            "week_day": [],
            "mouth_day": [],
            "hour": 8,
            "minute": 0
        }
    ],
    "immediately": false,
    "is_send": true,
    "send_url": "https://your-webhook.example.com/notify",
    "send_token": "your_token"
}
```

**任务字段说明：**

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `title` | string | ✅ | 任务标题 |
| `code` | string | ✅ | 要执行的 Python 函数代码（函数名须与 `def` 后的名称一致） |
| `immediately` | bool | ✅（与 `trigger_time_list` 二选一） | 是否立即执行 |
| `trigger_time_list` | array | ✅（与 `immediately` 二选一） | 触发时间规则列表 |
| `description` | string | ❌ | 任务描述 |
| `target_count` | int | ❌ | 最大执行次数，`0` 表示不限制 |
| `is_send` | bool | ❌ | 是否将执行结果推送到指定 URL |
| `send_url` | string | ❌ | 结果推送地址 |
| `send_token` | string | ❌ | 推送鉴权 Token（Bearer） |

**触发时间（`trigger_time_list` 元素）字段说明：**

| 字段 | 类型 | 说明 |
|------|------|------|
| `mouth` | `int[]` | 触发的月份，空数组表示每月 |
| `week_day` | `int[]` | 触发的星期（1=周一，7=周日），空数组表示每天 |
| `mouth_day` | `int[]` | 触发的日期，空数组表示每天 |
| `hour` | `int` | 触发的小时（24 小时制） |
| `minute` | `int` | 触发的分钟 |

---

## 任务代码规范

任务的 `code` 字段须包含一个 **顶层函数定义**，函数名即为模块名，例如：

```python
def my_task():
    import requests
    resp = requests.get("https://example.com")
    return resp.status_code
```

> ⚠️ 任务代码在独立子进程中执行，需自行导入所需模块。可调用 `Default_functions/functions.py` 中的 `get_single_ai_response(prompt)` 使用 AI 能力。

---

## 技术栈

| 层次 | 技术 |
|------|------|
| 后端框架 | FastAPI + Uvicorn |
| 任务调度 | Python threading + multiprocessing |
| 数据存储 | JSON 文件（`Tasks/tasks_list.json`） |
| AI 集成 | OpenAI SDK（兼容 DeepSeek 等） |
| 前端框架 | Vue 3 + Vue Router |
| HTTP 客户端 | Axios |
| 代码高亮 | highlight.js |
