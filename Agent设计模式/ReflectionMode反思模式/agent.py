# -*- coding: utf-8 -*-
"""
@Time    : 2025/10/9 13:32
@Author  : ZhangShenao
@File    : agent.py
@Desc    : ReflectionMode反思模式主Agent
"""

from langgraph.graph import START, StateGraph
from langgraph.graph.state import CompiledStateGraph
from state import CodeAndReflectionState
from code_node import code_node
from reflection_node import reflection_and_optimization_node
from conditional_node import conditional_node


def build_agent() -> CompiledStateGraph:
    """
    构建Agent
    """

    # 构造Graph图
    graph = StateGraph(CodeAndReflectionState)

    # 添加Node节点
    graph.add_node("code_node", code_node)
    graph.add_node("reflection_and_optimization_node", reflection_and_optimization_node)

    # 添加Edge边
    graph.add_edge(START, "code_node")
    graph.add_edge("code_node", "reflection_and_optimization_node")
    graph.add_conditional_edges(
        source="reflection_and_optimization_node", path=conditional_node
    )

    # 编译Graph图并返回
    return graph.compile()


def run_agent(agent: CompiledStateGraph, user_query: str) -> str:
    """
    运行Agent
    """

    # 初始化状态
    init_state = CodeAndReflectionState(
        user_query=user_query, current_code="", optimization_suggestion="", iterations=0
    )

    # 运行Agent
    result = agent.invoke(init_state)

    # 返回最终结果
    return result["current_code"]


if __name__ == "__main__":
    # 构建Agent
    agent: CompiledStateGraph = build_agent()

    # 运行Agent
    result = run_agent(agent, "帮我用python帮我实现快速排序算法")

    print("Agent运行结果:")
    print(result)
