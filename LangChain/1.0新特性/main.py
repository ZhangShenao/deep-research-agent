# -*- coding: utf-8 -*-
"""
@Time    : 2025/11/14 14:00
@Author  : ZhangShenao
@File    : main.py
@Desc    : 主程序
"""

from agent import create_smart_agent
from state import UserContext
import dotenv

if __name__ == "__main__":

    # 加载环境变量
    dotenv.load_dotenv()

    # 创建 Agent
    agent = create_smart_agent()

    USER_ID = "0001"

    # 配置上下文
    config = {"configurable": {"thread_id": USER_ID}}
    context = UserContext(user_id=USER_ID, user_name="zsa")

    # 获取用户信息
    print("【获取用户信息】")
    print("-" * 100)
    result = agent.invoke(
        {"messages": [{"role": "user", "content": "请告诉我我的用户信息"}]},
        config=config,
        context=context,
    )
    print(result["messages"][-1].content)
    print("-" * 100)

    # 保存事实记忆
    print("【保存事实记忆】")
    print("-" * 100)
    result = agent.invoke(
        {"messages": [{"role": "user", "content": "请记住：我喜欢喝咖啡"}]},
        config=config,
        context=context,
    )
    print(result["messages"][-1].content)
    print("-" * 100)

    # 记忆召回
    print("【记忆召回】")
    print("-" * 100)
    result = agent.invoke(
        {"messages": [{"role": "user", "content": "我之前告诉过你我喜欢什么？"}]},
        config=config,
        context=context,
    )
    print(result["messages"][-1].content)
    print("-" * 100)
