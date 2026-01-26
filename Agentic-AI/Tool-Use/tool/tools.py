# -*- coding: utf-8 -*-
"""
@Time    : 2026/01/26
@Author  : ZhangShenao
@File    : tools.py
@Desc    : 工具定义
"""

import os
from typing import List


def list_files() -> List[str]:
    """
    列出当前目录中的所有文件

    返回:
        文件名列表
    """
    return os.listdir(".")


def read_file(file_name: str) -> str:
    """
    读取指定文件的内容

    参数:
        file_name: 要读取的文件名

    返回:
        文件内容或错误信息
    """
    try:
        with open(file_name, "r") as file:
            return file.read()
    except FileNotFoundError:
        return f"Error: {file_name} not found."
    except Exception as e:
        return f"Error: {str(e)}"


def terminate(message: str) -> None:
    """
    终止智能体循环并显示总结消息

    参数:
        message (str): 要显示给用户的终止消息
    """
    print(f"终止消息: {message}")


# 工具列表
TOOLS = [list_files, read_file, terminate]

# 工具字典
TOOL_DICT = {
    "list_files": list_files,
    "read_file": read_file,
    "terminate": terminate,
}

# 工具的Schema定义
# LLM会读取该Schema，来决策进行工具调用
TOOL_DEFINITION = [
    {
        "type": "function",  # 工具类型：函数调用
        "function": {
            "name": "list_files",  # 工具名称
            "description": "Returns a list of files in the directory.",  # 工具描述
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },  # 参数配置（此工具无需参数）
        },
    },
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Reads the content of a specified file in the directory.",
            "parameters": {
                "type": "object",
                "properties": {"file_name": {"type": "string"}},  # 定义参数类型
                "required": ["file_name"],  # 必需参数列表
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "terminate",
            "description": "Terminates the conversation. No further actions or interactions are possible after this. Prints the provided message for the user.",
            "parameters": {
                "type": "object",
                "properties": {
                    "message": {"type": "string"},  # 终止消息参数
                },
                "required": ["message"],  # 消息参数是必需的
            },
        },
    },
]
