# -*- coding: utf-8 -*-
"""
@Time    : 2025/9/29 13:32
@Author  : ZhangShenao
@File    : execute_node.py
@Desc    : 执行计划节点
"""

from state import PlanAndExecuteState
from llm import LLM_WITH_TOOLS
from langchain_core.messages import SystemMessage

# 执行计划的System Prompt
SYSTEM_PROMPT = """
你是一位思路清晰、有条理的智能助手，你必须严格按照以下计划执行任务：
    
当前计划：
{plan}

如果你认为计划已经执行到最后一步了，请在内容的末尾加上 Final Answer 字样

示例：
这个问题的最终答案是99.99。
Final Answer
"""


def execute_node(state: PlanAndExecuteState) -> PlanAndExecuteState:
    """
    执行计划节点
    """

    # 获取迭代次数
    step = state["step"]

    # 构造消息列表
    message = [SystemMessage(content=SYSTEM_PROMPT.format(plan=state["plan"]))]
    messages = message + state["messages"]

    # 调用LLM,执行计划
    resp = LLM_WITH_TOOLS.invoke(input=messages)
    print(f"\n【第 {step + 1} 步】{resp.content}")

    # 更新状态,保存执行结果和迭代次数
    state["messages"].append(resp)
    state["step"] = step + 1

    # 返回更新后的状态
    return state
