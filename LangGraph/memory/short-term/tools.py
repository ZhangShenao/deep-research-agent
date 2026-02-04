# -*- coding: utf-8 -*-
"""
@Time    : 2026/02/04
@Author  : ZhangShenao
@File    : tools.py
@Desc    : 工具定义
"""


def add(a: int, b: int) -> int:
    """将 a 与 b 相加。

    参数:
        a: 第一个整数
        b: 第二个整数
    """
    return a + b


def subtract(a: int, b: int) -> int:
    """将 a 与 b 相减。

    参数:
        a: 第一个整数
        b: 第二个整数
    """
    return a - b


def multiply(a: int, b: int) -> int:
    """将 a 与 b 相乘。

    参数:
        a: 第一个整数
        b: 第二个整数
    """
    return a * b


def divide(a: int, b: int) -> float:
    """将 a 与 b 相除。

    参数:
        a: 第一个整数
        b: 第二个整数
    """
    return a / b


# 将工具列表绑定到模型实例上，使模型能够调用它们
tools = [add, subtract, multiply, divide]
