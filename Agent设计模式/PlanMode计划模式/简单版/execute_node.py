# -*- coding: utf-8 -*-
"""
@Time    : 2025/9/29 13:32
@Author  : ZhangShenao
@File    : execute_node.py
@Desc    : 执行计划节点
"""

from state import PlanState
from llm import LLM_WITH_TOOLS
from prompt import EXEC_PLAN_PROMPT
from langchain_core.messages import SystemMessage


def execute_node(state: PlanState) -> PlanState:
    """
    执行计划节点
    """

    print("=" * 100)
    print("进入execute_node")

    # 构造消息列表
    message = [SystemMessage(content=EXEC_PLAN_PROMPT.format(plan=state["plan"]))]
    messages = message + state["messages"]

    # 调用LLM,执行计划
    resp = LLM_WITH_TOOLS.invoke(input=messages)
    print(f"计划执行结果: \n{resp}")

    # 更新状态
    state["messages"].append(resp)

    # 返回更新后的状态
    return state
