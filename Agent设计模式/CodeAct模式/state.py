# -*- coding: utf-8 -*-
"""
@Time    : 2025/9/28 14:47
@Author  : ZhangShenao
@File    : state.py
@Desc    : LangGraph状态管理
"""

# 第三方库导入
from typing import Annotated, TypedDict
from langgraph.graph.message import add_messages


class Action(TypedDict):
    """
    动作定义
    """

    tool_name: str  # 工具名称
    tool_args: dict  # 工具参数


class GlobalState(TypedDict):
    """
    全局状态定义
    """

    messages: Annotated[list, add_messages]  # 对话历史
    actions: list[Action]  # 动作列表
    final_result: str  # 最终结果
