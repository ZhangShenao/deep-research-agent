# -*- coding: utf-8 -*-
"""
@Time    : 2026/01/26
@Author  : ZhangShenao
@File    : llm.py
@Desc    : LLM
"""

import os

from dotenv import load_dotenv
from zai import ZhipuAiClient
from typing import List, Dict
from tool.tools import TOOL_DEFINITION
from zai.api_resource.chat.completions import (
    Completion,
    StreamResponse,
    ChatCompletionChunk,
)

# 加载环境变量
load_dotenv()

# 创建智谱AI客户端
ZHIPU_CLIENT = ZhipuAiClient(api_key=os.getenv("ZHIPU_API_KEY"))


def generate_response(messages: List[Dict]) -> str:
    """
    调用智谱AI客户端生成响应

    Args:
        messages: 消息列表

    Returns:
        response: 响应
    """

    # 调用智谱AI客户端生成响应
    response = ZHIPU_CLIENT.chat.completions.create(
        model="glm-4.7",  # 使用智谱GLM-4.7模型
        messages=messages,  # 传入消息列表
        thinking={
            "type": "false",  # 禁用深度思考模式
        },
    )

    # 返回响应内容
    return response.choices[0].message.content


def generate_response_with_tools(
    messages: List[Dict],
) -> Completion | StreamResponse[ChatCompletionChunk]:
    """
    调用智谱AI客户端生成响应，支持工具调用

    Args:
        messages: 消息列表

    Returns:
        response: 响应,支持工具调用
    """

    # 调用智谱AI客户端生成响应
    return ZHIPU_CLIENT.chat.completions.create(
        model="glm-4.7",  # 使用智谱GLM-4.7模型
        messages=messages,  # 传入消息列表
        thinking={
            "type": "false",  # 禁用深度思考模式
        },
        tools=TOOL_DEFINITION,  # 传入工具定义
        tool_choice="auto",  # 让模型自行决策工具调用
    )
