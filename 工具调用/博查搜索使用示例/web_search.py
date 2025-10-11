# -*- coding: utf-8 -*-
"""
@Time    : 2025/10/11 16:23
@Author  : ZhangShenao
@File    : web_search.py
@Desc    : 使用博查搜索API进行网络搜索
"""

import json
import os

import requests
from dotenv import load_dotenv
from langchain_core.tools import tool

# 加载环境变量
load_dotenv()

# 检索结果模板
SEARCH_RESULT_TEMPLATE = """
标题:{}
简介:{}
链接:{}

"""


# @tool
async def web_search(query: str, page: int = 1, page_size: int = 5) -> str:
    """
    根据关键词在网络上搜索,并返回搜索结果

    这是一个异步工具函数,用于调用博查搜索API进行网络搜索。
    它会自动处理API调用、结果解析和格式化,返回包含标题、简介和链接的搜索结果。

    Args:
        query (str): 搜索关键词或问题,例如"美股暴跌的原因"
        page (int, optional): 页码,从1开始。默认为1
        page_size (int, optional): 每页返回的结果数量。默认为5

    Returns:
        str: 格式化的搜索结果字符串,包含每个结果的标题、简介和链接

    Raises:
        Exception: 当API调用失败或返回格式错误时抛出异常

    Example:
        >>> result = await web_search("人工智能最新进展", page=1, page_size=3)
        >>> print(result)
    """

    # 检索内容
    search_result = await bocha_search(query, page, page_size)

    # 解析检索结果
    result = await parse_search_result(search_result)
    return result


async def bocha_search(query: str, page: int = 1, page_size: int = 5) -> dict:
    """
    调用博查搜索API进行网络搜索

    这是一个底层函数,负责直接与博查AI的搜索API进行交互。
    它发送POST请求到博查API,并返回原始的JSON响应结果。

    Args:
        query (str): 搜索查询字符串
        page (int, optional): 请求的页码,从1开始。默认为1
        page_size (int, optional): 每页返回的搜索结果数量。默认为5

    Returns:
        dict: 博查API返回的JSON响应,包含搜索结果的完整数据
              如果请求失败,返回包含error键的字典

    Note:
        - 需要在环境变量中设置BOCHA_API_KEY
        - API会自动生成搜索结果摘要(summary=True)

    Example:
        >>> result = await bocha_search("机器学习", page=1, page_size=3)
        >>> print(result['data']['webPages']['value'])
    """

    url = "https://api.bochaai.com/v1/web-search"
    headers = {
        "Authorization": f"Bearer {os.environ.get("BOCHA_API_KEY")}",
        "Content-Type": "application/json",
    }
    data = {"query": query, "summary": True, "count": page_size, "page": page}
    response = requests.post(url, data=json.dumps(data), headers=headers)
    try:
        return response.json()
    except Exception as e:
        return {"error": str(e)}


async def parse_search_result(search_result: dict) -> str:
    """
    解析搜索结果,将其格式化为易读的字符串

    从博查API返回的JSON响应中提取关键信息(标题、摘要、链接),
    并使用预定义的模板将其格式化为用户友好的字符串格式。

    Args:
        search_result (dict): 博查API返回的原始JSON响应字典
                             必须包含data.webPages.value路径的数据结构

    Returns:
        str: 格式化后的搜索结果字符串,每个结果包含标题、简介和链接
             多个结果之间用换行符分隔

    Raises:
        KeyError: 当search_result的数据结构不符合预期时抛出

    Example:
        >>> search_result = {"data": {"webPages": {"value": [...]}}}
        >>> formatted = await parse_search_result(search_result)
        >>> print(formatted)
        标题:示例标题
        简介:示例简介
        链接:https://example.com
    """

    data = search_result["data"]
    pages = data["webPages"]["value"]

    # 遍历检索到的网页,拼接成字符串
    result = ""
    for page in pages:
        result += SEARCH_RESULT_TEMPLATE.format(
            page["name"], page["summary"], page["url"]
        )
    return result
