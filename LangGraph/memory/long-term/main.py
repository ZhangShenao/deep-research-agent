# -*- coding: utf-8 -*-
"""
@Time    : 2025/11/07 14:00
@Author  : ZhangShenao
@File    : main.py
@Desc    : 主程序
"""

from agent import build_agent, run_conversation
from langgraph.graph.state import CompiledStateGraph

# 设置Mem0用户ID
MEM0_USER_ID = "zsa"

if __name__ == "__main__":
    # 构建Agent
    agent: CompiledStateGraph = build_agent()

    # 运行对话
    print("欢迎使用智能助手! 有什么可以帮您的吗?")
    while True:
        user_input = input("You: ")
        if user_input.lower() in ["quit", "exit", "bye"]:
            print("智能助手: 感谢您的使用，祝您有个美好的一天!")
            break
        run_conversation(agent, user_input, MEM0_USER_ID)
