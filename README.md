# 智能旅行助手（可运行骨架）

这个项目实现了一个和「智能旅行助手」教程同类型的最小可运行版本：
- 多 Agent 编排：`planner`、`budget`、`local-guide`
- 工具层：天气提示、POI 推荐、预算估算（可替换为真实 API/MCP）
- 服务层：FastAPI 提供 `/plan-trip` 接口
- 演示层：内置一个简单网页表单

## 1. 安装依赖

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## 2. 配置环境变量

```bash
cp .env.example .env
# 编辑 .env，填入 OPENAI_API_KEY
```

可选项：
- `OPENAI_MODEL` 默认 `gpt-4.1-mini`
- `APP_HOST` 默认 `127.0.0.1`
- `APP_PORT` 默认 `8000`

## 3. 启动服务

```bash
python -m app.main
```

打开浏览器访问：
- `http://127.0.0.1:8000`

## 4. API 示例

```bash
curl -X POST "http://127.0.0.1:8000/plan-trip" \
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

## 5. 目录结构

```text
app/
  agents/
    llm.py
    orchestrator.py
  models/
    schemas.py
  tools/
    travel_tools.py
  web/
    index.html
  main.py
```

## 6. 如何升级到教程级实现

1. 把 `app/tools/travel_tools.py` 替换为真实工具（机票、酒店、地图、天气）。
2. 在 `orchestrator.py` 中加入更细粒度 agent（如签证、交通、风险控制）。
3. 将当前本地函数调用改成 MCP Server 工具调用。
4. 给 `/plan-trip` 增加会话记忆（Redis/SQLite）与用户偏好持久化。
5. 增加测试：日期校验、预算约束、工具异常回退。

## 7. 无 OpenAI Key 时行为

如果 `OPENAI_API_KEY` 未配置，系统自动使用 fallback 规则生成结果，便于你先验证整体链路。
