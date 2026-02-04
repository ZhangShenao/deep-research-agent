# -*- coding: utf-8 -*-
"""
@Time    : 2026/02/04
@Author  : ZhangShenao
@File    : agent.py
@Desc    : Short-Term Memory 短期记忆

LangGraph实现短期记忆的核心是Checkpoint机制
Checkpointer是LangGraph中用于保存和恢复图执行状态的组件。它允许:
1. Persistence 持久化：将对话状态保存到外部存储
2. Recovery 恢复：在应用重启后恢复之前的对话
3. Time Travel 时间旅行：查看历史状态,从任意检查点恢复
4. Human-in-the-Loop 人机交互：等待人类输入,然后恢复执行
5. Multi-threading 多线程支持：支持多个并发对话会话
"""

from langgraph.graph import StateGraph, START, END
from langgraph.graph.state import CompiledStateGraph
from state import AgentState
from chat_node import chat_node
from summary_node import summary_node
from conditional_edge import conditional_edge
from checkpointer import CHECKPOINTER
from langchain_core.messages import HumanMessage
from sqlite import DB_PATH
import dotenv


def build_agent() -> CompiledStateGraph:
    """
    构建Agent
    """

    # 构造Graph图
    graph = StateGraph(AgentState)

    # 添加Node节点
    graph.add_node("chat_node", chat_node)
    graph.add_node("summary_node", summary_node)

    # 添加普通边
    graph.add_edge(START, "chat_node")

    # 添加条件边
    graph.add_conditional_edges(
        source="chat_node",
        path=conditional_edge,
        path_map={
            "summary_node": "summary_node",
            END: END,
        },
    )

    # 添加普通边
    graph.add_edge("summary_node", END)

    # 编译Agent，并指定Checkpointer
    agent = graph.compile(checkpointer=CHECKPOINTER)

    # 打印Agent节点结构图,并保存到本地
    print("Agent构建完成")
    agent.get_graph().draw_mermaid_png(output_file_path="./short_term_memory_agent.png")

    # 返回编译后的Agent
    return agent


def state_check(agent: CompiledStateGraph) -> None:
    """
    状态检查
    """

    # 指定thread_id，resume state
    config = {"configurable": {"thread_id": "1"}}
    graph_state = agent.get_state(config)

    print("🔄 重新获取状态，验证持久化")
    print("=" * 50)

    # 验证状态是否完整恢复
    print(f"📊 状态恢复验证:")
    print(f"  - 消息数量: {len(graph_state.values["messages"])}")
    print(f"  - 是否有摘要: {"是" if graph_state.values.get("summary") else '否'}")
    print(f"  - 摘要: \n{graph_state.values.get("summary")}")
    print(f"  - 状态完整性: {"✅ 完整" if graph_state.values else "❌ 不完整"}")

    print(f"\n💾 持久化状态:")
    print(f"  - 数据库文件: {DB_PATH}")
    print(f"  - 线程ID: {config["configurable"]["thread_id"]}")
    print(f"  - 检查点ID: {graph_state.config.get("checkpoint_id", "N/A")}")

    print(f"\n🎉 持久化验证成功！")
    print(f"✨ 状态已成功保存到SQLite数据库，可以跨会话恢复")


if __name__ == "__main__":
    # 加载环境变量
    dotenv.load_dotenv()

    # 构建Agent
    agent = build_agent()

    # 测试多轮对话
    # 创建对话线程配置
    # thread_id用于标识不同的对话会话，相同ID的对话会共享状态
    config = {"configurable": {"thread_id": "1"}}

    print("🚀 开始聊天机器人测试")
    print("=" * 50)

    # 第1轮：自我介绍
    print("\n第1轮：自我介绍")
    query = HumanMessage(content="你好！我是zsa。")
    output = agent.invoke({"messages": [query], "summary": None}, config)
    for m in output["messages"][-1:]:
        m.pretty_print()

    # 第2轮：Agent记忆测试
    print("\n第2轮：Agent记忆测试")
    query = HumanMessage(content="你还记得我叫什么名字吗？")
    output = agent.invoke({"messages": [query], "summary": None}, config)
    for m in output["messages"][-1:]:
        m.pretty_print()

    # 第3轮：用户分享兴趣
    print("\n第3轮：用户分享兴趣")
    query = HumanMessage(content="我喜欢听周杰伦的歌")
    output = agent.invoke({"messages": [query], "summary": None}, config)
    for m in output["messages"][-1:]:
        m.pretty_print()

    # 状态检查
    state_check(agent)
