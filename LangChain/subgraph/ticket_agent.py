# -*- coding: utf-8 -*-
"""
@Time    : 2025/12/09
@Author  : ZhangShenao
@File    : ticket_agent.py
@Desc    : 车票查询子 Agent - 负责查询火车票价格信息
"""

from langgraph.graph import StateGraph, START, END
from langgraph.graph.state import CompiledStateGraph

from state import TicketAgentState
from tools import get_train_ticket


def ticket_query_node(state: TicketAgentState) -> dict:
    """
    车票查询节点

    调用火车票查询工具获取票价信息

    Args:
        state: 车票 Agent 状态，包含出发城市和目的城市

    Returns:
        更新后的状态，包含车票查询结果
    """
    from_city = state["from_city"]
    to_city = state["to_city"]

    # 调用火车票查询工具
    ticket_result = get_train_ticket.invoke(
        {"from_city": from_city, "to_city": to_city}
    )

    return {"ticket_result": ticket_result}


def build_ticket_agent() -> CompiledStateGraph:
    """
    构建车票查询子 Agent

    这是一个简单的单节点子图，专门负责火车票查询任务

    Returns:
        编译后的车票查询 Agent
    """
    # 创建状态图
    builder = StateGraph(TicketAgentState)

    # 添加车票查询节点
    builder.add_node("ticket_query", ticket_query_node)

    # 添加边：START -> ticket_query -> END
    builder.add_edge(START, "ticket_query")
    builder.add_edge("ticket_query", END)

    # 编译并返回子图
    # 注意：子图不需要单独配置 checkpointer，会自动继承父图的配置
    return builder.compile()


# 创建车票子 Agent 实例（供父图调用）
ticket_agent = build_ticket_agent()


if __name__ == "__main__":
    # 测试车票子 Agent
    print("=" * 50)
    print("车票查询子 Agent 测试")
    print("=" * 50)

    # 测试用例
    test_routes = [
        ("北京", "上海"),
        ("上海", "杭州"),
        ("广州", "深圳"),
        ("北京", "成都"),  # 不存在的路线
    ]

    for from_city, to_city in test_routes:
        result = ticket_agent.invoke({"from_city": from_city, "to_city": to_city})
        print(f"\n查询路线: {from_city} → {to_city}")
        print(f"查询结果: {result['ticket_result']}")
