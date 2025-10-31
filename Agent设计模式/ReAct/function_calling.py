# -*- coding: utf-8 -*-
"""
@Time    : 2025/9/26 20:08
@Author  : ZhangShenao
@File    : tools.py
@Desc    : 基于function calling实现ReAct模式

ReAct模式:
Thought -> Action -> Action Input -> Pause -> Observation 的循环

Function Calling是大模型预训练的产物,并不是所有大模型都支持Function Calling。
"""


# 第三方库导入
from llm import DEEPSEEK_CLIENT
from tools import tools
from openai.types.chat.chat_completion_message_param import ChatCompletionMessageParam
from typing import Iterable
from openai.types.chat.chat_completion import ChatCompletion
from tools import tool_dict
import json


def send_message(messages: Iterable[ChatCompletionMessageParam]) -> ChatCompletion:
    """
    发送消息
    """

    resp = DEEPSEEK_CLIENT.chat.completions.create(
        model="deepseek-chat",  # 使用deepseek-chat模型
        messages=messages,  # 传入消息列表
        tools=tools,  # 传入工具列表
        tool_choice="auto",  # 让模型自行决策工具调用
        temperature=0.1,  # 设置较小的temperature,鼓励模型生成确定性结果
    )
    return resp


if __name__ == "__main__":
    # 初始化消息列表
    messages = [
        {
            "role": "system",
            "content": "你是一位专业的助手，请根据用户的问题提供帮助。如果需要，可以调用工具。",
        },
        {"role": "user", "content": "我想买2斤苹果和3斤香蕉，一共需要多少钱？"},
    ]

    # 循环发送消息
    while True:
        resp = send_message(messages)
        # 保持对话历史
        print(f"AI回复: {resp.choices[0].message.content}")
        messages.append(resp.choices[0].message)

        # 如果模型没有进行工具调用,则直接返回结果
        if resp.choices[0].message.tool_calls is None:
            break

        # 如果模型进行了工具调用,则解析工具调用参数
        for tool_call in resp.choices[0].message.tool_calls:
            name = tool_call.function.name
            tool = tool_dict[name]
            if tool is not None:
                args = json.loads(tool_call.function.arguments)
                result = tool(**args)
                print(f"调用工具: {name}, 参数: {args}, 结果: {result}")
                messages.append(
                    {
                        "role": "tool",  # 添加工具消息
                        "content": result,
                        "tool_call_id": tool_call.id,  # 保持工具调用id,用于上下文关联
                    }
                )
