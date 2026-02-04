# -*- coding: utf-8 -*-
"""
@Time    : 2026/02/04
@Author  : ZhangShenao
@File    : summary_node.py
@Desc    : 摘要节点
"""

from state import AgentState
from langchain_core.messages import SystemMessage
from llm import LLM_WITH_TOOLS
from langgraph.graph.message import RemoveMessage

SYSTEM_PROMPT = """
请根据用户与AI助手的历史聊天记录，提前关键信息，生成精准的摘要。
"""

SUMMARY_PROMPT = """
以下是当前最新的摘要

{summary}
"""


def summary_node(state: AgentState) -> dict:
    """
    摘要节点
    """

    # 获取消息列表
    messages = state["messages"]

    # 获取摘要信息
    summary = state["summary"]

    # 根据系统提示词和消息列表，生成摘要
    system_message = SystemMessage(content=SYSTEM_PROMPT)
    messages = [system_message] + messages

    # 构造完整消息列表
    messages = [SystemMessage(content=SYSTEM_PROMPT)] + messages

    # 调用LLM，生成最新的摘要
    summary = LLM_WITH_TOOLS.invoke(messages).content

    # 摘要生成成功,删除最近2条消息之前的所有消息
    # 使用RemoveMessage来标记要删除的消息
    delete_messages = [RemoveMessage(id=m.id) for m in state["messages"][:-2]]

    return {"summary": summary, "messages": delete_messages}
