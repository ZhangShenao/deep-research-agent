# -*- coding: utf-8 -*-
"""
@Time    : 2025/12/06
@Author  : ZhangShenao
@File    : state.py
@Desc    : Agent 状态定义
"""

from typing import Annotated, Optional
from typing_extensions import TypedDict
from langgraph.graph.message import add_messages


class AgentState(TypedDict):
    """
    客服 Agent 状态定义
    
    Attributes:
        messages: 消息历史列表，使用 add_messages reducer 自动合并新消息
        user_id: 用户 ID，用于标识当前对话的用户
        session_info: 可选的会话附加信息
    """
    messages: Annotated[list, add_messages]
    user_id: Optional[str]
    session_info: Optional[dict]

