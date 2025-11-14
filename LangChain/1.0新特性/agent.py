# -*- coding: utf-8 -*-
"""
@Time    : 2025/11/14 14:00
@Author  : ZhangShenao
@File    : agent.py
@Desc    : 主Agent
"""

from tools import (
    get_user_info,
    update_user_preferences,
    get_weather,
    calculate,
    remember_fact,
    recall_facts,
    STORE,
)
from state import CustomAgentState, UserContext
from langgraph.checkpoint.memory import InMemorySaver
from langchain.agents import create_agent
from langgraph.graph.state import CompiledStateGraph


def create_smart_agent() -> CompiledStateGraph:
    """创建Agent"""

    agent = create_agent(
        model="deepseek:deepseek-chat",  # 通过统一api指定模型
        tools=[
            get_user_info,
            update_user_preferences,
            get_weather,
            calculate,
            remember_fact,
            recall_facts,
        ],  # 指定工具列表
        system_prompt=(  # 指定系统提示词
            "你是一位智能助手，具有记忆能力。"
            "你可以获取和更新用户信息、查询天气、执行计算、记住和回忆事实。"
        ),
        state_schema=CustomAgentState,  # 指定状态模式
        context_schema=UserContext,  # 指定上下文模式
        store=STORE,  # 指定长期记忆
        checkpointer=InMemorySaver(),  # 指定短期记忆
    )
    return agent
