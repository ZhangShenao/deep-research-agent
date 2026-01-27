# -*- coding: utf-8 -*-
"""
@Time    : 2026/01/26
@Author  : ZhangShenao
@File    : agent_loop_based_on_function_calling.py
@Desc    : 基于Function Calling驱动的Agent Loop
"""

import json

from llm.llm import generate_response_with_tools
from tool.tools import TOOL_DICT

# 定义System Prompt
# 相较于Prompt Engineering驱动而言，Function Calling驱动的Agent Loop的System Prompt更加简洁
# 不需要在System Prompt中定义工具列表和工具的参数说明
SYSTEM_PROMPT = """
你是一个AI智能体，可以使用可用工具来执行任务。
如果用户询问关于文件、文档或内容的问题，请先列出文件再读取它们。
当你完成任务后，使用 `terminate` 工具终止对话，我将向用户提供结果。
"""

# 定义Agent的最大迭代次数，避免出现无限循环
MAX_ITERATIONS = 10


def execute_tool(tool_name: str, tool_args: dict) -> dict:
    """
    执行指定的工具函数

    Args:
        tool_name: 工具名称
        tool_args: 工具参数

    Returns:
        包含执行结果或错误信息的字典
    """
    if tool_name in TOOL_DICT:
        try:
            result = {"result": TOOL_DICT[tool_name](**tool_args)}
        except Exception as e:
            result = {"error": f"Error executing {tool_name}: {str(e)}"}
    else:
        result = {"error": f"Unknown tool: {tool_name}"}
    return result


def update_memory(memory: list, tool_name: str, tool_args: dict, result: dict) -> None:
    """
    更新对话记忆，添加工具调用和执行结果

    Args:
        memory: 对话记忆列表
        tool_name: 工具名称
        tool_args: 工具参数
        result: 执行结果
    """
    action = {"tool_name": tool_name, "args": tool_args}
    memory.extend(
        [
            {"role": "assistant", "content": json.dumps(action)},
            {"role": "tool", "content": json.dumps(result)},
        ]
    )


def run_agent_loop(memory: list) -> None:
    """
    执行Agent循环，处理工具调用和响应

    Args:
        memory: 对话记忆列表
    """
    iteration = 0

    while iteration < MAX_ITERATIONS:
        print(f"【Round {iteration + 1}】Agent 正在思考")

        response = generate_response_with_tools(messages=memory)
        print(f"【Round {iteration + 1}】Agent 执行结果: {response}")

        if response.choices[0].message.tool_calls:
            tool = response.choices[0].message.tool_calls[0]
            tool_name = tool.function.name
            tool_args = json.loads(tool.function.arguments)

            if tool_name == "terminate":
                print(f"Termination message: {tool_args['message']}")
                break

            result = execute_tool(tool_name, tool_args)
            print(f"Executing: {tool_name} with args {tool_args}")
            print(f"Result: {result}")

            update_memory(memory, tool_name, tool_args, result)
            iteration += 1
        else:
            result = response.choices[0].message.content
            print(f"Response: {result}")
            break


if __name__ == "__main__":
    user_task = input("请输入您想让我执行的任务：")

    memory = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_task},
    ]

    run_agent_loop(memory)
