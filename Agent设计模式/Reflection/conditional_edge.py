# -*- coding: utf-8 -*-
"""
@Time    : 2025/11/3 13:32
@Author  : ZhangShenao
@File    : conditional_edge.py
@Desc    : 条件边
"""

from state import CodeAndReflectionState
from langgraph.graph import END
from reflection_node import NO_OPTIMIZATION_SUGGESTION


def conditional_edge(state: CodeAndReflectionState) -> str:
    """
    条件边
    """

    # 如果优化建议为空,则结束流程
    optimization_suggestion = state["optimization_suggestion"]
    if optimization_suggestion == NO_OPTIMIZATION_SUGGESTION:
        return END

    # 达到最大迭代次数,则结束流程
    if state["iterations"] >= 3:
        print("达到最大迭代次数，跳过反思优化，直接返回结果")
        return END

    # 否则进行写一轮迭代,继续优化代码
    return "code_node"
