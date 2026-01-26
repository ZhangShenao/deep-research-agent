# -*- coding: utf-8 -*-
"""
@Time    : 2026/01/26
@Author  : ZhangShenao
@File    : parser.py
@Desc    : 解析器
"""

import json
from typing import Dict


def extract_markdown_block(response: str, block_type: str = "json") -> str:
    """
    从LLM响应中提取指定类型的代码块内容，默认为json类型

    参数:
        response: LLM的原始响应文本
        block_type: 要提取的代码块类型，默认为"json"

    返回:
        提取出的代码块内容
    """
    # 检查响应中是否包含代码块标记
    if not "```" in response:
        return response

    # 分割响应并提取第一个代码块
    code_block = response.split("```")[1].strip()

    # 如果代码块以指定类型开头，则移除类型标识
    if code_block.startswith(block_type):
        code_block = code_block[len(block_type) :].strip()

    return code_block


def parse_action(response: str) -> Dict:
    """
    解析LLM响应，提取结构化的工具调用指令

    参数:
        response: LLM的响应文本

    返回:
        包含工具名称和参数的字典
    """
    try:
        # 从响应中提取action代码块
        response = extract_markdown_block(response, "action")

        # 将JSON字符串解析为Python字典
        response_json = json.loads(response)

        # 验证响应格式是否正确
        if "tool_name" in response_json and "args" in response_json:
            return response_json

        # 格式不正确，返回错误信息，便于LLM进行错误纠正
        return {
            "tool_name": "error",
            "args": {"message": "解析工具调用信息失败，请按照指定格式重新生成。"},
        }
    except json.JSONDecodeError:
        # 如果JSON解析失败，返回错误信息
        return {
            "tool_name": "error",
            "args": {"message": "解析工具调用信息失败，请按照指定格式重新生成。"},
        }
