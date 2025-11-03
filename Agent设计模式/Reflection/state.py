# -*- coding: utf-8 -*-
"""
@Time    : 2025/11/3 13:32
@Author  : ZhangShenao
@File    : state.py
@Desc    : 状态定义
"""

from typing import TypedDict


class CodeAndReflectionState(TypedDict):
    """
    代码与反思状态定义
    """

    user_query: str  # 用户提问
    current_code: str  # 当前代码
    optimization_suggestion: str  # 优化建议
    iterations: int  # 迭代次数
