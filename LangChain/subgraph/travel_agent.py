# -*- coding: utf-8 -*-
"""
@Time    : 2025/12/09
@Author  : ZhangShenao
@File    : travel_agent.py
@Desc    : 旅游规划主 Agent - 负责意图识别和子 Agent 调度
"""

import re
from typing import Optional

from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langgraph.graph import StateGraph, START, END
from langgraph.graph.state import CompiledStateGraph
from langgraph.checkpoint.base import BaseCheckpointSaver
from langgraph.checkpoint.memory import MemorySaver

from state import TravelAgentState
from llm import LLM
from weather_agent import weather_agent
from ticket_agent import ticket_agent


# 系统提示词：意图识别
INTENT_SYSTEM_PROMPT = """你是一个旅游规划助手的意图识别模块。

你需要分析用户的输入，判断用户的意图属于以下哪一类：
1. weather - 用户想查询某个城市的天气
2. ticket - 用户想查询火车票信息（需要出发地和目的地）
3. chat - 用户只是在闲聊，或者意图不明确

请直接输出意图类别（weather/ticket/chat），不要输出其他内容。

示例：
- 用户输入："北京今天天气怎么样？" → 输出：weather
- 用户输入："我想从上海去杭州，帮我查一下火车票" → 输出：ticket
- 用户输入："你好" → 输出：chat
- 用户输入："帮我查一下从北京到上海的火车票价格" → 输出：ticket
- 用户输入："明天广州的天气如何" → 输出：weather
"""

# 系统提示词：信息提取（天气）
WEATHER_EXTRACT_PROMPT = """你是一个信息提取模块。

请从用户的输入中提取出要查询天气的城市名称。

规则：
1. 只输出城市名称，不要带"市"字
2. 如果找不到城市名称，输出"未知"
3. 不要输出其他任何内容

示例：
- 用户输入："北京今天天气怎么样？" → 输出：北京
- 用户输入："查一下上海市的天气" → 输出：上海
- 用户输入："明天深圳天气如何" → 输出：深圳
"""

# 系统提示词：信息提取（车票）
TICKET_EXTRACT_PROMPT = """你是一个信息提取模块。

请从用户的输入中提取出出发城市和目的城市。

规则：
1. 输出格式为：出发城市,目的城市
2. 城市名称不要带"市"字
3. 如果找不到其中一个城市，对应位置输出"未知"
4. 不要输出其他任何内容

示例：
- 用户输入："我想从北京去上海" → 输出：北京,上海
- 用户输入："查一下上海到杭州的火车票" → 输出：上海,杭州
- 用户输入："广州市到深圳市的票价" → 输出：广州,深圳
"""

# 系统提示词：回复生成
RESPONSE_SYSTEM_PROMPT = """你是一个友好的旅游规划助手。

你需要根据查询结果，用自然、友好的语言回复用户。

规则：
1. 回复要简洁明了
2. 如果有查询结果，要把关键信息清晰地传达给用户
3. 可以适当加一些友好的话语，如"祝您旅途愉快"等
"""


def intent_recognition_node(state: TravelAgentState) -> dict:
    """
    意图识别节点（Intent Recognition Node）

    使用 LLM 分析用户输入，识别用户意图

    Args:
        state: 主 Agent 状态

    Returns:
        更新后的状态，包含识别出的意图
    """
    # 获取最后一条用户消息
    messages = state["messages"]
    last_message = messages[-1] if messages else None

    if not last_message or not isinstance(last_message, HumanMessage):
        return {"intent": "chat"}

    user_input = last_message.content

    # 调用 LLM 进行意图识别
    response = LLM.invoke(
        [SystemMessage(content=INTENT_SYSTEM_PROMPT), HumanMessage(content=user_input)]
    )

    intent_text = response.content.strip().lower()

    # 解析意图
    if "weather" in intent_text:
        intent = "weather"
    elif "ticket" in intent_text:
        intent = "ticket"
    else:
        intent = "chat"

    print(f"🎯 [意图识别] 用户意图: {intent}")

    return {"intent": intent}


