# -*- coding: utf-8 -*-
"""
@Time    : 2025/9/28 14:47
@Author  : ZhangShenao
@File    : llm_node.py
@Desc    : LLM节点
"""

from llm import DEEPSEEK
from state import GlobalState
from state import Action


def llm_node(state: GlobalState) -> GlobalState:
    """
    LLM节点
    """

    print("=" * 100)
    print("enter llm_node")

    # 获取历史消息列表
    messages = state["messages"]

    # 调用LLM,获取结果
    resp = DEEPSEEK.invoke(messages)
    print(resp)

    # 如果模型生成了python代码,则返回工具调用信息
    content = resp.content
    if "```python" in content:
        code_blocks = content.split("```python")
        code = code_blocks[1].split("```")[0].strip()
        action = Action(tool_name="execute_python_code", tool_args={"code": code})
        return {"messages": [resp], "actions": [action], "final_result": ""}

    # 模型直接生成回复,更新状态
    return {"messages": [resp], "actions": [], "final_result": content}
