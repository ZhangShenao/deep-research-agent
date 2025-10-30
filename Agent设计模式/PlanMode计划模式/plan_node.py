# -*- coding: utf-8 -*-
"""
@Time    : 2025/9/29 13:32
@Author  : ZhangShenao
@File    : plan_node.py
@Desc    : 生成计划节点
"""

from state import PlanAndExecuteState
from llm import LLM_WITH_TOOLS
from langchain_core.messages import SystemMessage

# 生成计划的System Prompt
SYSTEM_PROMPT = """
你是一位智能助手，擅长解决用户提出的各种问题。请为用户提出的问题创建分析方案步骤。
如果有需要，可以调用工具。

你可以调用工具的列表如下：
get_fruit_price:
    获取指定的水果价格
    
    Parameters:
    -----------
    fruit_name : str
        水果名称
    
    Returns:
    --------
    str
        指定水果的价格

calculate:
    计算表达式
    
    Parameters:
    -----------
    expression : str
        表达式内容
    
    Returns:
    --------
    str
        表达式的计算结果


要求：
1.用中文列出清晰步骤
2.每个步骤标记序号
3.明确说明需要分析和执行的内容
4.只需输出计划内容，不要做任何额外的解释和说明
5.设计的方案步骤要紧紧贴合我的工具所能返回的内容，不要超出工具返回的内容
"""


def plan_node(state: PlanAndExecuteState) -> PlanAndExecuteState:
    """
    生成计划节点
    """

    # 构造消息列表
    messages = [SystemMessage(content=SYSTEM_PROMPT)] + state["messages"]

    # 调用LLM,生成计划
    plan = LLM_WITH_TOOLS.invoke(input=messages).content
    print(f"生成的计划: \n{plan}")

    # 更新状态,保存生成的计划
    state["plan"] = plan

    # 返回更新后的状态
    return state
