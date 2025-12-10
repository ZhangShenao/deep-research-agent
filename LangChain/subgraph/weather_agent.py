# -*- coding: utf-8 -*-
"""
@Time    : 2025/12/09
@Author  : ZhangShenao
@File    : weather_agent.py
@Desc    : 天气查询子 Agent - 负责查询指定城市的天气信息
"""

from langgraph.graph import StateGraph, START, END
from langgraph.graph.state import CompiledStateGraph

from state import WeatherAgentState
from tools import get_weather


def weather_query_node(state: WeatherAgentState) -> dict:
    """
    天气查询节点
    
    调用天气查询工具获取指定城市的天气信息
    
    Args:
        state: 天气 Agent 状态，包含要查询的城市
        
    Returns:
        更新后的状态，包含天气查询结果
    """
    city = state["city"]
    
    # 调用天气查询工具
    weather_result = get_weather.invoke({"city": city})
    
    return {"weather_result": weather_result}


def build_weather_agent() -> CompiledStateGraph:
    """
    构建天气查询子 Agent
    
    这是一个简单的单节点子图，专门负责天气查询任务
    
    Returns:
        编译后的天气查询 Agent
    """
    # 创建状态图
    builder = StateGraph(WeatherAgentState)
    
    # 添加天气查询节点
    builder.add_node("weather_query", weather_query_node)
    
    # 添加边：START -> weather_query -> END
    builder.add_edge(START, "weather_query")
    builder.add_edge("weather_query", END)
    
    # 编译并返回子图
    # 注意：子图不需要单独配置 checkpointer，会自动继承父图的配置
    return builder.compile()


# 创建天气子 Agent 实例（供父图调用）
weather_agent = build_weather_agent()


if __name__ == "__main__":
    # 测试天气子 Agent
    print("=" * 50)
    print("天气查询子 Agent 测试")
    print("=" * 50)
    
    # 测试用例
    test_cities = ["北京", "上海", "成都", "纽约"]
    
    for city in test_cities:
        result = weather_agent.invoke({"city": city})
        print(f"\n查询城市: {city}")
        print(f"查询结果: {result['weather_result']}")