def router(state: TravelAgentState) -> str:
    """
    路由函数（Router）

    根据识别出的意图，决定下一步路由到哪个节点

    Args:
        state: 主 Agent 状态

    Returns:
        下一个节点的名称
    """
    intent = state.get("intent", "chat")

    if intent == "weather":
        return "call_weather_agent"
    elif intent == "ticket":
        return "call_ticket_agent"
    else:
        return "chat_response"


def call_weather_agent_node(state: TravelAgentState) -> dict:
    """
    调用天气子 Agent 节点（Invoke Weather Subgraph）

    提取城市信息，调用天气子 Agent，并返回结果

    这里演示了 "Invoke a Graph from a Node" 的模式：
    1. 将父图状态转换为子图状态
    2. 调用子图
    3. 将子图结果转换回父图状态

    Args:
        state: 主 Agent 状态

    Returns:
        更新后的状态，包含天气查询结果
    """
    # 获取用户消息
    messages = state["messages"]
    last_message = messages[-1].content if messages else ""

    # 使用 LLM 提取城市名称
    response = LLM.invoke(
        [
            SystemMessage(content=WEATHER_EXTRACT_PROMPT),
            HumanMessage(content=last_message),
        ]
    )

    city = response.content.strip()
    print(f"🌤️ [天气查询] 提取城市: {city}")

    # 状态转换：TravelAgentState -> WeatherAgentState
    subgraph_input = {"city": city}

    # 调用天气子 Agent（Invoke Subgraph）
    subgraph_output = weather_agent.invoke(subgraph_input)

    # 状态转换：WeatherAgentState -> TravelAgentState
    weather_result = subgraph_output.get("weather_result", "查询失败")

    print(f"🌤️ [天气查询] 查询结果: {weather_result}")

    return {"sub_result": weather_result}


def call_ticket_agent_node(state: TravelAgentState) -> dict:
    """
    调用车票子 Agent 节点（Invoke Ticket Subgraph）

    提取出发地和目的地信息，调用车票子 Agent，并返回结果

    Args:
        state: 主 Agent 状态

    Returns:
        更新后的状态，包含车票查询结果
    """
    # 获取用户消息
    messages = state["messages"]
    last_message = messages[-1].content if messages else ""

    # 使用 LLM 提取城市信息
    response = LLM.invoke(
        [
            SystemMessage(content=TICKET_EXTRACT_PROMPT),
            HumanMessage(content=last_message),
        ]
    )

    cities_text = response.content.strip()

    # 解析城市
    if "," in cities_text:
        parts = cities_text.split(",")
        from_city = parts[0].strip()
        to_city = parts[1].strip() if len(parts) > 1 else "未知"
    else:
        from_city = "未知"
        to_city = "未知"

    print(f"🚄 [车票查询] 出发地: {from_city}, 目的地: {to_city}")

    # 状态转换：TravelAgentState -> TicketAgentState
    subgraph_input = {"from_city": from_city, "to_city": to_city}

    # 调用车票子 Agent（Invoke Subgraph）
    subgraph_output = ticket_agent.invoke(subgraph_input)

    # 状态转换：TicketAgentState -> TravelAgentState
    ticket_result = subgraph_output.get("ticket_result", "查询失败")

    print(f"🚄 [车票查询] 查询结果: {ticket_result}")

    return {"sub_result": ticket_result}


def response_node(state: TravelAgentState) -> dict:
    """
    回复生成节点（Response Node）

    根据子 Agent 的查询结果，生成友好的回复消息

    Args:
        state: 主 Agent 状态

    Returns:
        更新后的状态，包含 AI 回复消息
    """
    sub_result = state.get("sub_result", "")
    intent = state.get("intent", "chat")

    # 获取用户原始消息
    messages = state["messages"]
    last_message = messages[-1].content if messages else ""

    # 构建上下文
    context = f"""用户问题：{last_message}
查询结果：{sub_result}

请根据以上信息，用友好自然的语言回复用户。"""

    # 使用 LLM 生成回复
    response = LLM.invoke(
        [SystemMessage(content=RESPONSE_SYSTEM_PROMPT), HumanMessage(content=context)]
    )

    ai_response = response.content.strip()

    print(f"💬 [回复生成] {ai_response[:50]}...")

    return {"messages": [AIMessage(content=ai_response)]}


