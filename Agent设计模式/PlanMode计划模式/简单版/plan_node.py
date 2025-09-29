# -*- coding: utf-8 -*-
"""
@Time    : 2025/9/29 13:32
@Author  : ZhangShenao
@File    : plan_node.py
@Desc    : 生成计划节点
"""

from state import PlanState
from llm import LLM_WITH_TOOLS
from prompt import GENERATE_PLAN_PROMPT
from langchain_core.messages import SystemMessage


def plan_node(state: PlanState) -> PlanState:
    """
    生成计划节点
    """

    print("=" * 100)
    print("进入plan_node")

    # 构造消息列表
    messages = [SystemMessage(content=GENERATE_PLAN_PROMPT)] + state["messages"]

    # 调用LLM,生成计划
    plan = LLM_WITH_TOOLS.invoke(input=messages).content
    print("=" * 100)
    print(f"生成的计划: \n{plan}")

    # 更新状态
    state["plan"] = plan

    # 返回更新后的状态
    return state
