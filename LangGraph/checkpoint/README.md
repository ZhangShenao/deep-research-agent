# LangGraph Checkpoint 演示项目

本项目演示 LangGraph 的持久化（Persistence）和检查点（Checkpoint）机制，通过一个完整的电商客服 Agent 展示核心功能。

## 项目结构

```
checkpoint/
├── LangGraph_Persistence_技术博客.md  # 技术博客文档
├── README.md                          # 本文件
├── requirements.txt                   # 依赖文件
├── state.py                           # Agent 状态定义
├── tools.py                           # 工具定义
├── llm.py                             # LLM 配置
├── nodes.py                           # 节点实现
├── mongodb_checkpointer.py            # MongoDB Checkpointer 实现
├── agent.py                           # Agent 主程序
└── main.py                            # 运行入口
```

## 核心功能

1. **多轮对话记忆（Memory）**：通过 `thread_id` 实现多轮对话的上下文保持
2. **人机交互（Human-in-the-Loop）**：使用 `interrupt()` 暂停执行，等待人类输入
3. **时间旅行（Time Travel）**：查看历史状态，从任意检查点恢复执行
4. **状态管理 API**：`get_state()`、`get_state_history()` 等

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境变量

```bash
export OPENAI_API_KEY="your-api-key"
export OPENAI_BASE_URL="https://api.openai.com/v1"  # 可选
export OPENAI_MODEL="gpt-4o-mini"  # 可选
```

### 3. 运行演示

```bash
python main.py
```

### 4. 使用 MongoDB 存储

确保本地 MongoDB 服务运行：

```bash
# 启动 MongoDB
mongod --dbpath /path/to/data

# 运行演示并选择 MongoDB 模式
python main.py
# 选择选项 5
```

## 使用示例

### 基础使用

```python
from agent import build_customer_service_agent
from langchain_core.messages import HumanMessage

# 构建 Agent
agent = build_customer_service_agent()

# 设置线程 ID（用于持久化）
config = {"configurable": {"thread_id": "user-001"}}

# 对话
result = agent.invoke(
    {"messages": [HumanMessage(content="iPhone 15 多少钱？")]},
    config=config
)

print(result["messages"][-1].content)
```

### 使用 MongoDB 存储

```python
from agent import build_agent_with_mongodb

# 使用 MongoDB 作为检查点存储
agent = build_agent_with_mongodb(
    mongodb_uri="mongodb://localhost:27017",
    db_name="customer_service"
)

config = {"configurable": {"thread_id": "user-001"}}
result = agent.invoke(
    {"messages": [HumanMessage(content="你好")]},
    config=config
)
```

### Human-in-the-Loop

```python
from langgraph.types import Command

# 当 Agent 调用 ask_human 工具时，会触发中断
result = agent.invoke(
    {"messages": [HumanMessage(content="订单丢了怎么办？")]},
    config=config
)

# 检查是否需要人工介入
if result.get("__interrupt__"):
    # 提供人工回复
    result = agent.invoke(
        Command(resume="我们会在24小时内处理"),
        config=config
    )
```

### 时间旅行

```python
# 查看状态历史
for state in agent.get_state_history(config):
    print(f"消息数: {len(state.values['messages'])}, 下一步: {state.next}")

# 从某个历史状态恢复
past_state = list(agent.get_state_history(config))[3]
result = agent.invoke(
    {"messages": [HumanMessage(content="换个问题")]},
    config=past_state.config
)
```

## 技术文档

详细的技术原理请阅读 [LangGraph_Persistence_技术博客.md](./LangGraph_Persistence_技术博客.md)

## 参考资料

- [LangGraph 官方文档 - Persistence](https://docs.langchain.com/oss/python/langgraph/persistence)
- [LangGraph GitHub](https://github.com/langchain-ai/langgraph)

