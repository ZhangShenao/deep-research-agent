# -*- coding: utf-8 -*-
"""
@Time    : 2025/11/13 14:00
@Author  : ZhangShenao
@File    : tools.py
@Desc    : 工具定义
"""

from langgraph.store.memory import InMemoryStore
from langchain.tools import tool, ToolRuntime
from state import UserContext, CustomAgentState
from langgraph.types import Command
from langchain.messages import ToolMessage
from datetime import datetime
import random

# 创建长期记忆存储
STORE = InMemoryStore()


@tool
def get_user_info(runtime: ToolRuntime[UserContext, CustomAgentState]) -> str:
    """从长期记忆中获取用户信息。如果用户信息不存在，会从上下文中初始化用户信息"""
    user_id = runtime.context.user_id
    user_info = STORE.get(("users",), user_id)

    if user_info:
        info = user_info.value
        return f"用户信息：姓名={info.get('name')}, 语言={info.get('language')}, 主题={info.get('theme', '未设置')}"
    else:
        # 如果用户信息不存在，从上下文中初始化
        initial_info = {
            "name": runtime.context.user_name or f"用户{user_id}",
            "language": "zh-CN",
            "theme": "default",
        }
        STORE.put(("users",), user_id, initial_info)
        return f"用户信息已初始化：姓名={initial_info['name']}, 语言={initial_info['language']}, 主题={initial_info['theme']}"


@tool
def update_user_preferences(
    language: str, theme: str, runtime: ToolRuntime[UserContext, CustomAgentState]
) -> Command:
    """更新用户偏好设置。如果用户信息不存在，会先创建用户信息"""
    user_id = runtime.context.user_id

    # 更新长期记忆
    user_info = STORE.get(("users",), user_id)
    if user_info:
        updated_info = user_info.value.copy()
        updated_info["language"] = language
        updated_info["theme"] = theme
        STORE.put(("users",), user_id, updated_info)
    else:
        # 如果用户信息不存在，创建新用户信息
        new_info = {
            "name": runtime.context.user_name or f"用户{user_id}",
            "language": language,
            "theme": theme,
        }
        STORE.put(("users",), user_id, new_info)

    # 更新短期状态
    return Command(
        update={
            "user_preferences": {
                "language": language,
                "theme": theme,
                "timezone": runtime.state.get("user_preferences", {}).get(
                    "timezone", "Asia/Shanghai"
                ),
            },
            "messages": [
                ToolMessage(
                    f"已更新用户偏好：语言={language}, 主题={theme}",
                    tool_call_id=runtime.tool_call_id,
                )
            ],
        }
    )


@tool
def remember_fact(
    fact: str, category: str, runtime: ToolRuntime[UserContext, CustomAgentState]
) -> Command:
    """记住一个事实到长期记忆"""
    user_id = runtime.context.user_id
    memory_key = f"memory_{user_id}"

    memories = STORE.get(("memories",), memory_key)
    if memories:
        memory_list = memories.value.get("facts", [])
    else:
        memory_list = []

    memory_list.append(
        {"fact": fact, "category": category, "timestamp": datetime.now().isoformat()}
    )

    STORE.put(("memories",), memory_key, {"facts": memory_list})

    return Command(
        update={
            "messages": [
                ToolMessage(
                    f"已记住：{fact}（类别：{category}）",
                    tool_call_id=runtime.tool_call_id,
                )
            ]
        }
    )


@tool
def get_weather(city: str) -> str:
    """获取指定城市的天气信息"""
    temperature = random.randint(10, 30)
    return f"{city}的当前气温是{temperature:.2f}摄氏度"


@tool
def calculate(expression: str) -> str:
    """计算表达式"""
    return f"计算结果为: {eval(expression)}"


@tool
def recall_facts(
    category: str, runtime: ToolRuntime[UserContext, CustomAgentState]
) -> str:
    """从长期记忆中召回事实。可以指定类别来过滤，如果类别为空字符串则返回所有事实"""
    user_id = runtime.context.user_id
    memory_key = f"memory_{user_id}"

    memories = STORE.get(("memories",), memory_key)
    if not memories:
        return "未找到任何记忆的事实"

    facts = memories.value.get("facts", [])
    if not facts:
        return "未找到任何记忆的事实"

    # 如果指定了类别（非空），则过滤
    if category and category.strip():
        filtered_facts = [f for f in facts if f.get("category") == category]
        if not filtered_facts:
            return f"未找到类别为 '{category}' 的事实"
        facts = filtered_facts

    # 格式化返回结果
    result_lines = [f"找到 {len(facts)} 条事实："]
    for i, fact_item in enumerate(facts, 1):
        fact_text = fact_item.get("fact", "")
        fact_category = fact_item.get("category", "")
        fact_timestamp = fact_item.get("timestamp", "")
        result_lines.append(
            f"{i}. {fact_text}（类别：{fact_category}，时间：{fact_timestamp}）"
        )

    return "\n".join(result_lines)
