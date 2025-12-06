# -*- coding: utf-8 -*-
"""
@Time    : 2025/12/06
@Author  : ZhangShenao
@File    : nodes.py
@Desc    : Agent 节点定义
"""

from langchain_core.messages import SystemMessage, AIMessage
from state import AgentState
from llm import LLM
from tools import ALL_TOOLS


# 系统提示词
SYSTEM_PROMPT = """你是一位专业的电商客服助手，负责回答用户关于商品和订单的问题。

你的职责包括：
1. 查询商品价格、库存和详细信息
2. 查询订单状态和物流信息
3. 解答用户的疑问

注意事项：
- 对于不确定或无法处理的问题，请使用 ask_human 工具向人类客服请求帮助
- 保持专业、友好的服务态度
- 回答要简洁明了，直接解决用户问题

可用工具说明：
- query_product_price: 查询商品价格
- query_product_stock: 查询商品库存
- query_product_info: 查询商品详细信息
- query_order_status: 查询订单状态
- list_available_products: 列出所有可购买的商品
- ask_human: 遇到无法处理的问题时，向人类客服请求帮助
"""


# 将模型绑定好工具
LLM_WITH_TOOLS = LLM.bind_tools(ALL_TOOLS)


def chatbot_node(state: AgentState) -> dict:
    """
    聊天机器人节点
    
    处理用户消息，调用 LLM 生成回复或工具调用。
    
    Args:
        state: 当前状态
        
    Returns:
        更新后的状态
    """
    messages = state["messages"]
    
    # 如果消息列表为空或第一条不是系统消息，添加系统提示
    if not messages or not isinstance(messages[0], SystemMessage):
        messages = [SystemMessage(content=SYSTEM_PROMPT)] + list(messages)
    
    # 调用 LLM
    response = LLM_WITH_TOOLS.invoke(messages)
    
    return {"messages": [response]}


async def async_chatbot_node(state: AgentState) -> dict:
    """
    异步聊天机器人节点
    
    处理用户消息，异步调用 LLM 生成回复或工具调用。
    
    Args:
        state: 当前状态
        
    Returns:
        更新后的状态
    """
    messages = state["messages"]
    
    # 如果消息列表为空或第一条不是系统消息，添加系统提示
    if not messages or not isinstance(messages[0], SystemMessage):
        messages = [SystemMessage(content=SYSTEM_PROMPT)] + list(messages)
    
    # 异步调用 LLM
    response = await LLM_WITH_TOOLS.ainvoke(messages)
    
    return {"messages": [response]}

