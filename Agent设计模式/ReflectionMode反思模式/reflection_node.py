# -*- coding: utf-8 -*-
"""
@Time    : 2025/10/9 13:32
@Author  : ZhangShenao
@File    : reflection_node.py
@Desc    : 反思节点
"""

from state import CodeAndReflectionState
from llm import LLM
from prompt import REFLECTION_PROMPT

NO_OPTIMIZATION_SUGGESTION = "当前代码已经达到最优，无需优化"


def reflection_and_optimization_node(
    state: CodeAndReflectionState,
) -> CodeAndReflectionState:
    """
    反思与优化节点
    """

    # 获取当前代码
    current_code = state["current_code"]
    user_query = state["user_query"]

    # 调用LLM,生成反思与优化建议
    prompt = REFLECTION_PROMPT.format(
        current_code=current_code,
        user_query=user_query,
    )
    optimization_suggestion = LLM.invoke(prompt).content
    if "无需优化" in optimization_suggestion:
        print(NO_OPTIMIZATION_SUGGESTION)
        state["optimization_suggestion"] = NO_OPTIMIZATION_SUGGESTION
    else:
        print(f"反思与优化建议: \n{optimization_suggestion}")
        state["optimization_suggestion"] = optimization_suggestion

    # 返回更新后的状态
    return state