def chat_response_node(state: TravelAgentState) -> dict:
    """
    闲聊回复节点（Chat Response Node）

    处理闲聊类型的对话

    Args:
        state: 主 Agent 状态

    Returns:
        更新后的状态，包含 AI 回复消息
    """
    # 获取用户消息
    messages = state["messages"]
    last_message = messages[-1].content if messages else ""

    # 构建聊天提示
    chat_prompt = """你是一个友好的旅游规划助手。

你可以帮助用户：
1. 查询各大城市的天气情况
2. 查询城市之间的火车票价格

请用友好的语言与用户交流，并引导用户使用你的功能。"""

    # 使用 LLM 生成回复
    response = LLM.invoke(
        [SystemMessage(content=chat_prompt), HumanMessage(content=last_message)]
    )

    ai_response = response.content.strip()

    print(f"💬 [闲聊回复] {ai_response[:50]}...")

    return {"messages": [AIMessage(content=ai_response)], "sub_result": None}


def build_travel_agent(
    checkpointer: Optional[BaseCheckpointSaver] = None,
) -> CompiledStateGraph:
    """
    构建旅游规划主 Agent（Parent Graph）

    创建一个完整的旅游规划 Agent 图，包括：
    - 意图识别节点：分析用户意图
    - 天气查询节点：调用天气子 Agent
    - 车票查询节点：调用车票子 Agent
    - 回复生成节点：生成友好回复
    - 闲聊节点：处理闲聊

    Args:
        checkpointer: 检查点存储器，用于持久化状态

    Returns:
        编译后的主 Agent 图
    """
    # 创建状态图
    builder = StateGraph(TravelAgentState)

    # 添加节点
    builder.add_node("intent_recognition", intent_recognition_node)
    builder.add_node("call_weather_agent", call_weather_agent_node)
    builder.add_node("call_ticket_agent", call_ticket_agent_node)
    builder.add_node("response", response_node)
    builder.add_node("chat_response", chat_response_node)

    # 添加边
    builder.add_edge(START, "intent_recognition")

    # 添加条件边：根据意图路由到不同节点
    builder.add_conditional_edges(
        source="intent_recognition",
        path=router,
        path_map={
            "call_weather_agent": "call_weather_agent",
            "call_ticket_agent": "call_ticket_agent",
            "chat_response": "chat_response",
        },
    )

    # 子 Agent 执行完后，生成回复
    builder.add_edge("call_weather_agent", "response")
    builder.add_edge("call_ticket_agent", "response")

    # 回复完成后结束
    builder.add_edge("response", END)
    builder.add_edge("chat_response", END)

    # 如果没有提供 checkpointer，使用内存存储
    if checkpointer is None:
        checkpointer = MemorySaver()

    # 编译图（Checkpointer 会自动传播到子图）
    compiled_graph = builder.compile(checkpointer=checkpointer)

    return compiled_graph


def save_agent_graph_image(
    agent: CompiledStateGraph, output_path: str = "./travel_agent_graph.png"
):
    """
    保存 Agent 图的可视化图像

    Args:
        agent: 编译后的 Agent
        output_path: 输出文件路径
    """
    try:
        agent.get_graph().draw_mermaid_png(output_file_path=output_path)
        print(f"✅ Agent 图已保存到: {output_path}")
    except Exception as e:
        print(f"❌ 保存 Agent 图失败: {e}")


if __name__ == "__main__":
    # 测试主 Agent
    print("=" * 60)
    print("旅游规划主 Agent 测试")
    print("=" * 60)

    # 构建 Agent
    agent = build_travel_agent()

    # 保存图像
    save_agent_graph_image(agent)

    # 测试配置
    config = {"configurable": {"thread_id": "test-001"}}

    # 测试用例
    test_queries = [
        "你好，请问你能做什么？",
        "北京今天天气怎么样？",
        "我想从上海去杭州，帮我查一下火车票",
    ]

    for query in test_queries:
        print(f"\n{'='*60}")
        print(f"用户: {query}")
        print("-" * 60)

        result = agent.invoke(
            {"messages": [HumanMessage(content=query)]}, config=config
        )

        # 获取 AI 回复
        ai_messages = [m for m in result["messages"] if isinstance(m, AIMessage)]
        if ai_messages:
            print(f"\n助手: {ai_messages[-1].content}")
