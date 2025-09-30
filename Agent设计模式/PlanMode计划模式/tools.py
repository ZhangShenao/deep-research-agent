# -*- coding: utf-8 -*-
"""
@Time    : 2025/9/29 13:32
@Author  : ZhangShenao
@File    : tools.py
@Desc    : 工具定义
"""

from langchain.tools import tool


@tool
def get_fruit_price(fruit_name: str) -> str:
    """
    获取水果价格
    """

    if fruit_name == "苹果":
        return "苹果价格为5.21元/斤"
    if fruit_name == "香蕉":
        return "香蕉价格为3.18元/斤"

    return "没有找到该水果的价格"


@tool
def calculate(expression: str) -> str:
    """
    计算表达式
    """
    return str(eval(expression))


# 定义工具列表
TOOLS = [get_fruit_price, calculate]

# 工具字典
TOOL_DICT = {tool.name: tool for tool in TOOLS}
