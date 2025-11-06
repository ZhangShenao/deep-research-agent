# -*- coding: utf-8 -*-
"""
@Time    : 2025/10/22 13:32
@Author  : ZhangShenao
@File    : llm.py
@Desc    : LLM大模型
"""

import os

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from tools import TOOLS


# 加载环境变量
load_dotenv()


# 创建DeepSeek Reasoner模型
LLM = ChatOpenAI(
    model="deepseek-reasoner",
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url=os.getenv("DEEPSEEK_BASE_URL"),
)

# 将模型绑定好工具
LLM_WITH_TOOLS = LLM.bind_tools(TOOLS)
