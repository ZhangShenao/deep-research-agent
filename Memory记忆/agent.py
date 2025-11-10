# -*- coding: utf-8 -*-
"""
@Time    : 2025/11/07 14:00
@Author  : ZhangShenao
@File    : agent.py
@Desc    : Agent
"""

from langgraph.graph import START, StateGraph
from langgraph.graph.state import CompiledStateGraph
from chat_node import chat_node
from state import State
from langchain_core.messages import HumanMessage


def build_agent() -> CompiledStateGraph:
    """
    构建Agent
    """

    # 构造Graph图
    graph = StateGraph(State)

    # 添加Node节点
    graph.add_node("chat_node", chat_node)

    # 添加Edge边
    graph.add_edge(START, "chat_node")
    graph.add_edge("chat_node", "chat_node")

    # 编译Agent
    agent = graph.compile()

    # 返回编译后的Agent
    return agent


def run_conversation(agent: CompiledStateGraph, user_input: str, mem0_user_id: str):
    """
    运行对话
    """

    # 构造配置,指定Mem0 user_id 为 thread_id
    config = {"configurable": {"thread_id": mem0_user_id}}

    # 设置State状态
    state = {
        "messages": [HumanMessage(content=user_input)],
        "mem0_user_id": mem0_user_id,
    }

    # 以Stream方式运行Agent
    for event in agent.stream(state, config):
        for value in event.values():
            if value.get("messages"):
                print("智能助手:", value["messages"][-1].content)
                return
