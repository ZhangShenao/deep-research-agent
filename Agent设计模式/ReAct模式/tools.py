# -*- coding: utf-8 -*-
"""
@Time    : 2025/9/26 20:08
@Author  : ZhangShenao
@File    : tools.py
@Desc    : 工具定义
"""


def get_fruit_price(fruit_name: str) -> str:
    """
    获取水果价格
    """

    if fruit_name == "苹果":
        return "苹果价格为5.21元/斤"
    if fruit_name == "香蕉":
        return "香蕉价格为3.18元/斤"

    return "没有找到该水果的价格"


def calculate(expression: str) -> str:
    """
    计算表达式
    """
    return str(eval(expression))


# 定义工具列表
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_fruit_price",
            "description": "使用该工具可以查询指定水果的价格",
            "parameters": {
                "type": "object",
                "properties": {
                    "fruit_name": {
                        "type": "string",
                        "description": "水果名称",
                    }
                },
                "required": ["fruit_name"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "calculate",
            "description": "使用该工具可以计算表达式",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "表达式",
                    }
                },
                "required": ["expression"],
            },
        },
    },
]

# 工具字典
tool_dict = {
    "get_fruit_price": get_fruit_price,
    "calculate": calculate,
}
