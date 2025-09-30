# -*- coding: utf-8 -*-
"""
@Time    : 2025/9/29 13:32
@Author  : ZhangShenao
@File    : agent.py
@Desc    : PlanMode主Agent
"""

from langgraph.graph import START, StateGraph
from langgraph.graph.state import CompiledStateGraph
from state import PlanState
from plan_node import plan_node
from execute_node import execute_node
from should_continue_node import should_continue_node
from tool_node import tool_node
from langchain_core.messages import HumanMessage


def build_agent() -> CompiledStateGraph:
    """
    构建Agent
    """

    # 构造Graph图
    graph = StateGraph(PlanState)

    # 添加Node节点
    graph.add_node("plan_node", plan_node)
    graph.add_node("execute_node", execute_node)
    graph.add_node("tool_node", tool_node)

    # 添加Edge边
    graph.add_edge(START, "plan_node")
    graph.add_edge("plan_node", "execute_node")
    graph.add_conditional_edges(source="execute_node", path=should_continue_node)
    graph.add_edge("tool_node", "execute_node")

    # 编译Graph图并返回
    return graph.compile()


def run_agent(agent: CompiledStateGraph, user_query: str) -> str:
    """
    运行Agent
    """

    # 初始化状态
    messages = [HumanMessage(content=user_query)]
    init_state = PlanState(plan="", messages=messages)

    # 运行Agent
    result = agent.invoke(init_state)

    # 返回最终结果
    return result["messages"][-1].content


if __name__ == "__main__":
    # 构建Agent
    agent: CompiledStateGraph = build_agent()

    # 运行Agent
    result = run_agent(agent, "我想买5斤苹果和4斤香蕉，总共需要多少钱？")

    print("=" * 100)
    print("Agent运行结果:")
    print(result)
