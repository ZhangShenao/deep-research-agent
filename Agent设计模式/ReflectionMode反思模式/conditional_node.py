# -*- coding: utf-8 -*-
"""
@Time    : 2025/10/9 13:32
@Author  : ZhangShenao
@File    : conditional_node.py
@Desc    : 条件节点
"""

from state import CodeAndReflectionState
from llm import LLM
from prompt import REFLECTION_PROMPT
from langchain_core.messages import SystemMessage
from langgraph.graph import END
from reflection_node import NO_OPTIMIZATION_SUGGESTION


def conditional_node(state: CodeAndReflectionState) -> str:
    """
    条件节点
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
