# -*- coding: utf-8 -*-
"""
@Time    : 2025/11/07 14:00
@Author  : ZhangShenao
@File    : state.py
@Desc    : 状态定义
"""

from typing import Annotated, TypedDict
from langgraph.graph.message import add_messages

from langchain_core.messages import HumanMessage, AIMessage
from typing import List


class State(TypedDict):
    """
    状态定义
    """

    messages: Annotated[List[HumanMessage | AIMessage], add_messages]  # 对话历史
    mem0_user_id: str  # Mem0用户ID，Mem0会基于用户ID进行记忆的保存与检索
