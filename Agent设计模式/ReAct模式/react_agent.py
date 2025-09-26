# -*- coding: utf-8 -*-
"""
@Time    : 2025/9/26 20:08
@Author  : ZhangShenao
@File    : react.py
@Desc    : 基于Prompt实现ReAct Agent

ReAct模式:
Thought -> Action -> Action Input -> Pause -> Observation 的循环

Function Calling是大模型预训练的产物,并不是所有大模型都支持Function Calling。
对于不支持Function Calling的大模型,可以使用Prompt实现ReAct模式。
"""

# 第三方库导入
from llm import DEEPSEEK_CLIENT
from openai.types.chat.chat_completion_message_param import ChatCompletionMessageParam
from typing import Iterable
from openai.types.chat.chat_completion import ChatCompletion
from prompt import REACT_PROMPT
from tools import tools
import re
import json
from tools import tool_dict


def send_message(messages: Iterable[ChatCompletionMessageParam]) -> ChatCompletion:
    """
    发送消息
    """

    resp = DEEPSEEK_CLIENT.chat.completions.create(
        model="deepseek-chat",  # 使用deepseek-chat模型
        messages=messages,  # 传入消息列表
        temperature=0.1,  # 设置较小的temperature,鼓励模型生成确定性结果
    )
    return resp


if __name__ == "__main__":
    # 替换ReAct Prompt Template
    react_prompt = REACT_PROMPT.replace("{tools}", json.dumps(tools))

    # 构造消息列表
    messages = [
        {
            "role": "system",
            "content": react_prompt,
        },
        {"role": "user", "content": "我想买2斤苹果和3斤香蕉，一共需要多少钱？"},
    ]

    # 循环发送消息
    while True:
        resp = send_message(messages)
        resp_text = resp.choices[0].message.content
        print(f"{resp.choices[0].message.content}")

        # 保持对话历史
        messages.append(resp.choices[0].message)

        # 使用正则匹配的方式,解析最终结果
        final_answer_match = re.search(r"Final Answer:\s*(.*)", resp_text)
        if final_answer_match is not None:
            # 生成了最终答案,直接返回
            # final_answer = final_answer_match.group(1)
            # print("Final Answer: ", final_answer)
            break

        # 使用正则表达式,匹配工具调用信息
        action_match = re.search(r"Action:\s*(\w+)", resp_text)
        action_input_match = re.search(
            r'Action Input:\s*({.*?}|".*?")', resp_text, re.DOTALL
        )

        if action_match and action_input_match:
            # 解析工具及调用参数
            tool_name = action_match.group(1)
            args = json.loads(action_input_match.group(1))

            # 调用工具,作为Observation,添加到对话历史中
            observation = ""
            tool = tool_dict[tool_name]
            if tool is not None:
                observation = tool(**args)
            print(f"Observation: {observation}")
            messages.append({"role": "user", "content": f"Observation: {observation}"})
