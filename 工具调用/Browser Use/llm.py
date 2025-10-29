# -*- coding: utf-8 -*-
"""
@Time    : 2025/10/29 20:11
@Author  : ZhangShenao
@File    : llm.py
@Desc    : LLM大模型
"""

import os

from dotenv import load_dotenv
from browser_use.llm import ChatDeepSeek

# 加载环境变量
load_dotenv()


# 创建DeepSeek模型
DEEPSEEK = ChatDeepSeek(
    model="deepseek-chat",
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url=os.getenv("DEEPSEEK_BASE_URL"),
)
