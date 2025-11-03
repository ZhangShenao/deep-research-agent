# -*- coding: utf-8 -*-
"""
@Time    : 2025/11/3 13:32
@Author  : ZhangShenao
@File    : agent.py
@Desc    : Reflectio反思模式主Agent
"""

from langgraph.graph import START, StateGraph
from langgraph.graph.state import CompiledStateGraph
from state import CodeAndReflectionState
from code_node import code_node
from reflection_node import reflection_and_optimization_node
from conditional_edge import conditional_edge
from langgraph.graph import END


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
        source="reflection_and_optimization_node",
        path=conditional_edge,
        path_map={
            "code_node": "code_node",
            END: END,
        },
    )

    # 编译Agent
    agent = graph.compile()

    # 打印Agent节点结构图,并保存到本地
    agent.get_graph().draw_mermaid_png(output_file_path="./agent.png")

    # 返回编译后的Agent
    return agent


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
    result = run_agent(agent, "帮我写一段python代码，计算1~10000的累加和")

    print("\n\nAgent运行结果:")
    print(result)
