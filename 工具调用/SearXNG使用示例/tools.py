# -*- coding: utf-8 -*-
"""
@Time    : 2025/10/28 14:00
@Author  : ZhangShenao
@File    : tools.py
@Desc    : 工具定义
"""

from langchain_core.tools import tool
from langchain_community.utilities import SearxSearchWrapper


# 结果模板
RESULT_TEMPLATE = """
    标题: {title}
    简介: {snippet}
    链接: {link}

    """


@tool
async def web_search(keyword: str) -> str:
    """
    根据关键词在互联网上搜索，并返回搜索结果
    """

    print(f"搜索关键词: {keyword}")

    # 使用LangChain封装好的SearxSearchWrapper
    searxng = SearxSearchWrapper(
        searx_host="http://localhost:18080",  # 设置SearXNG的地址
    )

    # 设置搜索引擎
    engines = ["baidu", "sogou", "quark"]

    # 执行搜索
    search_result = searxng.results(query=keyword, num_results=5, engines=engines)

    # 解析结果
    results = []
    for r in search_result:
        title = r.get("title", "暂无标题")
        snippet = r.get("snippet", "赞无简介")
        link = r.get("link", "暂无链接")

        results.append(RESULT_TEMPLATE.format(title=title, snippet=snippet, link=link))
    return results


TOOLS = [web_search]

TOOL_DICT = {tool.name: tool for tool in TOOLS}
