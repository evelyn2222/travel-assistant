# 智能旅行助手

## 项目简介

智能旅行助手是一个基于Flask和MINIMAX API的智能旅行规划系统，能够为用户生成详细、个性化的旅行计划。系统支持任意城市的旅行规划，提供景点推荐、美食建议、预算估算等功能，帮助用户轻松规划完美的旅行。

### 核心功能

- **智能行程规划**：根据用户输入的出发地、目的地、旅行日期、人数、预算和兴趣偏好，生成详细的每日行程
- **景点推荐**：基于目的地城市的特色，推荐热门景点和地标
- **美食建议**：提供当地特色美食推荐
- **预算估算**：根据旅行天数和人数，估算旅行预算并提供优化建议
- **天气提示**：根据旅行日期提供目的地的天气情况和穿衣建议
- **当地提示**：提供当地交通、景点游览等实用信息
- **ReAct Agent**：支持基于ReAct范式（推理-行动-观察）的智能代理，自主决策工具调用
- **上下文工程**：支持会话记忆和用户偏好存储，实现多轮对话和个性化推荐

## 技术栈

- **后端**：Python 3.14, Flask
- **API集成**：MINIMAX API
- **前端**：HTML, CSS, JavaScript
- **依赖管理**：pip
- **Agent架构**：支持多Agent协作范式和ReAct范式

## Agent架构

### 多Agent协作范式（默认）

系统采用多Agent协作架构，通过Orchestrator协调多个专业Agent：

- **Planner Agent**：负责行程规划和每日安排
- **Budget Agent**：负责预算优化和成本分配
- **Local Guide Agent**：负责本地建议和实用提示

### ReAct范式（可选）

系统支持基于ReAct范式的智能代理，通过推理-行动-观察循环自主决策：

- **推理**：分析用户需求，决定下一步行动
- **行动**：调用相应的工具获取信息
- **观察**：根据工具返回结果继续推理
- **循环**：直到收集足够信息，给出最终答案

**ReAct Agent优势**：
- 自主决策：LLM自主决定何时调用工具、调用哪个工具
- 灵活性：根据实际情况动态调整策略
- 可扩展性：易于添加新的工具和能力

**启用ReAct模式**：
在 `.env` 文件中设置 `USE_REACT=true` 即可启用ReAct模式。

## 上下文工程

系统实现了完整的上下文工程功能，支持会话记忆和用户偏好存储：

### 会话管理

- **会话创建**：通过 `/session` 接口创建新会话，支持自定义过期时间
- **会话查询**：通过 `/session/<session_id>` 获取会话上下文和历史消息
- **会话更新**：每次交互自动更新会话时间，防止过期

### 用户偏好存储

- **偏好保存**：通过 `/session/<session_id>/preferences` 保存用户偏好
- **偏好应用**：系统会根据用户偏好自动调整推荐策略
- **个性化推荐**：基于历史偏好提供更精准的旅行建议

### 对话历史

- **消息存储**：自动保存用户和助手的对话历史
- **上下文传递**：在生成旅行计划时，自动传递历史上下文
- **多轮对话**：支持基于历史对话进行修改和优化

### API接口

```bash
# 创建会话
curl -X POST "http://127.0.0.1:8001/session" \
  -H "Content-Type: application/json" \
  -d '{"user_id": "user123", "ttl_hours": 24}'

# 获取会话上下文
curl "http://127.0.0.1:8001/session/session_xxx"

# 保存用户偏好
curl -X POST "http://127.0.0.1:8001/session/session_xxx/preferences" \
  -H "Content-Type: application/json" \
  -d '{"preferences": {"preferred_destinations": ["东京", "上海"], "preferred_budget": 10000}}'

# 添加消息到上下文
curl -X POST "http://127.0.0.1:8001/session/session_xxx/message" \
  -H "Content-Type: application/json" \
  -d '{"role": "user", "content": "我想去东京旅行"}'
```

### 使用会话ID

在调用 `/plan-trip` 接口时，可以传入 `session_id` 参数来启用上下文：

```bash
curl -X POST "http://127.0.0.1:8001/plan-trip" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "session_xxx",
    "origin": "上海",
    "destination": "东京",
    ...
  }'
```

## 安装步骤

### 1. 克隆项目

```bash
git clone https://github.com/evelyn2222/travel-assistant.git
cd travel-assistant
```

### 2. 创建虚拟环境并安装依赖

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 3. 配置环境变量

