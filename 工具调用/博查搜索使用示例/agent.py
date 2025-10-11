# -*- coding: utf-8 -*-
"""
@Time    : 2025/10/11 16:23
@Author  : ZhangShenao
@File    : agent.py
@Desc    : 主Agent

本质上也是一种RAG技术
使用Web Search API进行网络搜索,并根据检索结果,构造Prompt,调用LLM,获取最终回答。
RAG的上下文即网络搜索结果
"""

from web_search import web_search
from llm import DEEPSEEK_CLIENT
import asyncio

# 定义System Prompt
SYSTEM_PROMPT = """
你是一个股票专家，请根据上下文回答用户的问题。

#上下文：
{context}

# 用户的问题是：
{query}
"""


async def run(query: str):
    """异步执行函数Agent"""

    # 执行网络检索
    web_search_result = await web_search(query=query)
    print("##网络搜索结果:\n", web_search_result)

    # 根据检索结果,填充上下文,构造Prompt
    prompt = SYSTEM_PROMPT.format(context=web_search_result, query=query)

    # 调用LLM,获取最终回答
    response = DEEPSEEK_CLIENT.chat.completions.create(
        model="deepseek-chat",
        messages=[{"role": "user", "content": prompt}],
    )

    return response.choices[0].message.content


if __name__ == "__main__":
    result = asyncio.run(run("美股大跌原因？"))
    print(result)
