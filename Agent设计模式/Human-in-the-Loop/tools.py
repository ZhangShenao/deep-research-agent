# -*- coding: utf-8 -*-
"""
@Time    : 2025/10/22 13:32
@Author  : ZhangShenao
@File    : tools.py
@Desc    : 工具定义
"""

from langchain_core.tools import tool
import random


@tool
def get_product_price(product_name: str) -> str:
    """
    获取商品价格
    """

    price = random.randint(10, 100)
    return f"商品 {product_name} 的价格为 {price:.2f} 元"


@tool
def ask_human(question: str) -> None:
    """
    向人类进一步提问，确认详细信息
    """

    print(f"向人类提问: {question}")
    pass


# 工具列表
TOOLS = [
    get_product_price,
    ask_human,
]

# 工具字典
TOOL_DICT = {tool.name: tool for tool in TOOLS}
