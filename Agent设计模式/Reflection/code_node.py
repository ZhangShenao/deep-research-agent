# -*- coding: utf-8 -*-
"""
@Time    : 2025/11/3 13:32
@Author  : ZhangShenao
@File    : code_node.py
@Desc    : 代码生成节点
"""

from llm import LLM
from state import CodeAndReflectionState

# 生成代码的System Prompt
SYSTEM_PROMPT = """
你是一位资深的软件开发工程师，精通各种编程语言。请根据用户需求生成最合适的代码。
要求：
1. 直接生成代码，不要包含任何其它内容。
2. 如果有具体的优化建议，则严格按照优化建议修改当前代码。

用户需求：{user_query}
当前代码：{current_code}
优化建议: {optimization_suggestion}

"""


def code_node(state: CodeAndReflectionState) -> CodeAndReflectionState:
    """
    代码生成节点
    """

    # 获取当前迭代次数
    iterations = state["iterations"]

    # 第一次迭代,直接生成代码
    if iterations == 0:
        prompt = SYSTEM_PROMPT.format(
            user_query=state["user_query"],
            current_code="无",
            optimization_suggestion="无",
        )
    else:
        prompt = SYSTEM_PROMPT.format(
            user_query=state["user_query"],
            current_code=state["current_code"],
            optimization_suggestion=state["optimization_suggestion"],
        )

    # 调用LLM,生成代码
    code = LLM.invoke(prompt).content

    # 更新状态
    state["current_code"] = code
    state["iterations"] = iterations + 1
    print(f"\n【第 {iterations + 1} 轮迭代】代码生成结果: \n{code}")

    # 返回更新后的状态
    return state
