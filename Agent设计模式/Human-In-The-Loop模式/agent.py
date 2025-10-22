# -*- coding: utf-8 -*-
"""
@Time    : 2025/10/22 13:32
@Author  : ZhangShenao
@File    : agent.py
@Desc    : 主Agent
"""

from langgraph.graph import START, StateGraph
from langgraph.graph.state import CompiledStateGraph
from langgraph.graph.message import MessagesState
from llm_node import llm_node
from tool_node import tool_node
from human_node import human_node
from conditional_node import conditional_node
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import SystemMessage, HumanMessage
import sys
import io
from langgraph.types import Command
import asyncio


SYSTEM_PROMPT = """
你是一个电商后台管理员，根据用户的要求回答相关的商品价格和库存信息。
如果有需要，可以调用ask_human工具，进一步向人类提问。
"""


async def build_agent() -> CompiledStateGraph:
    """
    构建Agent
    """

    # 构造Graph图
    graph = StateGraph(MessagesState)

    # 添加Node节点
    graph.add_node("llm_node", llm_node)
    graph.add_node("human_node", human_node)
    graph.add_node("tool_node", tool_node)

    # 添加Edge边
    graph.add_edge(START, "llm_node")
    graph.add_conditional_edges(source="llm_node", path=conditional_node)
    graph.add_edge("tool_node", "llm_node")
    graph.add_edge("human_node", "llm_node")

    # 开启Checkpoint机制，保存Agent的运行状态
    # 因为Human-In-The-Loop需要中断等待人类回复，之后再恢复执行，因此需要保存状态
    # 默认采用MemorySaver内存机制
    memory = MemorySaver()

    # 编译Graph图并返回
    return graph.compile(checkpointer=memory)


async def run_agent(user_query: str) -> str:
    """
    运行Agent
    """

    # 构建Agent
    agent = await build_agent()

    # 初始化状态
    messages = [SystemMessage(content=SYSTEM_PROMPT), HumanMessage(content=user_query)]
    init_state = MessagesState(messages=messages)

    # Checkpoint机制需要传入Config配置
    config = {"configurable": {"thread_id": "1"}}

    # 运行Agent
    result = await agent.ainvoke(input=init_state, config=config)

    # 中断时，等待人类输入
    tools_calls = result["messages"][-1].tool_calls
    if len(tools_calls) > 0 and tools_calls[0]["name"] == "ask_human":
        # 接收用户输入,并将其作为resume参数,通过Command对象恢复agent的运行
        sys.stdin = io.TextIOWrapper(sys.stdin.buffer, encoding="utf-8")
        user_input = input("请输入你的回答：")
        result = await agent.ainvoke(Command(resume=user_input), config=config)

    # 返回最终结果
    return result["messages"][-1].content


if __name__ == "__main__":
    result = asyncio.run(run_agent(user_query="帮我查下商品的实际价格"))
    print("Agent运行结果:")
    print(result)
