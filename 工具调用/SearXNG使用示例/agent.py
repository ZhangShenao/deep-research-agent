# -*- coding: utf-8 -*-
"""
@Time    : 2025/10/28 14:00
@Author  : ZhangShenao
@File    : agent.py
@Desc    : Agent
"""

from llm import DEEPSEEK
from tools import TOOLS
from prompt import SYSTEM_PROMPT
from langgraph.prebuilt import create_react_agent
import asyncio


async def run(query: str) -> str:
    """
    运行Agent
    """

    # 使用LangGraph预构建ReAct Agent
    agent = create_react_agent(
        model=DEEPSEEK,  # 指定模型
        tools=TOOLS,  # 指定工具
    )

    # 构造消息列表
    messages = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT,
        },
        {"role": "user", "content": query},
    ]

    # 运行Agent
    response = await agent.ainvoke({"messages": messages})

    # 返回最终结果
    return response["messages"][-1].content


if __name__ == "__main__":
    query = "中芯国际是在哪个交易所上市的？最新股价是多少？有哪些利好和利空的新闻？帮我总结一下，并给出投资建议。"
    response = asyncio.run(run(query=query))
    print(response)
