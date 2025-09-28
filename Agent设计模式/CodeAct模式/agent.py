# -*- coding: utf-8 -*-
"""
@Time    : 2025/9/28 14:47
@Author  : ZhangShenao
@File    : agent.py
@Desc    : 主Agent
"""

from langgraph.graph import START, StateGraph
from langgraph.graph.state import CompiledStateGraph
from state import GlobalState
from llm_node import llm_node
from process_node import process_node
from tool_node import tool_node
from prompt import SYSTEM_PROMPT


def build_agent() -> CompiledStateGraph:
    """
    构建Agent
    """

    # 构造Graph图
    graph = StateGraph(GlobalState)

    # 添加Node节点
    graph.add_node("llm_node", llm_node)
    graph.add_node("process_node", process_node)
    graph.add_node("tool_node", tool_node)

    # 添加Edge边
    graph.add_edge(START, "llm_node")
    graph.add_conditional_edges(source="llm_node", path=process_node)
    graph.add_edge("tool_node", "llm_node")

    # 编译Graph图并返回
    return graph.compile()


def run_agent(agent: CompiledStateGraph, user_query: str) -> str:
    """
    运行Agent
    """

    # 初始化状态
    from langchain_core.messages import SystemMessage, HumanMessage

    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=user_query),
    ]
    init_state = {"messages": messages, "actions": [], "final_result": ""}

    # 运行Agent
    ret = agent.invoke(init_state)
    return ret.get("final_result", "未生成结果")


if __name__ == "__main__":
    # 构建Agent
    agent: CompiledStateGraph = build_agent()

    # 运行Agent
    ret = run_agent(agent, "帮我计算1~100的累加和")

    print("=" * 100)
    print("Agent运行结果:")
    print(ret)