```bash
cp .env.example .env
# 编辑 .env 文件，填入 MINIMAX_API_KEY
```

### 4. 启动服务

```bash
source .venv/bin/activate && python3 -m app.main
```

## 使用方法

### 网页界面

打开浏览器访问：
- `http://127.0.0.1:8001`

在左侧输入旅行信息，包括出发地、目的地、旅行日期、人数、预算和兴趣偏好，点击"生成旅行计划"按钮，右侧会显示详细的旅行计划。

### API接口

可以通过POST请求调用 `/plan-trip` 端点：

```bash
curl -X POST "http://127.0.0.1:8001/plan-trip" \
  -H "Content-Type: application/json" \
  -d '{
    "origin": "上海",
    "destination": "东京",
    "start_date": "2026-05-01",
    "end_date": "2026-05-05",
    "travelers": 2,
    "budget_cny": 12000,
    "interests": ["美食", "城市漫步", "艺术馆"],
    "pace": "balanced"
  }'
```

## 配置选项

在 `.env` 文件中可以配置以下环境变量：

| 环境变量 | 默认值 | 描述 |
|---------|-------|------|
| `MINIMAX_API_KEY` | 无 | MINIMAX API 密钥 |
| `OPENAI_API_KEY` | 无 | OpenAI API 密钥（可选） |
| `OPENAI_MODEL` | `gpt-4.1-mini` | OpenAI 模型（可选） |
| `USE_REACT` | `false` | 是否启用ReAct模式（true/false） |
| `APP_HOST` | `127.0.0.1` | 应用主机地址 |
| `APP_PORT` | `8001` | 应用端口 |

## 目录结构

```text
app/
  agents/            # 代理相关代码
    llm.py          # 语言模型调用
    orchestrator.py  # 代理编排
    react_agent.py   # ReAct Agent实现
  context/           # 上下文管理模块
    context_manager.py  # 会话和偏好管理
  models/            # 数据模型
    schemas.py      # 请求和响应模式
  tools/             # 工具函数
    travel_tools.py  # 旅行相关工具
  web/               # 前端代码
    index.html       # 网页界面
  main.py            # 应用主入口
.env.example         # 环境变量示例
.gitignore          # Git忽略文件
README.md           # 项目说明
requirements.txt    # 依赖列表
```

## 功能特性

### 1. 智能行程规划

系统会根据用户输入的旅行信息，生成详细的每日行程，包括：
- 上午、中午、下午、晚上的活动安排
- 具体的景点推荐
- 特色美食建议
- 合理的时间安排

### 2. 景点推荐

- 对于内置城市，使用预定义的景点数据
- 对于其他城市，通过MINIMAX API获取景点信息
- 确保每个景点只出现一次，避免重复

### 3. 美食建议

- 对于内置城市，使用预定义的美食数据
- 对于其他城市，通过MINIMAX API获取美食信息
- 提供当地特色美食推荐

### 4. 预算估算

- 根据旅行天数和人数，估算总预算
- 提供详细的预算明细，包括住宿、交通、餐饮、门票等
- 提供预算优化建议

### 5. 天气提示

- 根据旅行日期提供目的地的天气情况
- 提供穿衣建议
- 提示出发前复查天气

### 6. 当地提示

- 提供当地交通信息
- 提供景点游览建议
- 提供安全提示

### 7. 上下文工程

- **会话管理**：支持创建、查询、更新会话
- **用户偏好**：保存和应用用户偏好，实现个性化推荐
- **对话历史**：自动保存对话历史，支持多轮对话
- **上下文传递**：在生成旅行计划时自动传递历史上下文

## 常见问题

### 1. API调用失败

如果遇到API调用失败的情况，系统会自动使用内置的默认数据，确保能够生成旅行计划。

### 2. 生成时间过长

如果生成旅行计划的时间过长，可能是因为API调用超时。系统已经优化了API调用逻辑，会在超时后使用默认数据。

### 3. 景点或美食信息不具体

对于一些较小的城市，可能无法获取到具体的景点和美食信息，系统会使用通用模板。

## 贡献指南

欢迎贡献代码！如果您有任何建议或改进，请：

1. Fork 本仓库
2. 创建您的特性分支 (`git checkout -b feature/amazing-feature`)
3. 提交您的更改 (`git commit -m 'Add some amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 开启一个 Pull Request

## 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件

## 联系方式

- GitHub: [https://github.com/evelyn2222/travel-assistant](https://github.com/evelyn2222/travel-assistant)
