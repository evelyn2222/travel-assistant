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

## 技术栈

- **后端**：Python 3.14, Flask
- **API集成**：MINIMAX API
- **前端**：HTML, CSS, JavaScript
- **依赖管理**：pip

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
| `APP_HOST` | `127.0.0.1` | 应用主机地址 |
| `APP_PORT` | `8001` | 应用端口 |

## 目录结构

```text
app/
  agents/            # 代理相关代码
    llm.py          # 语言模型调用
    orchestrator.py  # 代理编排
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
