# -*- coding: utf-8 -*-
"""
@Time    : 2025/12/09
@Author  : ZhangShenao
@File    : state.py
@Desc    : 状态定义 - 父图和子图的状态结构
"""

from typing import Annotated, Optional, Literal
from typing_extensions import TypedDict
from langgraph.graph.message import add_messages


class TravelAgentState(TypedDict):
    """
    旅游规划主 Agent 状态定义（Parent State）

    Attributes:
        messages: 对话消息历史，使用 add_messages reducer 自动合并
        intent: 用户意图，由 LLM 识别得出
        sub_result: 子 Agent 返回的结果
    """

    messages: Annotated[list, add_messages]
    intent: Optional[Literal["weather", "ticket", "chat"]]
    sub_result: Optional[str]


class WeatherAgentState(TypedDict):
    """
    天气查询子 Agent 状态定义（Subgraph State）

    与父图状态完全独立，通过状态转换函数进行数据传递

    Attributes:
        city: 要查询天气的城市名称
        weather_result: 天气查询结果
    """

    city: str
    weather_result: Optional[str]


class TicketAgentState(TypedDict):
    """
    车票查询子 Agent 状态定义（Subgraph State）

    与父图状态完全独立，通过状态转换函数进行数据传递

    Attributes:
        from_city: 出发城市
        to_city: 目的城市
        ticket_result: 车票查询结果
    """

    from_city: str
    to_city: str
    ticket_result: Optional[str]
