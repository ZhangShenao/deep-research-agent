# -*- coding: utf-8 -*-
"""
@Time    : 2025/11/13 14:00
@Author  : ZhangShenao
@File    : state.py
@Desc    : 状态与上下文定义
"""

from dataclasses import dataclass
from typing import TypedDict
from langchain.agents import AgentState


@dataclass
class UserContext:
    """用户上下文信息"""

    user_id: str  # 用户ID
    user_name: str = ""  # 用户名称


class UserPreferences(TypedDict):
    """用户偏好设置"""

    language: str  # 语言
    theme: str  # 主题
    timezone: str  # 时区


class CustomAgentState(AgentState):
    """自定义 Agent 状态"""

    user_preferences: UserPreferences  # 用户偏好设置
    conversation_count: int = 0  # 对话次数
    last_interaction_time: str = ""  # 最后一次交互时间
