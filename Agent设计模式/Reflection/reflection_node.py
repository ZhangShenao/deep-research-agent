# -*- coding: utf-8 -*-
"""
@Time    : 2025/11/3 13:32
@Author  : ZhangShenao
@File    : reflection_node.py
@Desc    : 反思节点
"""

from state import CodeAndReflectionState
from llm import LLM

# 反思与优化的System Prompt
SYSTEM_PROMPT = """
你是一位资深的软件架构师，精通代码审查与优化工作。请结合用户的实际需求，检查当前代码，生成优化建议。

当前代码：
{current_code}

用户原始需求：{user_query}

检查维度：
1. 是否符合特定编程语言的规范，如 PEP8、JavaScript 规范等。
2. 是否需要进行性能优化。
3. 是否有更高效、更优雅的解决方案。
4. 是否完全解决用户需求。
5. 是否存在边界 case 容易导致 bug。
6. 如果无需优化和改进，请输出固定文本 "无需优化" 。

"""

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
    prompt = SYSTEM_PROMPT.format(
        current_code=current_code,
        user_query=user_query,
    )
    optimization_suggestion = LLM.invoke(prompt).content
    if "无需优化" in optimization_suggestion:
        print(NO_OPTIMIZATION_SUGGESTION)
        state["optimization_suggestion"] = NO_OPTIMIZATION_SUGGESTION
    else:
        print(
            f"\n【第 {state["iterations"] + 1} 轮迭代】反思与优化建议: \n{optimization_suggestion}"
        )
        state["optimization_suggestion"] = optimization_suggestion

    # 返回更新后的状态
    return state
