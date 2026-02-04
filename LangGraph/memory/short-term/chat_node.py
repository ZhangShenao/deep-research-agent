# -*- coding: utf-8 -*-
"""
@Time    : 2026/02/04
@Author  : ZhangShenao
@File    : chat_node.py
@Desc    : 对话节点
"""

SYSTEM_PROMPT = """
你是一位智能的聊天助手，请根据用户的问题，给出相应的回答。
"""

SUMMARY_PROMPT = """
以下是历史对话的摘要，请根据最新对话和摘要信息，进行回答。

{summary}
"""

from state import AgentState
from llm import LLM_WITH_TOOLS
from langchain_core.messages import SystemMessage


def chat_node(state: AgentState) -> dict:
    """
    对话节点
    """

    # 从状态中获取摘要信息
    summary = state["summary"]

    # 根据是否存在摘要信息，构造系统提示词
    system_prompt = SYSTEM_PROMPT
    if summary is not None:
        system_prompt += SUMMARY_PROMPT.format(summary=summary)

    # 构造完整消息列表
    messages = [SystemMessage(content=system_prompt)] + state["messages"]

    # 调用LLM,生成回复
    response = LLM_WITH_TOOLS.invoke(messages)

    # 返回更新后的状态
    return {"messages": response}
