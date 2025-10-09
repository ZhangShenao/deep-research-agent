# -*- coding: utf-8 -*-
"""
@Time    : 2025/10/9 13:32
@Author  : ZhangShenao
@File    : code_node.py
@Desc    : 代码生成节点
"""

from llm import LLM
from prompt import CODE_PROMPT
from langchain_core.messages import SystemMessage
from state import CodeAndReflectionState


def code_node(state: CodeAndReflectionState) -> CodeAndReflectionState:
    """
    代码生成节点
    """

    # 获取当前迭代次数
    iterations = state["iterations"]

    # 第一次迭代,直接生成代码
    if iterations == 0:
        prompt = CODE_PROMPT.format(
            user_query=state["user_query"],
            current_code="无",
            optimization_suggestion="无",
        )
    else:
        prompt = CODE_PROMPT.format(
            user_query=state["user_query"],
            current_code=state["current_code"],
            optimization_suggestion=state["optimization_suggestion"],
        )

    # 调用LLM,生成代码
    code = LLM.invoke(prompt).content

    # 更新状态
    state["current_code"] = code
    state["iterations"] = iterations + 1
    print(f"第 {iterations + 1} 次迭代, 代码生成结果: \n{code}")

    # 返回更新后的状态
    return state
