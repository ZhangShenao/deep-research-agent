# -*- coding: utf-8 -*-
"""
@Time    : 2025/12/09
@Author  : ZhangShenao
@File    : main.py
@Desc    : 旅游规划多智能体系统入口 - 支持 Stream 流式输出
"""

from langchain_core.messages import HumanMessage, AIMessage
from langgraph.checkpoint.memory import MemorySaver

from travel_agent import build_travel_agent
from mongodb_checkpointer import MongoDBSaver


def format_namespace(namespace: tuple) -> str:
    """
    格式化命名空间为可读字符串

    Args:
        namespace: 流式输出的命名空间元组

    Returns:
        格式化后的字符串
    """
    if not namespace:
        return "主图"

    # 提取子图名称
    parts = []
    for item in namespace:
        # 格式如 "call_weather_agent:abc123"
        if ":" in item:
            name = item.split(":")[0]
        else:
            name = item
        parts.append(name)

    return f"子图({' > '.join(parts)})"


def print_stream_chunk(namespace: tuple, update: dict):
    """
    打印流式输出的单个 chunk

    Args:
        namespace: 命名空间元组
        update: 状态更新字典
    """
    ns_str = format_namespace(namespace)

    for node_name, node_update in update.items():
        print(f"  [{ns_str}] {node_name}:")

        # 格式化输出更新内容
        for key, value in node_update.items():
            if key == "messages":
                # 特殊处理消息列表
                for msg in value:
                    if isinstance(msg, AIMessage):
                        content = (
                            msg.content[:100] + "..."
                            if len(msg.content) > 100
                            else msg.content
                        )
                        print(f"    └─ AI回复: {content}")
                    elif isinstance(msg, HumanMessage):
                        print(f"    └─ 用户消息: {msg.content}")
            else:
                # 普通字段
                value_str = (
                    str(value)[:80] + "..." if len(str(value)) > 80 else str(value)
                )
                print(f"    └─ {key}: {value_str}")


def run_travel_agent_with_stream():
    """
    以流式输出方式运行旅游规划多智能体系统

    这个函数演示了如何：
    1. 使用 MemorySaver 作为 Checkpoint 持久化存储
    2. 使用 stream() 方法进行流式输出
    3. 设置 subgraphs=True 查看子图的执行过程
    """
    print("=" * 70)
    print("🌏 旅游规划多智能体系统 (Multi-Agent Travel Planning System)")
    print("=" * 70)
    print()
    print("本系统包含以下 Agent：")
    print("  • 主 Agent (Customer Service Agent) - 意图识别与路由调度")
    print("  • 天气子 Agent (Weather Agent) - 查询城市天气")
    print("  • 车票子 Agent (Ticket Agent) - 查询火车票价格")
    print()
    print("技术特点：")
    print("  • 使用 Subgraph 实现多智能体架构")
    print("  • 使用 MemorySaver 实现对话持久化")
    print("  • 使用 Stream 实现流式输出")
    print("=" * 70)
    print()

    # 创建MongoDB持久化存储
    mongodb_uri = "mongodb://localhost:27017"
    db_name = "travel_agent"
    checkpointer = MongoDBSaver.from_conn_string(mongodb_uri, db_name=db_name)

    # 构建主 Agent，并设置checkpointer
    agent = build_travel_agent(checkpointer=checkpointer)

    # 会话配置（Thread ID 用于标识对话会话）
    config = {"configurable": {"thread_id": "travel-session-001"}}

    print("输入 'quit' 或 'exit' 退出程序")
    print("-" * 70)
    print()

    while True:
        # 获取用户输入
        try:
            user_input = input("👤 用户: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n\n👋 再见！祝您旅途愉快！")
            break

        # 检查退出命令
        if user_input.lower() in ["quit", "exit", "q"]:
            print("\n👋 再见！祝您旅途愉快！")
            break

        # 跳过空输入
        if not user_input:
            continue

        print()
        print("📊 执行流程 (Stream Output with Subgraphs):")
        print("-" * 50)

        # 使用 Stream 流式执行（关键：subgraphs=True）
        final_response = None

        for chunk in agent.stream(
            {"messages": [HumanMessage(content=user_input)]},
            config=config,
            stream_mode="updates",
            subgraphs=True,  # 启用子图流式输出
        ):
            # chunk 格式: (namespace, update)
            namespace, update = chunk

            # 打印流式输出
            print_stream_chunk(namespace, update)

            # 记录最终回复
            if not namespace:  # 主图更新
                for node_name, node_update in update.items():
                    if "messages" in node_update:
                        for msg in node_update["messages"]:
                            if isinstance(msg, AIMessage):
                                final_response = msg.content

        print("-" * 50)

        # 输出最终回复
        if final_response:
            print()
            print(f"🤖 助手: {final_response}")

        print()
        print("-" * 70)
        print()


def run_demo_scenarios():
    """
    运行演示场景，展示系统的完整功能
    """
    print("=" * 70)
    print("🎬 演示模式 - 旅游规划多智能体系统")
    print("=" * 70)
    print()

    # 创建持久化存储
    checkpointer = MemorySaver()

    # 构建主 Agent
    agent = build_travel_agent(checkpointer=checkpointer)

    # 会话配置
    config = {"configurable": {"thread_id": "demo-session-001"}}

    # 演示场景
    demo_queries = [
        "你好，请问你能帮我做什么？",
        "我想去北京旅游，帮我查一下北京的天气",
        "我现在在上海，想去杭州，帮我查一下火车票价格",
        "广州天气怎么样？",
        "从北京到上海的火车票多少钱？",
    ]

    for i, query in enumerate(demo_queries, 1):
        print(f"\n{'='*70}")
        print(f"📌 演示场景 {i}/{len(demo_queries)}")
        print(f"{'='*70}")
        print(f"\n👤 用户: {query}")
        print()
        print("📊 执行流程:")
        print("-" * 50)

        final_response = None

        for chunk in agent.stream(
            {"messages": [HumanMessage(content=query)]},
            config=config,
            stream_mode="updates",
            subgraphs=True,
        ):
            namespace, update = chunk
            print_stream_chunk(namespace, update)

            if not namespace:
                for node_name, node_update in update.items():
                    if "messages" in node_update:
                        for msg in node_update["messages"]:
                            if isinstance(msg, AIMessage):
                                final_response = msg.content

        print("-" * 50)

        if final_response:
            print()
            print(f"🤖 助手: {final_response}")

        print()

        # 暂停一下，方便观看
        input("按 Enter 继续下一个演示...")

    print("\n" + "=" * 70)
    print("🎬 演示完成！")
    print("=" * 70)


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "--demo":
        # 运行演示模式
        run_demo_scenarios()
    else:
        # 运行交互模式
        run_travel_agent_with_stream()
